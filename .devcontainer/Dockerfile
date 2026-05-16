# https://github.com/devcontainers/images/tree/main/src/python
FROM mcr.microsoft.com/devcontainers/python:3.14@sha256:9e51c13505754efe79dd4a0b1a29523d3854090dabb8add3f3fa642ea3c98fad
# Set up cryptg and pillow requirements
RUN apt-get update && apt-get --no-install-recommends install -y \
    # Cryptg and Pillow requirements
    clang \
    libjpeg-dev \
    libwebp-dev \
    python3-dev \
    zlib1g-dev \
    \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
