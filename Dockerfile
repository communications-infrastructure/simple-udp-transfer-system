# Download base image
FROM ubuntu:22.04

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive

# Update Ubuntu Software repository
RUN apt update && apt dist-upgrade -y && apt install -y python3 python3-pip git

COPY server .

ENTRYPOINT python3.10 server.py