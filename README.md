# Simple File Transfer System

Simple file transfer system using TCP protocol between client and server.

## Usage

For executing the server in your system, use the following commands:
```sh
# Download Docker image
docker pull ghcr.io/communications-infrastructure/simple-file-transfer-system-server:main

# Start container with server
docker run --platform linux/amd64 -i ghcr.io/communications-infrastructure/simple-file-transfer-system-server:main
```

For executing the client in your system, use the following commands:
```sh
# Download Docker image
docker pull ghcr.io/communications-infrastructure/simple-file-transfer-system-client:main

# Start container with client
docker run --platform linux/amd64 -i ghcr.io/communications-infrastructure/simple-file-transfer-system-client:main
```
For verifying Docker image contents, export container filesystem with:

```sh
docker export $(docker ps -lq) -o out.tar
```

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](LICENSE)**
- Copyright 2022 © Juan Romero & Juan Alegría
