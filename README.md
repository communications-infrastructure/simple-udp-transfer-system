# Simple File Transfer System

Simple file transfer system using TCP protocol between client and server.

## Usage

For executing the server in your system, use the following commands:
```sh
# Download Docker image
docker pull ghcr.io/communications-infrastructure/simple-file-transfer-system:main

# Start container with server
docker run --platform linux/amd64 -e PYTHONUNBUFFERED=1 ghcr.io/communications-infrastructure/simple-file-transfer-system:main
```

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](LICENSE)**
- Copyright 2022 © Juan Romero & Juan Alegría

