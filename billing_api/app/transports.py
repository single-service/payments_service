import aiohttp
import asyncio
import backoff
import logging
import ujson

from aiohttp import ClientOSError
from decimal import Decimal
from json import dumps
from typing import Optional
from uuid import uuid4

from app.settings import settings

logger = logging.getLogger("info")


def backoff_handler(details):
    logger.info(
        'Backing off {wait:0.1f} seconds afters {tries} tries request method '
        'with args {args} and kwargs {kwargs}'.format(**details),
    )


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f'Wrong object type. Expected Decimal, got {type(obj)}')


def decimal_safe_json_dumps(json):
    return dumps(json, default=decimal_default)


class BaseTransportError(Exception):
    def __init__(self, response, status):
        self.response = response
        self.status = status

    def __str__(self):
        return str(self.response)


class NotFoundError(BaseTransportError):
    """Error for matching 404 error."""

    pass


class ClientError(BaseTransportError):
    pass


class Transport:
    async def request(  # noqa: CFQ002
        self,
        method: str,
        url: str,
        headers: dict = None,
        data: Optional[str] = None,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        auth: Optional[tuple] = (),
            **kwargs,
    ) -> dict:
        pass

    async def startup(self):
        pass

    async def shutdown(self):
        pass


class AiohttpSessionTransport(Transport):
    def __init__(self):
        self.trace_config = None
        self.session = None

    async def startup(self):
        self.trace_config = aiohttp.TraceConfig()
        self.trace_config.on_request_start.append(self.on_request_start)
        self.trace_config.on_request_exception.append(self.on_request_exception)
        self.trace_config.on_request_end.append(self.on_request_end)
        self.session = aiohttp.ClientSession(
            trace_configs=[self.trace_config],
            json_serialize=decimal_safe_json_dumps,
        )

    @backoff.on_exception(
        backoff.expo, max_tries=settings.MAX_RETRIES,
        max_time=settings.RETRY_MAX_TIME,
        giveup=lambda e: e.status < 500,
        on_backoff=backoff_handler,
        exception=ClientError,
    )
    async def request(  # noqa: CFQ002
        self,
        method: str,
        url: str,
        headers: dict = None,
        data: Optional[str] = None,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        auth: Optional[tuple] = (),
        **kwargs,
    ) -> dict:
        basic_auth = aiohttp.BasicAuth(*auth) if auth else None

        trace_request_ctx = {
            'method': method,
            'url': url,
            'body': json or data,
            'headers': headers,
            'params': params,
        }

        try:
            async with self.session.request(
                method,
                url,
                headers=headers or {},
                data=data or None,
                json=json or None,
                params=params,
                auth=basic_auth,
                trace_request_ctx=trace_request_ctx,
                **kwargs,
            ) as response:
                data = await response.text()

                try:
                    data = ujson.loads(data)
                except ValueError:  # может быть текст ошибки - а это не json
                    pass

                try:
                    response.raise_for_status()  # здесь закрывается коннект, при ошибке, после уже не прочитать тело
                except aiohttp.ClientResponseError as e:
                    if e.status == 404:
                        raise NotFoundError(response=data, status=e.status)

                    raise ClientError(response=data, status=e.status)

                return data
        except ClientOSError as e:
            raise ClientError(response=str(e), status=500)

    async def shutdown(self):
        return self.session.close()

    @staticmethod
    async def on_request_start(session, trace_config_ctx, params):
        uuid = str(uuid4())
        request_data = trace_config_ctx.trace_request_ctx or {}
        request_data['uuid'] = uuid
        logger.debug('Server make request', extra={'request': request_data})

        trace_config_ctx.uuid = uuid
        trace_config_ctx.start = asyncio.get_event_loop().time()

    @staticmethod
    async def on_request_exception(session, trace_config_ctx, params):
        exc = params.exception
        logger.exception(
            f'Server got request error: {exc.__class__.__name__}: {exc}',
            extra={'request': trace_config_ctx.trace_request_ctx},
        )

    @staticmethod
    async def on_request_end(session, trace_config_ctx, params):
        elapsed = asyncio.get_event_loop().time() - trace_config_ctx.start
        response_data = {
            'code': params.response.status,
            'url': str(params.response.url),
            'body': await params.response.text(),
            'time': elapsed,
            'uuid': trace_config_ctx.uuid,
        }
        logger.debug('Server got response', extra={'response': response_data})
