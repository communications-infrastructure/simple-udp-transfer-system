# Simple File Transfer System

Simple file transfer system using TCP protocol between client and server.

## Usage

For executing the server in your system, use the following commands:

```sh
# Download Docker image
docker pull ghcr.io/communications-infrastructure/simple-file-transfer-system-server@sha256:44f3ef8b15a4709d767ca0112e4406b64160d4a22ac3faf573b89d7b2657ddb6

# Start container with server
docker run --platform linux/amd64 -p 6969:6969 -i ghcr.io/communications-infrastructure/simple-file-transfer-system-server@sha256:44f3ef8b15a4709d767ca0112e4406b64160d4a22ac3faf573b89d7b2657ddb6
```

For executing the client in your system, use the following commands:

```sh
# Download Docker image
docker pull ghcr.io/communications-infrastructure/simple-file-transfer-system-client:main

# Start container with client
docker run --platform linux/amd64 -i ghcr.io/communications-infrastructure/simple-file-transfer-system-client:main
```

> **_NOTE:_** If you have problems connecting the client with the server from Windows, try to clone this repository and run directly the `./client/client.py` file. This may be due to your virtualization settings.

For verifying Docker image contents, export container filesystem with:

```sh
docker export $(docker ps -lq) -o out.tar
```

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](LICENSE)**
- Copyright 2022 © Juan Romero & Juan Alegría
