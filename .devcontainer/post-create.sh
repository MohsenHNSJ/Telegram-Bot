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

# -----------------------------------------------------------------------------
# Completion
# -----------------------------------------------------------------------------

log "Poetry environment setup completed successfully."
