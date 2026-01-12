"""
Shell Tool for Executing Arbitrary Commands

Provides a flexible shell execution tool that allows the LLM agent to run
any command on the Kali Linux system with timeout and output truncation.
"""

import subprocess
from typing import Optional

from langchain_core.tools import tool

# Global flag to track if shell commands are enabled
# This will be set by the main application
shell_commands_enabled = False


def set_shell_commands_enabled(enabled: bool):
    """Set whether shell commands are enabled."""
    global shell_commands_enabled
    shell_commands_enabled = enabled


MAX_OUTPUT_CHARACTERS = 30000


@tool
def execute_shell_command(command: str, timeout: int = 300) -> str:
    """
    Execute a shell command on the system with timeout and output truncation.

    This tool allows running arbitrary shell commands on the Kali Linux system.
    Commands are executed with a configurable timeout and large outputs are
    automatically truncated to prevent UI issues.

    IMPORTANT: Shell command execution must be enabled in the UI before this tool
    will execute any commands. If disabled, it will return a safety message.

    Args:
        command: The shell command to execute (e.g., "nmap -sV 192.168.1.1")
        timeout: Maximum execution time in seconds (default: 300)

    Returns:
        Command output as a string, truncated if too long, or safety message if disabled

    Example:
        execute_shell_command("ls -la /usr/share/wordlists")
        execute_shell_command("nmap -sV -p- 192.168.1.100", timeout=600)
    """
    # Safety check: ensure shell commands are enabled
    if not shell_commands_enabled:
        return (
            "❌ **Shell Command Execution Disabled**\n\n"
            "For safety reasons, shell command execution is currently disabled. "
            "Please enable it in the sidebar configuration before PipHack can execute commands.\n\n"
            f"Command that would have been executed: `{command}`"
        )
    try:
        # Execute the command
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )

        # Combine stdout and stderr
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            if output:
                output += "\n--- STDERR ---\n"
            output += result.stderr

        # Truncate if too long
        if len(output) > MAX_OUTPUT_CHARACTERS:
            truncated_output = output[:MAX_OUTPUT_CHARACTERS]
            truncated_output += f"\n\n[Output truncated - showing first {MAX_OUTPUT_CHARACTERS} characters]"

            # Count total characters for info
            total_chars = len(output)
            truncated_output += f"\nTotal output length: {total_chars} characters"
            output = truncated_output

        # Add exit code info if non-zero
        if result.returncode != 0:
            output = f"Command exited with code {result.returncode}\n\n{output}"

        # Ensure there is at least some output text
        if not output.strip():
            output = "(no output captured from the command)"

        # Always return the exact command that was executed along with its output
        return (
            "Shell command executed:\n"
            f"`{command}`\n\n"
            "Command output:\n"
            f"{output}"
        )

    except subprocess.TimeoutExpired:
        return (
            "Shell command executed:\n"
            f"`{command}`\n\n"
            f"Command timed out after {timeout} seconds."
        )

    except Exception as e:
        return (
            "Shell command executed:\n"
            f"`{command}`\n\n"
            f"Error executing command: {str(e)}"
        )
