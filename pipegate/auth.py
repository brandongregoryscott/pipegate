from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt

from .schemas import JWTPayload, Settings


def make_jwt_bearer() -> None:
    connection_id = uuid.uuid4()
    settings = Settings()

    jwt_paylaod = JWTPayload(
        sub=connection_id,
        exp=int((datetime.now(UTC) + timedelta(days=21)).timestamp()),
    )

    jwt_bearer = jwt.encode(
        jwt_paylaod.model_dump(mode="json"),
        key=settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithms[0],
    )

    print(f"Connection-id: {connection_id.hex}")
    print(f"JWT Bearer:    {jwt_bearer}")


if __name__ == "__main__":
    make_jwt_bearer()
