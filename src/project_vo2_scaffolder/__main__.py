#!/usr/bin/env python3
#
# @project: Project VO2 Scaffolder
# @file:    src/project_vo2_scaffolder/__main__.py
# @author:  Project VO2 Contributors
# @brief:   Professional, idempotent scaffolding tool for Project VO2.
#
# This script is the command-line entry point for the scaffolder. It reads
# the scaffolding files from its own package data and copies them to the
# user's current directory, creating a new Project VO2 workspace.
#

import argparse
import textwrap
import shutil
import stat
from pathlib import Path
from importlib import resources

# --- Constants for colored output ---
C_INFO = "\033[34m"
C_SUCCESS = "\033[32m"
C_WARN = "\033[33m"
C_ERROR = "\033[31m"
C_RESET = "\033[0m"

class Scaffolder:
    """Encapsulates the logic for the project scaffolding tool."""

    def __init__(self, destination: Path):
        self.destination = destination
        try:
            self.source_path = resources.files('project_vo2_scaffolder') / 'data_files'
        except ModuleNotFoundError:
            self._error("Could not find package data. Is the package installed correctly?")

    def scaffold(self, force: bool = False) -> None:
        self._info("Starting project scaffolding...")
        if self.destination_exists():
            if force:
                self._warn("Existing project files found. --force is enabled. Cleaning up first.")
                self.clean(prompt=False)
            else:
                self._error("Project files already exist in this directory. Aborting.")
                self._info("Use --force to overwrite or --clean to remove the existing structure.")
                return
        try:
            shutil.copytree(self.source_path, self.destination, dirs_exist_ok=True)
            self._set_executable_permissions()
            self._success("Project scaffolding complete!")
        except Exception as e:
            self._error(f"An unexpected error occurred during scaffolding: {e}")

    def clean(self, prompt: bool = True) -> None:
        if prompt:
            self._warn("This will permanently delete all scaffolded project files.")
            confirm = input("Are you sure you want to continue? (y/N): ")
            if confirm.lower() != 'y':
                self._info("Cleanup cancelled by user.")
                return
        self._info("Starting cleanup...")
        files_to_remove: list[Path] = []
        dirs_to_remove: list[Path] = []
        if self.source_path.is_dir():
            for src_item in self.source_path.rglob('*'):
                relative_path = src_item.relative_to(self.source_path)
                dest_path = self.destination / relative_path
                if dest_path.exists():
                    if dest_path.is_dir() and not dest_path.is_symlink():
                        dirs_to_remove.append(dest_path)
                    elif dest_path.is_file():
                        files_to_remove.append(dest_path)
        for src_item in self.source_path.iterdir():
            dest_path = self.destination / src_item.name
            if dest_path.is_dir() and dest_path not in dirs_to_remove:
                dirs_to_remove.append(dest_path)
        for f in files_to_remove:
            try:
                f.unlink()
                self._info(f"  Removed file:      {f}")
            except OSError as e:
                self._error(f"Failed to remove file '{f}': {e}")
        dirs_to_remove.sort(key=lambda p: len(p.parts), reverse=True)
        for d in dirs_to_remove:
            try:
                if d.exists():
                    shutil.rmtree(d)
                    self._info(f"  Removed directory: {d}/")
            except OSError as e:
                 self._error(f"Failed to remove directory '{d}': {e}")
        cleaned_count = len(files_to_remove) + len(dirs_to_remove)
        if cleaned_count > 0:
            self._success(f"Cleanup complete. Removed approximately {cleaned_count} items.")
        else:
            self._info("No project files found to clean.")

    def destination_exists(self) -> bool:
        if not self.source_path.is_dir():
             return False
        for item in self.source_path.iterdir():
            if (self.destination / item.name).exists():
                return True
        return False
        
    def _set_executable_permissions(self) -> None:
        executable_scripts = ["bootstrap.sh", "scripts/01-setup-env.sh", "scripts/02-scaffold-project.sh"]
        for script_path_str in executable_scripts:
            script_path = self.destination / script_path_str
            if script_path.exists():
                try:
                    script_path.chmod(script_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                    self._info(f"  Executable permissions set for '{script_path}'.")
                except OSError as e:
                    self._warn(f"Could not set executable permission on '{script_path}': {e}")

    def _info(self, message: str) -> None: print(f"{C_INFO}[INFO]{C_RESET} {message}")
    def _success(self, message: str) -> None: print(f"{C_SUCCESS}[SUCCESS]{C_RESET} {message}")
    def _warn(self, message: str) -> None: print(f"{C_WARN}[WARNING]{C_RESET} {message}")
    def _error(self, message: str) -> None:
        print(f"{C_ERROR}[ERROR]{C_RESET} {message}", flush=True)
        exit(1)

def display_banner() -> None:
    banner = textwrap.dedent(f"""
        {C_SUCCESS}
         _   _  _____  _   _  _____ ______ _____ _   _  _____
        | | | |/ ____|| \\ | |/ ____||  ____||_   _| \\ | ||  __ \\
        | | | | (___  |  \\| | (___  | |__     | | |  \\| || |__) |
        | | | |\\___ \\ | . ` |\\___ \\ |  __|    | | | . ` ||  _  /
        | |_| |____) || |\\  |____) || |      _| |_| |\\  || | \\ \\
         \\___/|_____/ |_| \\_|_____/ |_|     |_____|_| \\_||_|  \\_\\
        {C_RESET}
    """)
    print(banner)
    print("="*60)
    print("        Professional Project Scaffolding Tool")
    print("="*60)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="A professional scaffolding tool for Project VO2.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              vo2-init           # Safely scaffold the project. Fails if files exist.
              vo2-init --force   # Scaffold, overwriting any existing project files.
              vo2-init --clean   # Remove all scaffolded project files.
        """)
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--force", action="store_true", help="Force overwrite. Deletes existing project structure before creating a new one.")
    group.add_argument("-c", "--clean", action="store_true", help="Clean up. Removes all files and directories associated with the project.")
    args = parser.parse_args()
    display_banner()
    scaffolder = Scaffolder(destination=Path.cwd())
    if args.clean:
        scaffolder.clean()
    else:
        scaffolder.scaffold(force=args.force)

if __name__ == "__main__":
    main()

