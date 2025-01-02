from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt

from .schemas import JWTPayload, Settings


def make_jwt_bearer() -> None:
    settings = Settings()
    connection_id = settings.connection_id or uuid.uuid4().hex

    jwt_payload = JWTPayload(
        sub=connection_id,
        exp=int((datetime.now(UTC) + timedelta(days=21)).timestamp()),
    )

    jwt_bearer = jwt.encode(
        jwt_payload.model_dump(mode="json"),
        key=settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithms[0],
    )

    print(f"Connection-id: {connection_id}")
    print(f"JWT Bearer:    {jwt_bearer}")


if __name__ == "__main__":
    make_jwt_bearer()
