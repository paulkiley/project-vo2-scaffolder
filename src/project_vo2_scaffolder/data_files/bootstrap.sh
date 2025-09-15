#!/bin/bash
#
# @project: Project VO2
# @file:    bootstrap.sh
# @author:  Project VO2 Contributors
# @brief:   Main entry point for initializing the development environment.
#
# This is the main entry point for initializing the Project VO2 development
# environment. It is idempotent and orchestrates all necessary setup and
# scaffolding scripts.
#

set -euo pipefail # Strict mode

# --- Configuration ---
CONFIG_FILE="project.conf"
SCRIPTS_DIR="scripts"

# --- Functions for clear, colored output ---
info() { echo -e "\033[34m[INFO]\033[0m $1"; }
success() { echo -e "\033[32m[SUCCESS]\033[0m $1"; }
error() { echo -e "\033[31m[ERROR]\033[0m $1" >&2; exit 1; }

# --- Banner Function ---
display_banner() {
    echo -e "\033[32m" # Green text for the banner
    echo ' ____  _                       _   _'
    echo '|  _ \| | __ _ _   _  ___  ___| |_| |_'
    echo '| |_) | |/ _` | | | |/ _ \/ __| __| __|'
    echo '|  __/| | (_| | |_| |  __/\__ \ |_| |_'
    echo '|_|   |_|\__,_|\__, |\___||___/\__|_\__|'
    echo '               |___/'
    echo -e "\033[0m" # Reset text color
}

# --- Main Logic ---
main() {
    # 1. Source the project configuration first to get the name
    if [ ! -f "$CONFIG_FILE" ]; then
        error "Configuration file '$CONFIG_FILE' not found. Cannot proceed."
    fi
    # shellcheck source=project.conf
    source "$CONFIG_FILE"

    clear # Clear the screen for a clean start
    display_banner
    info "Bootstrapping Environment for: $PROJECT_NAME"
    echo # Add a newline for spacing

    # 2. Perform pre-flight checks
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not found on your PATH. Please install it to continue."
    fi
    success "Pre-flight checks passed."

    # 3. Execute sub-scripts in order
    info "Executing environment setup script..."
    bash "$SCRIPTS_DIR/01-setup-env.sh"

    info "Executing project scaffolding script..."
    bash "$SCRIPTS_DIR/02-scaffold-project.sh"

    # 4. Provide clear next steps
    echo
    success "Bootstrap complete! Your project is ready."
    info "To activate the virtual environment, run:"
    info "  source $VENV_DIR/bin/activate"
    info "Then, to generate the documentation, run:"
    info "  python $GENERATOR_SCRIPT"
}

# --- Run the main function ---
main

