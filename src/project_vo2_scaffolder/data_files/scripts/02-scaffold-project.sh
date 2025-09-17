#!/bin/bash
#
# @project: Project VO2
# @file:    scripts/02-scaffold-project.sh
# @author:  Project VO2 Contributors
# @brief:   Creates the required directories and empty source files.
#
# Creates the required directories and empty source files for the project
# based on the paths defined in project.conf. This script is idempotent.
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
# Create necessary directories
DIRECTORIES=("$TEMPLATE_DIR" "$SRC_DIR")
for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$dir" ]; then
        info "Creating directory: $dir/"
        mkdir -p "$dir"
        success "Directory '$dir/' created."
    else
        info "Directory '$dir/' already exists."
    fi
done

# Create the empty template files
for tpl in "${TEMPLATE_FILES[@]}"; do
    FILE_PATH="$TEMPLATE_DIR/$tpl"
    if [ ! -f "$FILE_PATH" ]; then
        info "Creating empty template file: $FILE_PATH"
        touch "$FILE_PATH"
        success "File '$FILE_PATH' created."
    else
        info "Template file '$FILE_PATH' already exists."
    fi
done

# Create empty source files in the src directory if they don't exist
SOURCE_FILES=("$STATE_FILE" "$GENERATOR_SCRIPT")
for file in "${SOURCE_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        info "Creating empty source file: $file"
        mkdir -p "$(dirname "$file")"
        touch "$file"
        success "File '$file' created."
    else
        info "Source file '$file' already exists."
    fi
done

success "Project scaffolding is complete."
