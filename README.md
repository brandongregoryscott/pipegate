# PipeGate
PipeGate is a lightweight, self-hosted proxy built with FastAPI, designed as a "poor man's ngrok." It allows you to expose your local servers to the internet, providing a simple way to create tunnels from your local machine to the external world. PipeGate is an excellent tool for developers who want to understand how tunneling services like ngrok work under the hood or need a customizable alternative hosted on their own infrastructure.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Clone the Repository](#clone-the-repository)
  - [Install Dependencies](#install-dependencies)
  - [Alternatively, Install via pip](#alternatively-install-via-pip)
- [Usage](#usage)
  - [Starting the Server](#starting-the-server)
  - [Starting the Client](#starting-the-client)
  - [Example Workflow](#example-workflow)
- [Configuration](#configuration)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

## Features

- **Self-Hosted:** Deploy PipeGate on your own infrastructure, giving you control over your setup.
- **Unique Connections:** Clients connect using unique UUIDs, ensuring each tunnel is distinct.
- **Customizable:** Modify and extend PipeGate to fit your specific needs.
- **Lightweight:** Minimal dependencies and straightforward setup make it easy to use.
- **Educational:** A great tool for learning how tunneling services operate internally.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.12+**
- [Git](https://git-scm.com/)
- [pip](https://pip.pypa.io/en/stable/installation/)

## Installation

### Clone the Repository

First, clone the PipeGate repository to your local machine:

```bash
git clone https://github.com/janbjorge/pipegate.git
cd pipegate
```

### Install Dependencies

You can also install PipeGate directly from GitHub using pip:

```bash
pip install git+https://github.com/janbjorge/pipegate.git
```

## Usage

### Starting the Server

Deploy the PipeGate server on your infrastructure. By default, the server runs on `http://0.0.0.0:8000`.

```bash
python -m pipegate.server
```

**Optional:** To customize the host and port, modify the `uvicorn.run` parameters in `server.py` or set environment variables if implemented.

### Starting the Client

Run the PipeGate client on your local machine to expose a local server.

```bash
python -m pipegate.client --port 8000 --server_url wss://yourserver.com/<connection_id>
```

**Parameters:**

- `--port`: Port where your local server is running (e.g., `8000`).
- `--server_url`: WebSocket URL of your PipeGate server, including the unique connection ID.

**Example:**

```bash
python -m pipegate.client --port 8000 --server_url wss://example.com/123e4567-e89b-12d3-a456-426614174000
```

### Example Workflow

1. **Start the Server:**

   ```bash
   python -m pipegate.server
   ```

2. **Start the Client:**

   ```bash
   python -m pipegate.client --port 8000 --server_url wss://yourserver.com/<connection_id>
   ```

   Replace `<connection_id>` with a generated UUID to establish a unique tunnel.

3. **Expose Local Server:**

   Point your external webhooks or services to `https://yourserver.com/<connection_id>/path`, and PipeGate will forward the requests to your local server running on port `8000`.

### Public Server (Temporary)

For demonstration purposes, a PipeGate server is currently running at [https://pipegate.fly.dev/](https://pipegate.fly.dev/). Feel free to use this server to test PipeGate functionality. This server will remain operational until the Fly.io credits are exhausted. 🤷‍♂️

**Usage Example with Public Server:**

1. **Start the Client:**

   ```bash
   python -m pipegate.client --port 8000 --server_url wss://pipegate.fly.dev/123e4567-e89b-12d3-a456-426614174000
   ```

   Replace `123e4567-e89b-12d3-a456-426614174000` with a generated UUID.

2. **Expose Local Server:**

   Point your external webhooks or services to `https://pipegate.fly.dev/123e4567-e89b-12d3-a456-426614174000/path`, and PipeGate will forward the requests to your local server running on port `8000`.

*Note: The public server at [https://pipegate.fly.dev/](https://pipegate.fly.dev/) is intended for temporary use only. Users are encouraged to set up their own PipeGate server for persistent and secure tunneling.*

## Configuration

PipeGate is highly customizable. You can modify the server and client configurations to tailor the tool to your specific needs. Refer to the source code and documentation for detailed configuration options.

**Possible Configuration Enhancements:**

- **Authentication:** Implement API keys or tokens to manage client connections.
- **Timeouts:** Adjust request and connection timeouts based on your requirements.
- **Logging:** Configure logging levels and outputs to monitor activity.

*Note: Future releases may include configuration files or environment variable support for easier customization.*

## Security Considerations

**PipeGate** has minimal to no built-in security features. It is essential to implement your own security measures to protect your infrastructure when using PipeGate. Consider the following:

- **Authentication:** Ensure that only authorized clients can connect to your PipeGate server by implementing authentication mechanisms such as API keys or tokens.
- **Network Security:** Utilize firewalls, VPNs, or other network security tools to restrict access to your PipeGate server.
- **Input Validation:** Apply thorough validation and filtering of incoming requests to prevent malicious activities.
- **Encryption:** Consider setting up HTTPS to encrypt data in transit, especially if transmitting sensitive information.
- **Monitoring and Auditing:** Regularly monitor and audit your PipeGate setup to detect and respond to potential threats.
- **Resource Limiting:** Implement rate limiting or throttling to prevent abuse and ensure fair usage of server resources.

*Disclaimer: PipeGate is provided "as is" without any guarantees. Use it at your own risk.*

## Contributing

Contributions are welcome! Whether you're fixing bugs, improving documentation, or adding new features, your help is appreciated.

### How to Contribute

1. **Fork the Repository:** Click the "Fork" button at the top right of the repository page.
2. **Clone Your Fork:**

   ```bash
   git clone https://github.com/janbjorge/pipegate.git
   cd pipegate
   ```

3. **Create a New Branch:**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes:** Implement your feature or fix.
5. **Commit Your Changes:**

   ```bash
   git commit -m "Add your message here"
   ```

6. **Push to Your Fork:**

   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Open a Pull Request:** Go to the original repository and create a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [HTTPX](https://www.python-httpx.org/)
- [Typer](https://typer.tiangolo.com/)
- Inspired by [ngrok](https://ngrok.com/)

## Contact

For any questions or suggestions, feel free to open an issue.

## FAQ
   **Q:** How do I generate a unique connection ID?

   **A:** You can use Python's `uuid` module or any UUID generator to create a unique ID.

   **Q:** Can I run multiple clients with the same server?

   **A:** Yes, each client should use a unique connection ID to establish separate tunnels.
