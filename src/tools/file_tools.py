"""
File Tools for Reading, Writing, and Listing Files

Provides file system operations for the LLM agent to:
- Read file contents (wordlists, configs, manpages, command outputs)
- Write notes and findings to files
- List directory contents to explore the filesystem
"""

import os
from typing import List

from langchain_core.tools import tool


@tool
def read_file(file_path: str) -> str:
    """
    Read the contents of a file.

    Useful for reading wordlists, configuration files, manpages, or command outputs.
    Returns the full file contents as a string.

    Args:
        file_path: Path to the file to read (e.g., "/usr/share/wordlists/rockyou.txt")

    Returns:
        File contents as a string, or error message if file cannot be read

    Example:
        read_file("/etc/passwd")
        read_file("/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt")
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {file_path}"
    except PermissionError:
        return f"Error: Permission denied reading file: {file_path}"
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"


@tool
def write_file(file_path: str, content: str, overwrite: bool = False) -> str:
    """
    Write content to a file.

    Useful for saving notes, findings, scripts, or command outputs.
    By default, will not overwrite existing files unless overwrite=True.

    Args:
        file_path: Path where to write the file
        content: Content to write to the file
        overwrite: Whether to overwrite existing files (default: False)

    Returns:
        Success message or error message

    Example:
        write_file("/tmp/notes.txt", "Found open port 80 with Apache")
        write_file("/tmp/exploit.py", "#!/usr/bin/env python3\nprint('exploit code')", overwrite=True)
    """
    try:
        if os.path.exists(file_path) and not overwrite:
            return f"Error: File already exists and overwrite=False: {file_path}"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"Successfully wrote {len(content)} characters to {file_path}"

    except PermissionError:
        return f"Error: Permission denied writing to file: {file_path}"
    except Exception as e:
        return f"Error writing to file {file_path}: {str(e)}"


@tool
def list_directory(directory_path: str) -> str:
    """
    List the contents of a directory.

    Useful for exploring the filesystem to find wordlists, tools, or data files.
    Shows both files and subdirectories.

    Args:
        directory_path: Path to the directory to list (e.g., "/usr/share/wordlists")

    Returns:
        Formatted list of directory contents or error message

    Example:
        list_directory("/usr/share/wordlists")
        list_directory("/tmp")
    """
    try:
        if not os.path.exists(directory_path):
            return f"Error: Directory not found: {directory_path}"

        if not os.path.isdir(directory_path):
            return f"Error: Path is not a directory: {directory_path}"

        entries = os.listdir(directory_path)
        if not entries:
            return f"Directory is empty: {directory_path}"

        # Separate directories and files
        dirs = []
        files = []

        for entry in sorted(entries):
            full_path = os.path.join(directory_path, entry)
            if os.path.isdir(full_path):
                dirs.append(f"[DIR]  {entry}/")
            else:
                files.append(f"[FILE] {entry}")

        result = f"Contents of {directory_path}:\n\n"
        if dirs:
            result += "Directories:\n" + "\n".join(dirs) + "\n\n"
        if files:
            result += "Files:\n" + "\n".join(files)

        return result

    except PermissionError:
        return f"Error: Permission denied listing directory: {directory_path}"
    except Exception as e:
        return f"Error listing directory {directory_path}: {str(e)}"