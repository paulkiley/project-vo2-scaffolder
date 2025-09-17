#!/bin/bash
#
# @project: Project VO2 Bootstrapper
# @file:    01-create-structure.sh
# @author:  Project VO2 Contributors
# @brief:   Creates the complete directory structure and empty files for the scaffolder.
#

set -euo pipefail

# --- Functions for clear, colored output ---
info() { echo -e "\033[34m[INFO]\033[0m $1"; }
success() { echo -e "\033[32m[SUCCESS]\033[0m $1"; }
error() { echo -e "\033[31m[ERROR]\033[0m $1" >&2; exit 1; }

main() {
    info "Step 1: Creating project directory structure and empty files..."

    # Define the structure
    DIRECTORIES=(
        "src/project_vo2_scaffolder/data_files/scripts"
        "src/project_vo2_scaffolder/data_files/src"
        "src/project_vo2_scaffolder/data_files/templates"
    )

    FILES=(
        "pyproject.toml"
        "src/project_vo2_scaffolder/__main__.py"
        "src/project_vo2_scaffolder/data_files/bootstrap.sh"
        "src/project_vo2_scaffolder/data_files/project.conf"
        "src/project_vo2_scaffolder/data_files/scripts/01-setup-env.sh"
        "src/project_vo2_scaffolder/data_files/scripts/02-scaffold-project.sh"
        "src/project_vo2_scaffolder/data_files/src/generate_docs.py"
        "src/project_vo2_scaffolder/data_files/src/vo2_project_state.jsonl"
        "src/project_vo2_scaffolder/data_files/templates/ADR.md.j2"
        "src/project_vo2_scaffolder/data_files/templates/Project_Charter.md.j2"
        "src/project_vo2_scaffolder/data_files/templates/README.md.j2"
    )

    # Create directories
    for dir in "${DIRECTORIES[@]}"; do
        mkdir -p "$dir"
        info "  Created directory: $dir/"
    done

    # Create empty files
    for file in "${FILES[@]}"; do
        # Ensure parent directory exists before touching the file
        mkdir -p "$(dirname "$file")"
        touch "$file"
        info "  Created empty file: $file"
    done

    success "Directory structure created successfully."
}

main
