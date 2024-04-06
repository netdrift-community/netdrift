from typing import Literal

from pydantic import BaseModel


class Webhook(BaseModel):
    method: Literal["get", "post"] = "get"
    url: str
    body: dict
    session_kwargs: dict | None = {}
    method_kwargs: dict | None = {}
