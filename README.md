# pipegate

**pipegate** is a lightweight, self-hosted proxy built with FastAPI, designed as a "poor man's ngrok." It allows you to expose your local servers to the internet securely, giving you full control over security rules and configurations.

## Features

- **Self-Hosted:** Deploy on your own infrastructure.
- **Unique Connections:** Clients connect using unique IDs.
- **Customizable:** Apply your own security and filtering rules.

## Prerequisites

- **Python 3.12+**
- [Git](https://git-scm.com/)
- [pip](https://pip.pypa.io/en/stable/installation/)

## Install from GitHub

   ```bash
   pip install git+https://github.com/yourusername/pipegate.git
   ```

   *Replace `yourusername` with your GitHub username.*

## Usage

### Start the Server

```bash
python -m pipegate.server
```

By default, the server runs on `http://0.0.0.0:8000`.

### Start the Client

```bash
python -m pipegate.client --port 8000 --server_url wss://yourserver.com/<connection_id:uuid>
```

**Parameters:**

- `--port`: Port where your local server is running.
- `--server_url`: WebSocket URL of your pipegate server.

## Security Considerations

**pipegate** currently has minimal built-in security. It is assumed that all necessary filtering and security measures are applied **before** traffic reaches this service. Ensure that:

- Only trusted clients can connect.
- Use network security measures (e.g., firewalls, VPNs).
- Regularly monitor and audit your setup.

## Example

1. **Start the Server:**

   ```bash
   python -m pipegate.server
   ```

2. **Start the Client:**

   ```bash
   python -m pipegate.client start_server --port 8000 --server_url ws://localhost:8000/ws
   ```

3. **Expose Local Server:**

   Point your external webhooks to `http://yourserver.com/<unique_id>/path`, and pipegate will forward the requests to your local server on port `8000`.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [HTTPX](https://www.python-httpx.org/)
- Inspired by [ngrok](https://ngrok.com/)
