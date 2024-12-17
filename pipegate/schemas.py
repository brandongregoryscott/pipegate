from __future__ import annotations

import uuid
from typing import Literal

from pydantic import UUID4, BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

Methods = Literal[
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "PATCH",
    "OPTIONS",
    "HEAD",
]


class BufferGateCorrelationId(BaseModel):
    correlation_id: uuid.UUID


class BufferGateRequest(BufferGateCorrelationId):
    url_path: str
    url_query: str

    method: Methods
    headers: str
    body: str


class BufferGateResponse(BufferGateCorrelationId):
    headers: str
    body: str
    status_code: int


class JWTPayload(BaseModel):
    sub: UUID4  # UUID of the user or connection_id
    exp: int  # Expiration timestamp


class Settings(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True)
    jwt_secret: SecretStr = Field(alias="PIPEGATE_JWT_SECRET")
    jwt_algorithms: list[str] = Field(alias="PIPEGATE_JWT_ALGORITHMS")
