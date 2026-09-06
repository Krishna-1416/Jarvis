"""
Diagnostic test for Jarvis Windows Tool Registry & Built-in Tools.
"""

import sys
import io
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from tools.registry import registry
from tools import *  # Imports all tools

def main():
    print("=== [TOOLS] Testing Jarvis Tool Registry & Handlers ===")
    
    schemas = registry.get_all_schemas()
    print(f"Registered {len(schemas)} tools:")
    for s in schemas:
        fn = s.get("function", {})
        print(f"  - [Tool] {fn.get('name')}: {fn.get('description')}")
    
    print("\n1. Testing System Volume Tool...")
    res = registry.execute_tool_call("get_system_volume", {})
    print(f"  Result: {res}")

    print("\n2. Testing System Stats Tool...")
    res = registry.execute_tool_call("get_system_stats", {})
    print(f"  Result:\n{res}")

    print("\n3. Testing Safe PowerShell Runner...")
    res = registry.execute_tool_call("run_powershell_command", {"command": "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"})
    print(f"  Result: {res}")

    print("\n4. Testing Blocked Destructive Command Interlock...")
    res = registry.execute_tool_call("run_powershell_command", {"command": "rmdir /s /q test"})
    print(f"  Result: {res}")

    print("\n5. Testing Web Search Tool...")
    res = registry.execute_tool_call("search_web", {"query": "NVIDIA RTX 3050 mobile specs", "max_results": 2})
    print(f"  Result:\n{res[:300]}...\n")

    print("[SUCCESS] All Tool Diagnostics Completed.")

if __name__ == "__main__":
    main()
