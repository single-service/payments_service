from pydantic import BaseModel


class TokenCreateRequest(BaseModel):
    token_type: int


class TokenCheckRequest(BaseModel):
    token: str
