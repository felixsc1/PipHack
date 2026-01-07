"""
Web Enumeration Tool using Playwright for Web Application Analysis
"""

import json
import os
from typing import Optional

from dotenv import load_dotenv
from langchain_core.tools import tool

# Load environment variables
load_dotenv()

MOCK_MODE = os.getenv("MOCK_MODE", "False").lower() == "true"

# Import playwright conditionally to avoid import errors in mock mode
if not MOCK_MODE:
    try:
        from playwright.sync_api import sync_playwright, Page, Browser
    except ImportError:
        print("Warning: Playwright not installed. Install with: pip install playwright && playwright install")
        sync_playwright = None
else:
    sync_playwright = None


def enumerate_web_app(url: str) -> str:
    """
    Enumerate a web application for potential vulnerabilities and attack vectors.

    Args:
        url: URL of the web application to enumerate

    Returns:
        JSON string containing enumeration results
    """
    if MOCK_MODE:
        return get_mock_web_enum_data(url)

    if sync_playwright is None:
        return json.dumps({
            "error": "Playwright not available. Please install with: pip install playwright && playwright install",
            "url": url
        })

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            page = context.new_page()

            # Navigate to the URL
            try:
                page.goto(url, timeout=10000)
                page.wait_for_load_state('networkidle', timeout=5000)
            except Exception as e:
                return json.dumps({
                    "error": f"Failed to load page: {str(e)}",
                    "url": url
                })

            # Analyze the page
            analysis_results = analyze_page(page, url)

            browser.close()
            return json.dumps(analysis_results, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Error during web enumeration: {str(e)}",
            "url": url
        })


def analyze_page(page, url: str) -> dict:
    """
    Analyze a web page for potential vulnerabilities and attack vectors.

    Args:
        page: Playwright page object
        url: Original URL

    Returns:
        Dictionary containing analysis results
    """
    results = {
        "url": url,
        "title": page.title(),
        "forms": [],
        "inputs": [],
        "links": [],
        "potential_vulnerabilities": [],
        "recommendations": []
    }

    # Extract forms
    forms = page.query_selector_all('form')
    for i, form in enumerate(forms):
        form_info = {
            "index": i,
            "action": form.get_attribute('action') or "",
            "method": form.get_attribute('method') or "GET",
            "inputs": []
        }

        # Extract inputs within this form
        inputs = form.query_selector_all('input, textarea, select')
        for input_elem in inputs:
            input_info = {
                "type": input_elem.get_attribute('type') or "text",
                "name": input_elem.get_attribute('name') or "",
                "id": input_elem.get_attribute('id') or "",
                "placeholder": input_elem.get_attribute('placeholder') or ""
            }
            form_info["inputs"].append(input_info)

        results["forms"].append(form_info)

    # Extract all input elements (not just in forms)
    all_inputs = page.query_selector_all('input, textarea, select')
    for input_elem in all_inputs:
        input_info = {
            "type": input_elem.get_attribute('type') or "text",
            "name": input_elem.get_attribute('name') or "",
            "id": input_elem.get_attribute('id') or "",
            "placeholder": input_elem.get_attribute('placeholder') or ""
        }
        results["inputs"].append(input_info)

    # Extract links (potential for directory traversal, etc.)
    links = page.query_selector_all('a[href]')
    for link in links[:20]:  # Limit to first 20 links
        href = link.get_attribute('href')
        if href and not href.startswith(('http', 'mailto:', 'tel:', '#')):
            results["links"].append(href)

    # Analyze for potential vulnerabilities
    vulnerabilities = []

    # Check for login forms
    for form in results["forms"]:
        if any(inp.get('type') in ['password', 'email'] or
               'login' in (inp.get('name', '').lower() + inp.get('id', '').lower() + inp.get('placeholder', '').lower())
               for inp in form["inputs"]):
            vulnerabilities.append({
                "type": "login_form",
                "severity": "info",
                "description": "Login form detected - potential for brute force attacks",
                "form_index": form["index"]
            })

    # Check for file upload forms
    for form in results["forms"]:
        if any(inp.get('type') == 'file' for inp in form["inputs"]):
            vulnerabilities.append({
                "type": "file_upload",
                "severity": "medium",
                "description": "File upload functionality detected - check for upload restrictions",
                "form_index": form["index"]
            })

    # Check for search forms (potential SQL injection)
    for form in results["forms"]:
        if any('search' in (inp.get('name', '').lower() + inp.get('placeholder', '').lower())
               for inp in form["inputs"]):
            vulnerabilities.append({
                "type": "search_form",
                "severity": "medium",
                "description": "Search functionality detected - potential for injection attacks",
                "form_index": form["index"]
            })

    # Check for exposed admin panels or sensitive paths
    sensitive_paths = ['admin', 'administrator', 'login', 'auth', 'dashboard', 'wp-admin', 'phpmyadmin']
    for link in results["links"]:
        link_lower = link.lower()
        for path in sensitive_paths:
            if path in link_lower:
                vulnerabilities.append({
                    "type": "exposed_path",
                    "severity": "low",
                    "description": f"Potentially sensitive path exposed: {link}",
                    "path": link
                })
                break

    results["potential_vulnerabilities"] = vulnerabilities

    # Generate recommendations
    recommendations = []
    if vulnerabilities:
        recommendations.append("Review identified forms and inputs for proper validation")
        recommendations.append("Test for common web vulnerabilities (XSS, CSRF, SQL injection)")
        if any(v["type"] == "login_form" for v in vulnerabilities):
            recommendations.append("Consider implementing rate limiting on login endpoints")
        if any(v["type"] == "file_upload" for v in vulnerabilities):
            recommendations.append("Implement proper file type and size restrictions for uploads")

    results["recommendations"] = recommendations

    return results


