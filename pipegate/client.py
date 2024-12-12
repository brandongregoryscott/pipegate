from __future__ import annotations

import asyncio

import httpx
import orjson
import typer
from websockets.asyncio.client import ClientConnection, connect

from .schemas import BufferGateRequest, BufferGateResponse

app = typer.Typer()


@app.command()
def start_server(port: int, server_url: str):
    """Start the Buffer Gate Server.

    Args:
        port (int): The port number on which the server will run.
        server_url (str): The WebSocket server URL to connect to.
    """
    asyncio.run(main(port, server_url))


async def request_and_response(
    target: str,
    request: BufferGateRequest,
    http_client: httpx.AsyncClient,
    ws_client: ClientConnection,
) -> None:
    """Send an HTTP request based on the BufferGateRequest and forward the response via WebSocket.

    Args:
        target (str): The target URL for the HTTP request.
        request (BufferGateRequest): The request payload containing HTTP details.
        http_client (httpx.AsyncClient): The HTTP client for making requests.
        ws_client (ClientConnection): The WebSocket client for sending responses.
    """
    try:
        response = await http_client.request(
            method=request.method,
            url=f"{target}/{request.url_path}",
            headers=orjson.loads(request.headers),
            params=orjson.loads(request.url_query),
            content=request.body,
        )
        await ws_client.send(
            BufferGateResponse(
                correlation_id=request.correlation_id,
                headers=orjson.dumps(dict(response.headers)).decode(),
                body=response.content.decode(),
                status_code=response.status_code,
            ).model_dump_json()
        )
    except Exception as e:
        print(e)
        await ws_client.send(
            BufferGateResponse(
                correlation_id=request.correlation_id,
                headers="",
                body="",
                status_code=504,
            ).model_dump_json()
        )


async def main(port: int, server_url: str) -> None:
    """Main function to handle WebSocket connections and route HTTP requests.

    Args:
        port (int): The port number for the HTTP server.
        server_url (str): The WebSocket server URL to connect to.
    """
    target = f"http://0.0.0.0:{port}"

    async with (
        connect(server_url) as ws_client,
        httpx.AsyncClient() as http_client,
        asyncio.TaskGroup() as tg,
    ):
        async for message in ws_client:
            request = BufferGateRequest.model_validate_json(message)
            tg.create_task(
                request_and_response(
                    target,
                    request,
                    http_client,
                    ws_client,
                )
            )


if __name__ == "__main__":
    app()
