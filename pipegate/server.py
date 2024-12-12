from __future__ import annotations

import asyncio
import collections
import uuid
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import AsyncGenerator

import async_timeout
import orjson
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
)

from .schemas import BufferGateRequest, BufferGateResponse


def main() -> FastAPI:
    buffers = collections.defaultdict[
        uuid.UUID,
        asyncio.Queue[BufferGateRequest],
    ](asyncio.Queue)

    futures = collections.defaultdict[
        uuid.UUID,
        asyncio.Future[BufferGateResponse],
    ](asyncio.Future)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        yield

        for fut in futures.values():
            fut.set_exception(HTTPException(504))

    app = FastAPI(lifespan=lifespan)

    @app.api_route(
        "/{connection_id}/{path_slug:path}",
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    )
    async def handle_http_request(
        connection_id: uuid.UUID,
        request: Request,
        path_slug: str = "",
    ):
        """Handle HTTP requests and forward them to the WebSocket connection.

        Args:
            connection_id (uuid.UUID): The unique identifier for the connection.
            request (Request): The incoming HTTP request.
            path_slug (str): Additional path after the connection ID.

        Returns:
            Response: The HTTP response received from the WebSocket client.
        """
        correlation_id = uuid.uuid4()

        await buffers[connection_id].put(
            BufferGateRequest(
                correlation_id=correlation_id,
                method=request.method,
                url_path=path_slug,
                url_query=orjson.dumps(str(request.query_params)).decode(),
                headers=orjson.dumps(
                    dict(request.headers)
                    | {"x-pipegate-correlation-id": correlation_id.hex}
                ).decode(),
                body=(await request.body()).decode(),
            )
        )

        timeout = timedelta(seconds=300)

        try:
            async with async_timeout.timeout(timeout.total_seconds()):
                response = await futures[correlation_id]
        except TimeoutError:
            raise HTTPException(504)
        finally:
            futures.pop(correlation_id)

        return Response(
            content=response.body,
            headers=orjson.loads(response.headers) if response.headers else {},
            status_code=response.status_code,
        )

    @app.websocket("/{connection_id}")
    async def handle_websocket(
        connection_id: uuid.UUID,
        websocket: WebSocket,
    ):
        """Handle WebSocket connections for sending and receiving data.

        Args:
            connection_id (uuid.UUID): The unique identifier for the WebSocket connection.
            websocket (WebSocket): The WebSocket connection object.
        """
        await websocket.accept()

        async def receive():
            """Receive messages from the WebSocket and resolve pending futures."""
            try:
                while True:
                    message = BufferGateResponse.model_validate_json(
                        await websocket.receive_text()
                    )
                    futures[message.correlation_id].set_result(message)
            except WebSocketDisconnect as e:
                print("Disconnect receive", e)
                return
            except Exception as e:
                print(f"Error in receive handler: {e}")

        async def send():
            """Send messages from the buffer queue to the WebSocket."""
            try:
                while True:
                    await websocket.send_text(
                        (await buffers[connection_id].get()).model_dump_json()
                    )
            except WebSocketDisconnect as e:
                print("Disconnect send", e)
                return
            except Exception as e:
                print(f"Error in send handler: {e}")

        await asyncio.gather(receive(), send())

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(main())
