from app.transports import AiohttpSessionTransport, Transport


class TransportManager:
    def __init__(self, transport: Transport):
        self.transport: Transport = transport

    async def startup(self):
        await self.transport.startup()

    def __call__(self) -> Transport:
        return self.transport

    async def shutdown(self):
        await self.transport.shutdown()


connection_test_getter = TransportManager(AiohttpSessionTransport())
