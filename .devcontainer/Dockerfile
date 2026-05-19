# https://github.com/devcontainers/images/tree/main/src/python
FROM mcr.microsoft.com/devcontainers/python:3.14@sha256:882b17d068262c7af4300180ead0ee14423d2c03393778c92435b0ca642dea07
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
