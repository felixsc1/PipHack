# PipHack - LLM Powered Penetration Testing Tool

<p align="center">
  <img src="assets/piphack_logo.png" alt="PipHack Logo" width="256">
</p>

PipHack is an intelligent penetration testing assistant that combines the power of Large Language Models with Kali Linux command-line tools to help ethical hackers perform comprehensive security assessments.

This is a learning project that is still in early development.

## Features

- 💻 **Shell-Based Pentesting**: LLM-guided execution of arbitrary Kali Linux commands with user confirmation
- 📁 **File Operations**: Read, write, and list files to manage notes, wordlists, and results
- 📋 **Context-Aware Assistance**: Uses a configurable context file for wordlists, commands, and target notes
- 🔍 **Web Research**: Tavily-powered web search for documentation, CVEs, and exploit information
- 🤖 **AI-Powered Analysis**: GPT-5 powered agent that understands context and provides recommendations
- 💬 **Interactive Chat**: Streamlit-based chat interface for natural interaction

## Architecture

- **Frontend**: Streamlit web interface
- **Core Logic**: LangGraph state management and agent orchestration
- **Tools**: Shell execution, file tools, and Tavily web search
- **Context**: User-editable `config/context.md` loaded into the system prompt
- **LLM**: OpenAI GPT-5 for intelligent analysis

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key
- Kali Linux with common pentesting tools available on the system PATH

### Setup

1. **Clone and navigate to the project**:

   ```bash
   git clone <repository-url>
   cd PipHack
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers** (for web enumeration):

   ```bash
   playwright install
   ```

   Note: It might complain that there are missing dependencies. You can ignore this.

5. **Configure environment**:
   ```bash
   # Create a .env file (optionally based on env_example.txt)
   # and add your API keys
   ```

## Configuration

### Environment Variables

Create a `.env` file with at least the following variables:

```env
# OpenAI API Key for the LLM
OPENAI_API_KEY=your_openai_api_key_here

# Tavily API Key for web search (optional but recommended)
TAVILY_API_KEY=your_tavily_api_key_here
```

## Usage

### Starting the Application

```bash
streamlit run src/main.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Basic Workflow

1. **Start a conversation**: Ask PipHack to perform recon or analysis on a target

   ```
   "Scan 192.168.1.100 for open ports"
   ```

2. **Review proposed commands**: PipHack will suggest one or more Kali commands (e.g. `nmap`, `gobuster`, `searchsploit`) and display them with a confirmation step in the UI.

3. **Confirm execution**: You decide which commands to run; on confirmation, PipHack executes them on the Kali host and ingests the results.

4. **Iterate**: Ask follow-up questions, refine scans, and pivot based on findings.

### Example Commands

- "Scan 192.168.1.1"
- "What services are running on 10.0.0.1?"
- "Check for exploits for Apache 2.4.52"
- "Analyze the website at http://192.168.1.100"
- "Search for vulnerabilities in SSH"

## Tooling Overview

- **Shell Execution**: Run arbitrary Kali Linux commands proposed by the agent, with explicit user confirmation.
- **File Tools**: Read existing files (e.g. wordlists, config, output), write notes, and list directories.
- **Tavily Web Search**: Look up documentation, CVEs, exploit details, and tool usage.
- **Context File**: `config/context.md` holds wordlists, common commands, tool locations, and target-specific notes that the agent can consult.

## Security & Ethics

⚠️ **Important**: PipHack is designed for ethical hacking only. Always ensure you have explicit permission to test any systems. Unauthorized testing may be illegal.

- Only scan networks and systems you own or have permission to assess
- Respect all applicable laws and regulations
- Use the tool responsibly for defensive security purposes

## Future Enhancements

- Automated vulnerability exploitation (with user confirmation)
- Advanced web vulnerability scanning (XSS, CSRF, etc.)
- Report generation and export
- Integration with additional security tools and workflows
- Multi-target assessment workflows
