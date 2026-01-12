"""
Tavily Web Search Tool

Provides web search capabilities for the LLM agent to look up:
- Tool documentation and usage
- Exploit details and CVE information
- Security research and techniques
- As a last resort when local resources are insufficient
"""

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

# Load environment variables before creating the Tavily instance
load_dotenv()

# Create the Tavily search tool instance
tavily_search = TavilySearch(
    max_results=5,  # Limit results to avoid token limits
    include_answer=False,
    include_raw_content=False,
    search_depth="basic",
    description="Search the web for information about security tools, exploits, CVEs, and penetration testing techniques. Use this as a last resort when local resources are insufficient.",
)


@tool
def web_search(query: str) -> str:
    """
    Search the web using Tavily for security-related information.

    Use this tool as a last resort when you need information that's not available
    locally. Useful for:
    - Tool documentation and command syntax
    - CVE details and exploit information
    - Security research and techniques
    - New tools or methodologies

    Args:
        query: Search query (e.g., "nmap UDP scan syntax", "Apache 2.4.52 CVE-2021-41773")

    Returns:
        Search results formatted as a readable string

    Example:
        web_search("how to use gobuster for directory enumeration")
        web_search("recent vulnerabilities in OpenSSH")
    """
    try:
        # Use the Tavily search tool
        results = tavily_search.invoke({"query": query})

        if not results:
            return "No search results found."

        # Format the results
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "No URL")
            content = result.get("content", "No content")

            formatted_results.append(f"## Result {i}: {title}")
            formatted_results.append(f"**URL**: {url}")
            formatted_results.append(
                f"**Content**: {content[:500]}..."
            )  # Truncate content
            formatted_results.append("")

        return "\n".join(formatted_results)

    except Exception as e:
        return f"Error performing web search: {str(e)}"
