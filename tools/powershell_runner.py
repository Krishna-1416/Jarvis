"""
PowerShell & CMD Execution Tool with Safety Interlocks.
Executes non-destructive Windows shell commands and guards against dangerous operations.
"""

import re
import subprocess
from typing import Optional
from core.config import config
from tools.registry import tool

# Regex patterns for destructive commands
DESTRUCTIVE_REGEXES = [
    r"\brmdir\s+/[sS]",
    r"\bdel\s+/[fF]\s+/[sS]",
    r"\bformat\s+[a-zA-Z]:",
    r"\bFormat-Volume\b",
    r"\bRemove-Item\s+.*-Recurse\b",
    r"\bStop-Computer\b",
    r"\bRestart-Computer\b",
    r"\breg\s+delete\b",
    r"\bdiskpart\b",
]

@tool(description="Execute a PowerShell or CMD command safely on Windows. Use for scripting, querying system state, networking, or developer utilities.")
def run_powershell_command(command: str) -> str:
    """
    Execute a PowerShell command.
    command: The PowerShell command string to run
    """
    # Safety check against destructive command regexes
    for pattern in DESTRUCTIVE_REGEXES:
        if re.search(pattern, command, re.IGNORECASE):
            return f"Security Interlock: Command blocked because it matched potentially destructive pattern '{pattern}'. Manual execution required."

    try:
        process = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=25
        )
        
        stdout = process.stdout.strip()
        stderr = process.stderr.strip()
        
        if process.returncode == 0:
            if not stdout:
                return "Command executed successfully with no output."
            if len(stdout) > 2000:
                stdout = stdout[:2000] + "\n... [Output truncated]"
            return stdout
        else:
            return f"Command returned exit code {process.returncode}:\n{stderr or stdout}"
    except subprocess.TimeoutExpired:
        return "Command execution timed out after 25 seconds."
    except Exception as e:
        return f"Error executing PowerShell command: {str(e)}"
