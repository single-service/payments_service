from pydantic import BaseModel


class SimpleBoolenSchema(BaseModel):
    detail: bool = True


class LiveResponseSchema(BaseModel):
    live: str = "ok"
