# PipHack - LLM Powered Penetration Testing Tool

<p align="center">
  <img src="assets/piphack_logo.png" alt="PipHack Logo" width="256">
</p>


PipHack is an intelligent penetration testing assistant that combines the power of Large Language Models with specialized security tools to help ethical hackers perform comprehensive security assessments.

This is a learning project that is still in early development.

## Features

- 🔍 **Network Scanning**: Automated nmap scans for port discovery and service enumeration
- 💀 **Exploit Research**: SearchSploit integration for finding known vulnerabilities
- 🌐 **Web Application Analysis**: Playwright-powered web enumeration and vulnerability detection
- 🤖 **AI-Powered Analysis**: GPT-5 powered agent that understands context and provides recommendations
- 🧪 **Mock Mode**: Development mode with simulated outputs for testing on Windows
- 💬 **Interactive Chat**: Streamlit-based chat interface for natural interaction

## Architecture

- **Frontend**: Streamlit web interface
- **Core Logic**: LangGraph state management and agent orchestration
- **Tools**: Custom LangChain tools wrapping security utilities
- **LLM**: OpenAI GPT-5 for intelligent analysis

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key
- (For Kali Linux) nmap, searchsploit, and other pentesting tools

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
   cp .env.example .env
   # Edit .env file with your OpenAI API key
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI API Key for the LLM
OPENAI_API_KEY=your_openai_api_key_here

# Mock mode for development on Windows (True) or real execution on Kali (False)
MOCK_MODE=True
```

### Mode Settings

- **Mock Mode (`MOCK_MODE=True`)**: Uses simulated tool outputs. Perfect for development and testing on Windows.
- **Real Mode (`MOCK_MODE=False`)**: Uses actual security tools. Required for Kali Linux deployment.

## Usage

### Starting the Application

```bash
streamlit run src/main.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Basic Workflow

1. **Start a conversation**: Ask PipHack to scan a target

   ```
   "Scan 192.168.1.100 for open ports"
   ```

2. **Analyze results**: The AI will automatically run nmap and present findings

3. **Check for exploits**: For discovered services, PipHack will search for known vulnerabilities

   ```
   "Check for exploits for the services found"
   ```

4. **Web analysis**: If web services are detected, analyze the web application
   ```
   "Analyze the web application on port 80"
   ```

### Example Commands

- "Scan 192.168.1.1"
- "What services are running on 10.0.0.1?"
- "Check for exploits for Apache 2.4.52"
- "Analyze the website at http://192.168.1.100"
- "Search for vulnerabilities in SSH"

## Tool Details

### Nmap Tool

- Performs comprehensive port scanning with service version detection
- Returns structured JSON output with all discovered services
- Automatically identifies potential web services for further analysis

### SearchSploit Tool

- Searches local Exploit-DB for known vulnerabilities
- Provides exploit titles, descriptions, and usage instructions
- Helps prioritize vulnerabilities by severity

### Web Enumeration Tool

- Uses browser automation to analyze web applications
- Detects forms, login pages, file uploads, and potential vulnerabilities
- Identifies common attack vectors like SQL injection points

## Development vs Production

### Windows Development (Mock Mode)

- Set `MOCK_MODE=True` in your `.env` file
- All tools return simulated outputs
- Perfect for UI testing and logic verification
- No security tools required

### Kali Linux Production (Real Mode)

- Set `MOCK_MODE=False` in your `.env` file
- Requires actual security tools:
  - `nmap` for network scanning
  - `searchsploit` for exploit database
  - `playwright` for web analysis
- Full penetration testing capabilities

## Security & Ethics

⚠️ **Important**: PipHack is designed for ethical hacking only. Always ensure you have explicit permission to test any systems. Unauthorized testing may be illegal.

- Only scan networks and systems you own or have permission to assess
- Respect all applicable laws and regulations
- Use the tool responsibly for defensive security purposes


## Future Enhancements

- Automated vulnerability exploitation (with user confirmation)
- Advanced web vulnerability scanning (XSS, CSRF, etc.)
- Report generation and export
- Integration with additional security tools
- Multi-target assessment workflows
