# PipeGate

PipeGate is a lightweight, self-hosted proxy built with FastAPI, designed as a "poor man's ngrok." It allows you to expose your local servers to the internet, providing a simple way to create tunnels from your local machine to the external world.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Clone the Repository](#clone-the-repository)
  - [Install Dependencies](#install-dependencies)
  - [Alternatively, Install via pip](#alternatively-install-via-pip)
- [Usage](#usage)
  - [Generating a JWT Bearer Token](#generating-a-jwt-bearer-token)
  - [Starting the Server](#starting-the-server)
  - [Starting the Client](#starting-the-client)
  - [Example Workflow](#example-workflow)
- [Configuration](#configuration)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)
- [FAQ](#faq)

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
- [uv](https://github.com/astral-sh/uv)

## Installation

### Clone the Repository

First, clone the PipeGate repository to your local machine:

```bash
git clone https://github.com/janbjorge/pipegate.git
cd pipegate
```

### Install Dependencies

Install the required dependencies using `uv`:

```bash
uv sync
```

### Alternatively, Install via pip

You can also install PipeGate directly from GitHub using pip:

```bash
pip install git+https://github.com/janbjorge/pipegate.git
```

## Usage

### Generating a JWT Bearer Token

PipeGate uses JWT (JSON Web Tokens) for authenticating client connections. To establish a secure tunnel, you need to generate a JWT bearer token that includes a unique connection ID.

1. **Generate the JWT Token:**

   Run the authentication helper script to generate a JWT bearer token and a corresponding connection ID.

   ```bash
   python -m pipegate.auth
   ```

   **Output Example:**

   ```
   Connection-id: 123e4567-e89b-12d3-a456-426614174000
   JWT Bearer:    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

   - **Connection-id:** A unique UUID representing your tunnel connection.
   - **JWT Bearer:** The JWT token you will use to authenticate your requests to the PipeGate server.

2. **Store the Credentials:**

   Keep the `Connection-id` and `JWT Bearer` token secure, as they are required to establish a connection between the server and client.

### Starting the Server

Deploy the PipeGate server on your infrastructure. By default, the server runs on `http://0.0.0.0:8000`.

1. **Configure the Server:**

   Ensure that the server is configured to use the same JWT secret and algorithms as used when generating the JWT token. You can modify the `Settings` in your server configuration as needed, typically found in `server.py` or your configuration files.

2. **Run the Server:**

   ```bash
   python -m pipegate.server
   ```

   **Optional:** To customize the host and port, modify the `uvicorn.run` parameters in `server.py` or set environment variables if implemented.

### Starting the Client

Run the PipeGate client on your local machine to expose a local server.

```bash
python -m pipegate.client <TARGET_URL> <SERVER_URL>
```

**Parameters:**

- `TARGET_URL`: The local target (e.g., `http://127.0.0.1:9090`).
- `SERVER_URL`: WebSocket URL of your PipeGate server, including the unique connection ID.

**Example:**

```bash
python -m pipegate.client http://127.0.0.1:9090 wss://yourserver.com/123e4567-e89b-12d3-a456-426614174000
```

### Example Workflow

1. **Generate a JWT Bearer Token:**

   ```bash
   python -m pipegate.auth
   ```

   *Sample Output:*

   ```
   Connection-id: 123e4567-e89b-12d3-a456-426614174000
   JWT Bearer:    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

2. **Start the Server:**

   Ensure your server is configured with the appropriate JWT settings, then run:

   ```bash
   python -m pipegate.server
   ```

3. **Start the Client:**

   Use the generated `Connection-id` to start the client:

   ```bash
   python -m pipegate.client http://127.0.0.1:9090 wss://yourserver.com/123e4567-e89b-12d3-a456-426614174000
   ```

4. **Expose Local Server:**

   Point your external webhooks or services to `https://yourserver.com/123e4567-e89b-12d3-a456-426614174000/path`, and PipeGate will forward the requests to your local server running on port `9090`.

## Configuration

PipeGate is highly customizable. You can modify the server and client configurations to tailor the tool to your specific needs. Refer to the source code and documentation for detailed configuration options.

**Possible Configuration Enhancements:**

- **Authentication:** PipeGate uses JWT for authenticating client connections. Ensure that the JWT settings (`jwt_secret`, `jwt_algorithms`) in both server and client are consistent.
- **Timeouts:** Adjust request and connection timeouts based on your requirements.
- **Logging:** Configure logging levels and outputs to monitor activity.

*Note: Future releases may include configuration files or environment variable support for easier customization.*

## Security Considerations

**PipeGate** has minimal to no built-in security features beyond JWT authentication. It is essential to implement your own security measures to protect your infrastructure when using PipeGate. Consider the following:

- **Authentication:** Ensure that only authorized clients can connect to your PipeGate server by using strong JWT secrets and managing token distribution securely.
- **Network Security:** Utilize firewalls, VPNs, or other network security tools to restrict access to your PipeGate server.
- **Input Validation:** Apply thorough validation and filtering of incoming requests to prevent malicious activities.
- **Encryption:** Ensure that HTTPS is set up to encrypt data in transit, especially if transmitting sensitive information.
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

**A:** You can use Python's `uuid` module or any UUID generator to create a unique ID. Alternatively, use the provided authentication helper to generate a connection ID along with a JWT bearer token.

**Q:** Can I run multiple clients with the same server?

**A:** Yes, each client should use a unique connection ID and corresponding JWT bearer token to establish separate tunnels.

**Q:** How do I renew my JWT bearer token?

**A:** Generate a new JWT bearer token using the authentication helper script and update both the server and client configurations accordingly.

**Q:** What happens if my JWT token expires?

**A:** If the JWT token expires, the client will no longer be able to authenticate with the server. Generate a new token and restart the client with the updated token.
