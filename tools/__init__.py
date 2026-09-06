"""
Jarvis Windows Tools & Capabilities Suite.
Exports the tool registry and registers system ops, powershell, web search, file ops, media keys, and memory tools.
"""

from .registry import registry, tool
from . import system_ops
from . import browser_ops
from . import powershell_runner
from . import web_search
from . import file_ops
from . import media_control
from . import window_ops
from . import rag_researcher
from . import gmail_ops
import memory.memory_manager  # Register long-term memory tools

__all__ = ["registry", "tool"]

