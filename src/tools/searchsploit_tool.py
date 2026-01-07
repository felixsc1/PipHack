"""
SearchSploit Tool for Finding Exploits in Exploit-DB
"""

import os
import subprocess
from typing import Optional

from dotenv import load_dotenv
from langchain_core.tools import tool

# Load environment variables
load_dotenv()

MOCK_MODE = os.getenv("MOCK_MODE", "False").lower() == "true"


def run_searchsploit(service: str, version: Optional[str] = None) -> str:
    """
    Search for exploits in Exploit-DB using searchsploit.

    Args:
        service: Service name (e.g., "apache", "ssh", "mysql")
        version: Optional version string

    Returns:
        String containing search results or error message
    """
    if MOCK_MODE:
        return get_mock_searchsploit_data(service, version)

    try:
        # Build the search query
        query_parts = [service]
        if version:
            query_parts.append(version)

        query = " ".join(query_parts)

        # Run searchsploit
        cmd = ["searchsploit", query]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            output = result.stdout.strip()
            if not output:
                return f"No exploits found for {query}"
            return f"Exploit search results for '{query}':\n\n{output}"
        else:
            return f"Error searching for exploits: {result.stderr}"

    except subprocess.TimeoutExpired:
        return "SearchSploit search timed out"
    except Exception as e:
        return f"Error running searchsploit: {str(e)}"


def get_mock_searchsploit_data(service: str, version: Optional[str] = None) -> str:
    """
    Return mock searchsploit data for development purposes.

    Args:
        service: Service name being searched
        version: Optional version string

    Returns:
        String simulating searchsploit output
    """
    query = f"{service} {version}" if version else service

    # Mock data based on common services
    mock_exploits = {
        "apache": [
            "Apache 2.4.52 - Remote Code Execution",
            "Apache HTTP Server 2.4.52 - Denial of Service",
            "Apache mod_cgi - 'Shellshock' Remote Code Execution"
        ],
        "ssh": [
            "OpenSSH 8.9p1 - Remote Code Execution",
            "OpenSSH 8.9p1 - User Enumeration",
            "OpenSSH < 7.4 - 'UsePrivilegeSeparation Disabled' Privilege Escalation"
        ],
        "mysql": [
            "MySQL 5.7.35 - Remote Code Execution",
            "MySQL Authentication Bypass",
            "MySQL UDF - Dynamic Library Code Execution"
        ],
        "http": [
            "Apache HTTP Server 2.4.52 - Remote Code Execution",
            "Nginx 1.20.1 - Remote Code Execution",
            "HTTP Server - Directory Traversal"
        ]
    }

    # Get exploits for the service (case insensitive)
    exploits = mock_exploits.get(service.lower(), [])

    if not exploits:
        return f"No exploits found for {query}"

    # Format output similar to real searchsploit
    output_lines = [
        f"Exploit search results for '{query}':",
        "",
        "--------------------------------------------------------------------------------",
        "|  Title                                                                       |",
        "--------------------------------------------------------------------------------"
    ]

    for i, exploit in enumerate(exploits, 1):
        output_lines.append(f"|  {exploit:<72} |")

    output_lines.extend([
        "--------------------------------------------------------------------------------",
        "",
        f"Found {len(exploits)} exploits for {query}",
        "",
        "To view exploit details, run: searchsploit -x <exploit_number>",
        "To download exploit, run: searchsploit -m <exploit_number>"
    ])

    return "\n".join(output_lines)


@tool
def search_exploit(service: str, version: Optional[str] = None) -> str:
    """
    Search for known exploits in Exploit-DB using searchsploit.

    This tool searches the local Exploit-DB database for known vulnerabilities
    and exploits related to a specific service and version. It helps identify
    potential attack vectors for discovered services.

    Args:
        service: Service name to search for (e.g., "apache", "ssh", "mysql")
        version: Optional version string for more specific results

    Returns:
        String containing exploit search results or error message

    Example:
        search_exploit("apache", "2.4.52")
        search_exploit("ssh")
    """
    return run_searchsploit(service, version)