def get_mock_web_enum_data(url: str) -> str:
    """
    Return mock web enumeration data for development purposes.

    Args:
        url: URL being enumerated

    Returns:
        JSON string simulating web enumeration results
    """
    mock_data = {
        "url": url,
        "title": "Mock Web Application",
        "forms": [
            {
                "index": 0,
                "action": "/login",
                "method": "POST",
                "inputs": [
                    {
                        "type": "text",
                        "name": "username",
                        "id": "username",
                        "placeholder": "Enter username"
                    },
                    {
                        "type": "password",
                        "name": "password",
                        "id": "password",
                        "placeholder": "Enter password"
                    }
                ]
            }
        ],
        "inputs": [
            {
                "type": "text",
                "name": "username",
                "id": "username",
                "placeholder": "Enter username"
            },
            {
                "type": "password",
                "name": "password",
                "id": "password",
                "placeholder": "Enter password"
            }
        ],
        "links": [
            "/admin",
            "/dashboard",
            "/logout"
        ],
        "potential_vulnerabilities": [
            {
                "type": "login_form",
                "severity": "info",
                "description": "Login form detected - potential for brute force attacks",
                "form_index": 0
            },
            {
                "type": "exposed_path",
                "severity": "low",
                "description": "Potentially sensitive path exposed: /admin",
                "path": "/admin"
            }
        ],
        "recommendations": [
            "Review identified forms and inputs for proper validation",
            "Test for common web vulnerabilities (XSS, CSRF, SQL injection)",
            "Consider implementing rate limiting on login endpoints"
        ]
    }

    return json.dumps(mock_data, indent=2)


@tool
def enumerate_web_application(url: str) -> str:
    """
    Enumerate a web application for potential vulnerabilities and attack vectors.

    This tool uses browser automation to analyze a web application and identify:
    - Forms and input fields
    - Potential login forms
    - File upload functionality
    - Exposed sensitive paths
    - Other potential attack vectors

    Args:
        url: Full URL of the web application to enumerate (e.g., "http://192.168.1.100" or "https://example.com")

    Returns:
        JSON string containing detailed enumeration results including forms, vulnerabilities, and recommendations

    Example:
        enumerate_web_application("http://192.168.1.100")
    """
    return enumerate_web_app(url)