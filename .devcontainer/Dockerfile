# https://github.com/devcontainers/images/tree/main/src/python
FROM mcr.microsoft.com/devcontainers/python:3.14@sha256:66af9ee0a89e76f83b5c54a0cfdc19966ec8e443e294707f8f9b45f465b42cf1
# Set up requirements
RUN apt-get update && apt-get --no-install-recommends install -y \
    # Cryptg and Pillow requirements for Telethon
    clang \
    libjpeg-dev \
    libwebp-dev \
    python3-dev \
    zlib1g-dev \
    \
    # ffmpeg for yt-dlp
    ffmpeg \
    \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
