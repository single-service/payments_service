import json_logging


class CustomJSONLog(json_logging.JSONLogWebFormatter):
    """
    Customized logger
    """

    def _format_log_object(self, record, request_util):
        # request and response object can be extracted from record like this
        json_log_object = super()._format_log_object(record, request_util)
        del json_log_object["written_ts"]
        del json_log_object["thread"]

        json_log_object["request_id"] = json_log_object.pop("correlation_id")
        if hasattr(record, 'response'):
            json_log_object["response"] = record.response

        if hasattr(record, 'request'):
            json_log_object["request"] = record.request

        json_log_object.update({"service_name": "x5bank"})

        return json_log_object


class CustomRequestJSONLog(json_logging.JSONRequestLogFormatter):
    """
    Customized logger
    """

    def _format_log_object(self, record, request_util):
        json_log_object = super(CustomRequestJSONLog, self)._format_log_object(
            record,
            request_util,
        )

        del json_log_object["remote_user"]
        del json_log_object["referer"]
        del json_log_object["x_forwarded_for"]

        json_log_object.update(
            {
                "service_name": "x5bank",
                "level": record.levelname,
            },
        )
        return json_log_object


class CustomBrawlJSONLog(json_logging.JSONLogFormatter):
    """
    Customized logger
    """

    def _format_log_object(self, record, request_util):
        json_log_object = super(CustomBrawlJSONLog, self)._format_log_object(
            record,
            request_util,
        )

        json_log_object.update(
            {
                "service_name": "5ka-api-campaign",
                "level": record.levelname,
                "request": record.request,
                "method": record.method,
                "response_time_ms": record.response_time_ms,
                "response_status": record.response_status,
            },
        )
        return json_log_object
