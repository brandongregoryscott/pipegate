from __future__ import annotations

import asyncio
import collections
import uuid
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import AsyncGenerator, cast, get_args

import async_timeout
import jwt
import orjson
import uvicorn
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
)
from pydantic import UUID4, ValidationError

from .schemas import (
    BufferGateRequest,
    BufferGateResponse,
    JWTPayload,
    Methods,
    Settings,
)


def get_settings(request: Request) -> Settings:
    return request.app.extra["settings"]


def verify_jwt_uuid_match(
    connection_id: UUID4,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> JWTPayload:
    """
    Verify the JWT token, validate its structure, and ensure the 'uuid' matches the path parameter.
    """
    authorization: str | None = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
        )

    token = authorization.split(" ", 1)[1]

    decoded_payload = jwt.decode(
        token,
        settings.jwt_secret.get_secret_value(),
        algorithms=settings.jwt_algorithms,
    )
    payload = JWTPayload.model_validate(decoded_payload)

    # Verify that the token's UUID (sub) matches the path parameter connection_id
    if payload.sub != connection_id:
        raise HTTPException(
            status_code=403, detail="Token UUID does not match path UUID"
        )

    return payload


def create_app() -> FastAPI:
    """
    Initialize and configure the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    buffers: collections.defaultdict[UUID4, asyncio.Queue[BufferGateRequest]] = (
        collections.defaultdict(asyncio.Queue)
    )
    futures: collections.defaultdict[UUID4, asyncio.Future[BufferGateResponse]] = (
        collections.defaultdict(asyncio.Future)
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """
        Define the application's lifespan events.

        Args:
            _: FastAPI: The FastAPI application instance.

        Yields:
            AsyncGenerator[None, None]: Yields control back to FastAPI.
        """
        app.extra["settings"] = Settings()

        try:
            yield
        finally:
            # On shutdown, set exceptions for all pending futures to prevent hanging
            for fut in futures.values():
                if not fut.done():
                    fut.set_exception(
                        HTTPException(status_code=504, detail="Gateway Timeout")
                    )

    app = FastAPI(lifespan=lifespan)

    @app.api_route(
        "/{connection_id}/{path_slug:path}",
        methods=list(get_args(Methods)),
    )
    async def handle_http_request(
        connection_id: UUID4,
        request: Request,
        path_slug: str = "",
        payload: JWTPayload = Depends(verify_jwt_uuid_match),
    ) -> Response:
        """
        Handle incoming HTTP requests and forward them to the corresponding WebSocket connection.

        Args:
            connection_id (uuid.UUID): The unique identifier for the connection.
            request (Request): The incoming HTTP request.
            path_slug (str, optional): Additional path after the connection ID. Defaults to "".

        Returns:
            Response: The HTTP response received from the WebSocket client.
        """
        correlation_id = uuid.uuid4()

        try:
            await buffers[connection_id].put(
                BufferGateRequest(
                    correlation_id=correlation_id,
                    method=cast(Methods, request.method),
                    url_path=path_slug,
                    url_query=orjson.dumps(
                        {k: v for k, v in request.query_params.multi_items()}
                    ).decode(),
                    headers=orjson.dumps(
                        {
                            **dict(request.headers),
                            "x-pipegate-correlation-id": correlation_id.hex,
                        }
                    ).decode(),
                    body=(await request.body()).decode(),
                )
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to enqueue request: {e}"
            ) from e

        timeout = timedelta(seconds=300)

        try:
            async with async_timeout.timeout(timeout.total_seconds()):
                response = await futures[correlation_id]
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Gateway Timeout")
        finally:
            futures.pop(correlation_id, None)

        return Response(
            content=response.body.encode(),
            headers=orjson.loads(response.headers) if response.headers else {},
            status_code=response.status_code,
        )

    @app.websocket("/{connection_id}")
    async def handle_websocket(
        connection_id: UUID4,
        websocket: WebSocket,
    ):
        """
        Manage WebSocket connections for sending and receiving data.

        Args:
            connection_id (uuid.UUID): The unique identifier for the WebSocket connection.
            websocket (WebSocket): The WebSocket connection object.
        """
        await websocket.accept()
        print(f"WebSocket connection established for ID: {connection_id}")

        async def receive():
            """
            Receive messages from the WebSocket and resolve pending futures.
            """
            try:
                while True:
                    message_text = await websocket.receive_text()
                    try:
                        message = BufferGateResponse.model_validate_json(message_text)
                        future = futures.get(message.correlation_id)
                        if future and not future.done():
                            future.set_result(message)
                        else:
                            print(
                                f"No pending future for correlation ID: {message.correlation_id}"
                            )
                    except ValidationError as ve:
                        print(f"Invalid message format: {ve}")
                    except Exception as e:
                        print(f"Error processing received message: {e}")
            except WebSocketDisconnect as e:
                print(f"WebSocket disconnected during receive: {e}")
            except Exception as e:
                print(f"Unexpected error in receive handler: {e}")

        async def send():
            """
            Send messages from the buffer queue to the WebSocket.
            """
            try:
                while True:
                    request = await buffers[connection_id].get()
                    try:
                        await websocket.send_text(request.model_dump_json())
                    except WebSocketDisconnect as e:
                        print(f"WebSocket disconnected during send: {e}")
                        break
                    except Exception as e:
                        print(f"Error sending message: {e}")
            except Exception as e:
                print(f"Unexpected error in send handler: {e}")

        await asyncio.gather(receive(), send())
        print(f"WebSocket connection closed for ID: {connection_id}")

    return app


if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
