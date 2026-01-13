"""
PipHack - LLM Powered Penetration Testing Tool
Main Streamlit application entry point
"""

import os
import json
from typing import Dict, List

import streamlit as st
from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackHandler

from agents.pentest_agent import run_pentest_query, pentest_agent
from tools.shell_tool import (
    set_shell_commands_enabled,
    set_confirmation_mode,
    get_pending_commands,
    clear_pending_commands,
    execute_command_directly,
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="PipHack - Penetration Testing Assistant",
    page_icon="🔒",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "scan_results" not in st.session_state:
    st.session_state.scan_results = {}

if "current_target" not in st.session_state:
    st.session_state.current_target = ""

if "shell_commands_enabled" not in st.session_state:
    st.session_state.shell_commands_enabled = False

if "confirmation_mode" not in st.session_state:
    st.session_state.confirmation_mode = True  # Enabled by default for safety

if "command_results" not in st.session_state:
    st.session_state.command_results = []  # Store results from confirmed commands


def display_message(message: Dict):
    """Display a message in the chat interface."""
    role = message["role"]
    content = message["content"]

    if role == "user":
        with st.chat_message("user"):
            st.write(content)
    else:
        with st.chat_message("assistant"):
            # Try to format JSON content nicely
            if content.strip().startswith('{') or content.strip().startswith('['):
                try:
                    parsed_json = json.loads(content)
                    if isinstance(parsed_json, dict):
                        # Check if it's nmap output
                        if "nmaprun" in parsed_json:
                            display_nmap_results(parsed_json)
                        # Check if it's web enumeration output
                        elif "forms" in parsed_json or "potential_vulnerabilities" in parsed_json:
                            display_web_enum_results(parsed_json)
                        else:
                            st.json(parsed_json)
                    else:
                        st.json(parsed_json)
                except json.JSONDecodeError:
                    st.write(content)
            else:
                st.write(content)


def display_nmap_results(nmap_data: Dict):
    """Display formatted nmap scan results."""
    st.subheader("🔍 Nmap Scan Results")

    if "error" in nmap_data:
        st.error(f"Scan Error: {nmap_data['error']}")
        return

    # Display basic info
    if "host" in nmap_data:
        host = nmap_data["host"]
        if isinstance(host, dict):
            addr = host.get("address", {}).get("addr", "Unknown")
            st.info(f"Target: {addr}")

            # Display ports
            if "ports" in host and "port" in host["ports"]:
                ports = host["ports"]["port"]
                if isinstance(ports, list):
                    st.subheader("Open Ports & Services")
                    for port in ports:
                        if isinstance(port, dict) and port.get("state", {}).get("state") == "open":
                            port_id = port.get("portid", "Unknown")
                            service = port.get("service", {})
                            service_name = service.get("name", "Unknown")
                            product = service.get("product", "")
                            version = service.get("version", "")

                            service_info = f"{service_name}"
                            if product:
                                service_info += f" ({product}"
                                if version:
                                    service_info += f" {version}"
                                service_info += ")"

                            st.success(f"Port {port_id}: {service_info}")
                else:
                    st.write("No open ports found or unexpected data format")
        else:
            st.write("Unexpected host data format")
    else:
        st.write("No host information available")


def display_pending_commands():
    """Display pending commands with confirm/cancel buttons."""
    pending = get_pending_commands()
    
    if not pending:
        return False
    
    st.markdown("---")
    st.subheader("🔒 Commands Awaiting Confirmation")
    
    for i, cmd_info in enumerate(pending):
        command = cmd_info["command"]
        timeout = cmd_info.get("timeout", 300)
        
        # Display the command in a styled box
        st.markdown(f"""
        <div style="background-color: #1e1e1e; border: 1px solid #ffa500; border-radius: 8px; padding: 16px; margin: 10px 0;">
            <p style="color: #ffa500; font-weight: bold; margin-bottom: 8px;">📋 Command #{i+1}</p>
            <code style="background-color: #2d2d2d; color: #00ff00; padding: 8px; display: block; border-radius: 4px; font-family: monospace;">{command}</code>
            <p style="color: #888; font-size: 12px; margin-top: 8px;">Timeout: {timeout}s</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create confirm/cancel buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button(f"✅ Confirm", key=f"confirm_{i}", type="primary"):
                # Execute the command
                with st.spinner(f"Executing command..."):
                    output = execute_command_directly(command, timeout)
                
                # Store the result
                result_message = f"**Executed Command:**\n```bash\n{command}\n```\n\n**Output:**\n```\n{output}\n```"
                st.session_state.command_results.append({
                    "command": command,
                    "output": output
                })
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result_message
                })
                
                # Clear this pending command and rerun
                clear_pending_commands()
                st.rerun()
        
        with col2:
            if st.button(f"❌ Cancel", key=f"cancel_{i}"):
                # Add cancellation message to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"⚠️ Command cancelled by user:\n```bash\n{command}\n```"
                })
                
                clear_pending_commands()
                st.rerun()
    
    # Add a "Confirm All" and "Cancel All" if multiple commands
    if len(pending) > 1:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("✅ Confirm All", type="primary"):
                results = []
                for cmd_info in pending:
                    command = cmd_info["command"]
                    timeout = cmd_info.get("timeout", 300)
                    with st.spinner(f"Executing: {command[:50]}..."):
                        output = execute_command_directly(command, timeout)
                    results.append(f"**Command:**\n```bash\n{command}\n```\n\n**Output:**\n```\n{output}\n```")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "\n\n---\n\n".join(results)
                })
                clear_pending_commands()
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel All"):
                cancelled_cmds = "\n".join([f"- `{c['command']}`" for c in pending])
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"⚠️ All commands cancelled by user:\n{cancelled_cmds}"
                })
                clear_pending_commands()
                st.rerun()
    
    st.markdown("---")
    return True


def display_web_enum_results(web_data: Dict):
    """Display formatted web enumeration results."""
    st.subheader("🌐 Web Application Analysis")

    if "error" in web_data:
        st.error(f"Enumeration Error: {web_data['error']}")
        return

    # Display basic info
    url = web_data.get("url", "Unknown")
    title = web_data.get("title", "No title")
    st.info(f"URL: {url}")
    st.info(f"Title: {title}")

    # Display forms
    forms = web_data.get("forms", [])
    if forms:
        st.subheader("📝 Forms Found")
        for i, form in enumerate(forms):
            with st.expander(f"Form {i+1}: {form.get('action', 'No action')}"):
                st.write(f"Method: {form.get('method', 'GET')}")
                st.write(f"Action: {form.get('action', '')}")
                inputs = form.get("inputs", [])
                if inputs:
                    st.write("Inputs:")
                    for inp in inputs:
                        st.write(f"- {inp.get('type', 'text')}: {inp.get('name', '')} (ID: {inp.get('id', '')})")

    # Display vulnerabilities
    vulnerabilities = web_data.get("potential_vulnerabilities", [])
    if vulnerabilities:
        st.subheader("⚠️ Potential Vulnerabilities")
        for vuln in vulnerabilities:
            severity_colors = {
                "low": "🟢",
                "medium": "🟡",
                "high": "🔴",
                "critical": "🔴",
                "info": "🔵"
            }
            color = severity_colors.get(vuln.get("severity", "info").lower(), "🔵")
            st.warning(f"{color} {vuln.get('type', 'Unknown')}: {vuln.get('description', '')}")

    # Display recommendations
    recommendations = web_data.get("recommendations", [])
    if recommendations:
        st.subheader("💡 Recommendations")
        for rec in recommendations:
            st.info(f"• {rec}")


def main():
    st.title("🔒 PipHack - LLM Powered Pentesting Tool")
    st.markdown("*Ethical hacking assistant for comprehensive security assessments*")

    # Sidebar configuration
    with st.sidebar:
        # Display logo at the top
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "piphack_logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width='stretch')
            st.markdown("---")
        
        st.header("⚙️ Configuration")

        # Shell command safety toggle
        st.subheader("🛡️ Safety Settings")
        shell_enabled = st.checkbox("Enable Shell Command Execution", value=st.session_state.shell_commands_enabled,
                                   help="Must be enabled to allow PipHack to execute shell commands on the system")

        # Update both session state and tool flag
        if shell_enabled != st.session_state.shell_commands_enabled:
            st.session_state.shell_commands_enabled = shell_enabled
            set_shell_commands_enabled(shell_enabled)

        if st.session_state.shell_commands_enabled:
            st.success("✅ Shell commands enabled - PipHack can now execute system commands")
        else:
            st.warning("⚠️ Shell commands disabled - Enable to allow command execution")

        # Confirmation mode toggle
        confirmation_enabled = st.checkbox(
            "Require Command Confirmation",
            value=st.session_state.confirmation_mode,
            help="When enabled, PipHack will ask for your approval before executing shell commands"
        )

        if confirmation_enabled != st.session_state.confirmation_mode:
            st.session_state.confirmation_mode = confirmation_enabled
            set_confirmation_mode(confirmation_enabled)

        if st.session_state.confirmation_mode:
            st.info("🔐 Confirmation mode - Commands require approval before execution")
        else:
            st.warning("⚡ Auto-execute mode - Commands run immediately without confirmation")

        st.success("🔧 **Live Mode** - Executing Kali Linux commands")

        st.divider()

        # Current target
        if st.session_state.current_target:
            st.subheader("🎯 Current Target")
            st.info(st.session_state.current_target)

        # Available tools
        st.subheader("🛠️ Available Tools")
        tools = [
            "💻 Shell Execution - Run any Kali Linux command",
            "📁 File Operations - Read/write/list files",
            "🔍 Web Search - Research tools and vulnerabilities",
            "📋 Context File - Custom wordlists and commands"
        ]
        for tool in tools:
            st.write(f"• {tool}")

        st.caption("*Tools execute real commands on the Kali Linux system*")

        st.divider()

        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.scan_results = {}
            st.session_state.current_target = ""
            st.session_state.command_results = []
            clear_pending_commands()
            st.rerun()

    # Initialize confirmation mode on startup
    set_confirmation_mode(st.session_state.confirmation_mode)
    set_shell_commands_enabled(st.session_state.shell_commands_enabled)

    # Main chat interface
    st.header("💬 Chat with PipHack")

    # Display chat history
    for message in st.session_state.messages:
        display_message(message)

    # Display any pending commands with confirmation buttons
    has_pending = display_pending_commands()

    # Chat input (disabled if there are pending commands)
    if has_pending:
        st.info("⏳ Please confirm or cancel the pending commands above before continuing.")
        st.chat_input("Waiting for command confirmation...", disabled=True)
    elif prompt := st.chat_input("Ask PipHack to scan a target, search for exploits, or analyze web applications..."):
        # Add user message to history
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)

        # Display user message
        display_message(user_message)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("PipHack is analyzing..."):
                try:
                    # Extract target from prompt if mentioned
                    if "scan" in prompt.lower() or "nmap" in prompt.lower():
                        # Simple target extraction - could be improved
                        words = prompt.split()
                        for word in words:
                            if word.replace(".", "").replace("/", "").isalnum() and ("." in word or "/" in word):
                                st.session_state.current_target = word
                                break


                    # Run the query through the agent
                    result = run_pentest_query(prompt, st.session_state.current_target)

                    # Extract the last message from the result
                    if "messages" in result and result["messages"]:
                        last_message = result["messages"][-1]
                        if hasattr(last_message, 'content'):
                            ai_content = last_message.content
                        else:
                            ai_content = str(last_message)
                    else:
                        ai_content = "I apologize, but I encountered an error processing your request."

                    # Add AI response to history
                    ai_message = {"role": "assistant", "content": ai_content}
                    st.session_state.messages.append(ai_message)

                    # Display AI response
                    display_message(ai_message)

                    # Check if there are pending commands - rerun to show confirmation UI
                    if get_pending_commands():
                        st.rerun()

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    error_message = {"role": "assistant", "content": f"I encountered an error: {str(e)}"}
                    st.session_state.messages.append(error_message)
                    display_message(error_message)

    # Footer
    # st.divider()
    # st.caption("🔒 PipHack - Remember: Only test systems you have permission to assess. Ethical hacking only!")


if __name__ == "__main__":
    main()