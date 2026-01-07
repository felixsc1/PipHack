"""
Nmap Tool for Port Scanning and Service Detection
"""

import json
import os
import subprocess
import tempfile
from typing import Optional

from dotenv import load_dotenv
from langchain_core.tools import tool

# Load environment variables
load_dotenv()

MOCK_MODE = os.getenv("MOCK_MODE", "False").lower() == "true"


def run_nmap_scan(target: str) -> str:
    """
    Run an nmap scan on the target IP or hostname.

    Args:
        target: IP address or hostname to scan

    Returns:
        JSON string containing scan results
    """
    if MOCK_MODE:
        return get_mock_nmap_data(target)

    try:
        # Create a temporary file for output
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
            output_file = temp_file.name

        # Run nmap with service version detection and JSON output
        cmd = ["nmap", "-sV", "-oJ", output_file, target]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            return json.dumps({
                "error": f"Nmap scan failed: {result.stderr}",
                "target": target
            })

        # Read the JSON output
        with open(output_file, 'r') as f:
            nmap_output = f.read()

        # Clean up temp file
        os.unlink(output_file)

        return nmap_output

    except subprocess.TimeoutExpired:
        return json.dumps({
            "error": "Nmap scan timed out",
            "target": target
        })
    except Exception as e:
        return json.dumps({
            "error": f"Error running nmap: {str(e)}",
            "target": target
        })


def get_mock_nmap_data(target: str) -> str:
    """
    Return mock nmap data for development purposes.

    Args:
        target: The target being scanned (used for display)

    Returns:
        JSON string simulating nmap output
    """
    mock_data = {
        "nmaprun": {
            "scanner": "nmap",
            "args": f"nmap -sV -oJ /tmp/mock_output.json {target}",
            "start": "1704567890",
            "version": "7.94",
            "xmloutputversion": "1.05"
        },
        "scaninfo": {
            "type": "syn",
            "protocol": "tcp",
            "numservices": "1000",
            "services": "1-1000"
        },
        "verbose": {
            "level": "0"
        },
        "debugging": {
            "level": "0"
        },
        "host": {
            "starttime": "1704567890",
            "endtime": "1704567905",
            "status": {
                "state": "up",
                "reason": "arp-response",
                "reason_ttl": "0"
            },
            "address": {
                "addr": target,
                "addrtype": "ipv4"
            },
            "hostnames": {
                "hostname": {
                    "name": target,
                    "type": "PTR"
                }
            },
            "ports": {
                "port": [
                    {
                        "protocol": "tcp",
                        "portid": "22",
                        "state": {
                            "state": "open",
                            "reason": "syn-ack",
                            "reason_ttl": "64"
                        },
                        "service": {
                            "name": "ssh",
                            "product": "OpenSSH",
                            "version": "8.9p1 Ubuntu 3ubuntu0.6",
                            "extrainfo": "Ubuntu Linux; protocol 2.0",
                            "ostype": "Linux",
                            "method": "probed",
                            "conf": "10"
                        }
                    },
                    {
                        "protocol": "tcp",
                        "portid": "80",
                        "state": {
                            "state": "open",
                            "reason": "syn-ack",
                            "reason_ttl": "64"
                        },
                        "service": {
                            "name": "http",
                            "product": "Apache httpd",
                            "version": "2.4.52",
                            "extrainfo": "(Ubuntu)",
                            "method": "probed",
                            "conf": "10"
                        }
                    }
                ]
            }
        }
    }

    return json.dumps(mock_data, indent=2)


@tool
def nmap_scan(target: str) -> str:
    """
    Perform an nmap scan on a target IP or hostname to discover open ports and running services.

    This tool will run nmap with service version detection (-sV) and return detailed information
    about discovered services. Results are returned in JSON format for easy parsing.

    Args:
        target: IP address or hostname to scan (e.g., "192.168.1.1" or "example.com")

    Returns:
        JSON string containing nmap scan results including open ports and service information

    Example:
        nmap_scan("192.168.1.100")
    """
    return run_nmap_scan(target)