from __future__ import annotations

import uuid

from pydantic import BaseModel


class BufferGateCorrelationId(BaseModel):
    correlation_id: uuid.UUID


class BufferGateRequest(BufferGateCorrelationId):
    url_path: str
    url_query: str

    method: str
    headers: str
    body: str


class BufferGateResponse(BufferGateCorrelationId):
    headers: str
    body: str
    status_code: int
