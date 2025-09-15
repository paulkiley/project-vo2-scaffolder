#!/bin/bash
#
# @project: Project VO2
# @file:    scripts/01-setup-env.sh
# @author:  Project VO2 Contributors
# @brief:   Sets up the Python virtual environment and installs dependencies.
#
# Sets up the Python virtual environment and installs dependencies using uv.
# Sources configuration from project.conf.
#

set -euo pipefail

# This script is called by bootstrap.sh, which sets the working directory.
# shellcheck source=../project.conf
source "project.conf"

# --- Functions ---
info() { echo -e "  \033[34m[INFO]\033[0m $1"; }
success() { echo -e "  \033[32m[SUCCESS]\033[0m $1"; }
error() { echo -e "  \033[31m[ERROR]\033[0m $1" >&2; exit 1; }

# --- Main Logic ---
# Check for and install 'uv' if necessary
if ! command -v uv &> /dev/null; then
    info "'uv' not found. Installing via pip..."
    python3 -m pip install uv || error "Failed to install 'uv'."
    success "'uv' installed."
else
    info "'uv' is already installed."
fi

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    info "Creating Python virtual environment in './$VENV_DIR'..."
    uv venv || error "Failed to create virtual environment."
    success "Virtual environment created."
else
    info "Virtual environment './$VENV_DIR' already exists."
fi

# Install dependencies
info "Installing dependencies..."
# shellcheck disable=SC2154
"$VENV_DIR/bin/uv" pip install Jinja2 || error "Failed to install Jinja2."
success "Dependencies installed."

