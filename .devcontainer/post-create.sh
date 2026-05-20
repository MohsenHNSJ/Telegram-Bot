#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# post-create.sh
#
# This script runs after the development container is created.
# It prepares the Python development environment using Poetry.
#
# Responsibilities:
#   - Display environment information
#   - Generate/update poetry.lock
#   - Install dependencies
#   - Synchronize the virtual environment
#   - Install and verify FFmpeg and FFprobe
#   - Install Deno (JavaScript/TypeScript runtime)
#   - Install yt-dlp-ejs for JS-heavy extractor support
#
# The script fails immediately on any error.
# -----------------------------------------------------------------------------

# Enable strict mode:
#   -E : Propagate ERR trap
#   -e : Exit on error
#   -u : Treat unset variables as errors
#   -o pipefail : Fail if any command in a pipeline fails
set -Eeuo pipefail

# Restrict word splitting to newline and tab for safer scripting
IFS=$'\n\t'

# -----------------------------------------------------------------------------
# log <message>
#
# Outputs a timestamped log entry.
# Used instead of plain echo to improve traceability in CI logs
# and container startup diagnostics.
# -----------------------------------------------------------------------------
log() {
	printf "\n[%s] %s\n" "$(date +'%Y-%m-%d %H:%M:%S')" "$1"
}

# Capture any error and print the line number before exiting.
# Helps diagnose failures during automated container builds.
trap 'echo "Error: Script failed at line $LINENO." >&2' ERR

# -----------------------------------------------------------------------------
# Toolchain Visibility
# -----------------------------------------------------------------------------

# Display Poetry metadata to confirm toolchain version.
# Useful for debugging environment inconsistencies between
# local development and containerized builds.
log "Poetry version:"
poetry about

# Display detailed environment information.
# Provides visibility into:
#   - Python version
#   - Virtual environment path
#   - Active configuration
# This output is valuable when diagnosing dependency resolution issues.
log "System information:"
poetry debug info

# -----------------------------------------------------------------------------
# Dependency Resolution
# -----------------------------------------------------------------------------

# Generate or update poetry.lock.
# Ensures dependency resolution is deterministic and aligned
# with pyproject.toml before installation.
log "Writing Poetry lock file..."
poetry lock

# -----------------------------------------------------------------------------
# Environment Installation
# -----------------------------------------------------------------------------

# Install project dependencies into the virtual environment.
# Reads exact versions from poetry.lock to ensure reproducibility.
log "Installing dependencies..."
poetry install

# Synchronize the environment strictly with poetry.lock.
# Removes packages not defined in the lock file to prevent drift.
log "Syncing Poetry environment..."
poetry sync
log "Poetry environment setup completed successfully."

# -----------------------------------------------------------------------------
# FFmpeg & FFprobe Verification
#
# Ensures that the FFmpeg and FFprobe binaries are installed and accessible
# in the system PATH. These tools are required by yt-dlp to merge audio and
# video streams, convert formats, and process media files.
# -----------------------------------------------------------------------------

log "Verifying FFmpeg installation..."

# Check if 'ffmpeg' binary exists in PATH
if command -v ffmpeg >/dev/null 2>&1; then
    # Binary found, log the first line of version info for quick verification
    log "FFmpeg version:"
    ffmpeg -version | head -n 1
else
    # Binary not found, warn the user that FFmpeg is missing
    log "FFmpeg is not installed or not in PATH!"
fi

# Check if 'ffprobe' binary exists in PATH
if command -v ffprobe >/dev/null 2>&1; then
    # Binary found, log the first line of version info for quick verification
    log "FFprobe version:"
    ffprobe -version | head -n 1
else
    # Binary not found, warn the user that FFprobe is missing
    log "FFprobe is not installed or not in PATH!"
fi

log "FFmpeg and FFprobe verification completed."

# -----------------------------------------------------------------------------
# Deno Installation
#
# Deno is a modern JavaScript/TypeScript runtime that is required by
# yt-dlp-ejs to evaluate JavaScript-heavy pages. Installing Deno allows
# the bot to use yt-dlp-ejs for sites that require JS execution.
# -----------------------------------------------------------------------------
log "Installing Deno (JavaScript/TypeScript runtime)..."

# Download and run the official Deno installation script.
# - 'curl -fsSL' : fetches the install script silently, failing on errors
# - 'sh'         : executes the fetched shell script
# The script installs Deno into the default directory: $HOME/.deno
curl -fsSL https://deno.land/install.sh | sh

# Add the Deno binary directory to the PATH for the current shell session
# This ensures that the 'deno' command can be called from anywhere
export PATH="${HOME}/.deno/bin:${PATH}"

log "Verifying Deno installation..."

# 'command -v deno' checks if the 'deno' executable exists in PATH
# '>/dev/null 2>&1' suppresses output, we only care about success/failure
if command -v deno >/dev/null 2>&1; then
    # Installation succeeded, display full version information
    deno --version
else
    # Installation failed or PATH not updated, warn the user
    log "Deno installation failed or not in PATH!"
fi

log "Deno installation and verification completed."

# -----------------------------------------------------------------------------
# yt-dlp-ejs Installation
#
# yt-dlp-ejs is an optional extension for yt-dlp that enables the bot
# to handle JavaScript-heavy websites, including some YouTube pages.
# It requires Deno to execute the JavaScript extractors.
# -----------------------------------------------------------------------------
log "Installing yt-dlp-ejs (yt-dlp JavaScript extractors)..."

# Run the official yt-dlp-ejs installation script using Deno
# - 'deno run' executes the script
# - '-A' grants all permissions (network, filesystem, etc.)
# - '--unstable' allows usage of unstable Deno APIs required by the script
# The script installs the 'yt-dlp-ejs' binary into the Deno bin directory ($HOME/.deno/bin)
deno run -A --unstable https://deno.land/x/yt_dlp_ejs@latest/install.ts


log "Verifying yt-dlp-ejs installation..."

# 'command -v yt-dlp-ejs' checks if the executable exists in PATH
# '>/dev/null 2>&1' suppresses command output, we only care about existence
if command -v yt-dlp-ejs >/dev/null 2>&1; then
    # Binary found, display version for verification
    yt-dlp-ejs --version
else
    # Binary not found, warn the user that installation failed
    log "yt-dlp-ejs installation failed or not in PATH!"
fi

log "Post-create setup completed successfully."
