"""
Shell Tool for Executing Arbitrary Commands

Provides a flexible shell execution tool that allows the LLM agent to run
any command on the Kali Linux system with timeout and output truncation.
"""

import subprocess
from typing import Optional, List, Dict

from langchain_core.tools import tool

# Global flag to track if shell commands are enabled
# This will be set by the main application
shell_commands_enabled = False

# Global flag for confirmation mode
# When True, commands are queued instead of executed immediately
confirmation_mode_enabled = False

# Queue of pending commands awaiting confirmation
pending_commands: List[Dict] = []


def set_shell_commands_enabled(enabled: bool):
    """Set whether shell commands are enabled."""
    global shell_commands_enabled
    shell_commands_enabled = enabled


def set_confirmation_mode(enabled: bool):
    """Set whether confirmation mode is enabled."""
    global confirmation_mode_enabled
    confirmation_mode_enabled = enabled


def get_pending_commands() -> List[Dict]:
    """Get the list of pending commands awaiting confirmation."""
    return pending_commands.copy()


def clear_pending_commands():
    """Clear all pending commands."""
    global pending_commands
    pending_commands = []


def add_pending_command(command: str, timeout: int = 300):
    """Add a command to the pending queue."""
    pending_commands.append({"command": command, "timeout": timeout})


def execute_command_directly(command: str, timeout: int = 300) -> str:
    """
    Execute a shell command directly without going through the tool wrapper.
    Used for executing confirmed commands.
    """
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )

        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            if output:
                output += "\n--- STDERR ---\n"
            output += result.stderr

        if len(output) > MAX_OUTPUT_CHARACTERS:
            truncated_output = output[:MAX_OUTPUT_CHARACTERS]
            truncated_output += f"\n\n[Output truncated - showing first {MAX_OUTPUT_CHARACTERS} characters]"
            total_chars = len(output)
            truncated_output += f"\nTotal output length: {total_chars} characters"
            output = truncated_output

        if result.returncode != 0:
            output = f"Command exited with code {result.returncode}\n\n{output}"

        if not output.strip():
            output = "(no output captured from the command)"

        return output

    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds."

    except Exception as e:
        return f"Error executing command: {str(e)}"


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

    # Confirmation mode: queue command instead of executing
    if confirmation_mode_enabled:
        add_pending_command(command, timeout)
        return (
            "🔒 **Command Pending Confirmation**\n\n"
            f"The following command has been queued for your approval:\n\n"
            f"```bash\n{command}\n```\n\n"
            "Please use the confirmation buttons in the UI to approve or cancel this command."
        )

    # Direct execution mode
    output = execute_command_directly(command, timeout)
    
    return (
        "Shell command executed:\n"
        f"`{command}`\n\n"
        "Command output:\n"
        f"{output}"
    )
