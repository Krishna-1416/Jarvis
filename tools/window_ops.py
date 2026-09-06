"""
Windows Window & Browser Tab Automation Tool for Project Jarvis.
Provides operations to close/exit apps, close/switch browser tabs, minimize/maximize windows,
and terminate named running desktop applications cleanly.
"""

import time
import ctypes
import ctypes.wintypes
import subprocess
from typing import Optional, List, Set
import psutil
from tools.registry import tool

# Windows Virtual Key Codes & Hardware Scan Codes
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_MENU = 0x12       # Alt key
VK_LWIN = 0x5B       # Windows key
VK_TAB = 0x09
VK_F4 = 0x73
VK_ESCAPE = 0x1B
VK_W = 0x57
VK_T = 0x54
VK_D = 0x44
VK_M = 0x4D

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002

user32 = ctypes.windll.user32

def _focus_browser():
    """Attempt to bring any open browser window to the foreground."""
    browser_names: Set[str] = {"brave.exe", "chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "vivaldi.exe"}
    target_hwnd = None

    # Check if current foreground is already a browser
    fg_hwnd = user32.GetForegroundWindow()
    if fg_hwnd:
        pid = ctypes.wintypes.DWORD()
        user32.GetWindowThreadProcessId(fg_hwnd, ctypes.byref(pid))
        try:
            p = psutil.Process(pid.value)
            if p.name().lower() in browser_names:
                return fg_hwnd
        except Exception:
            pass

    def enum_cb(hwnd, _):
        nonlocal target_hwnd
        if target_hwnd is None and user32.IsWindowVisible(hwnd):
            pid = ctypes.wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            try:
                p = psutil.Process(pid.value)
                if p.name().lower() in browser_names:
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        target_hwnd = hwnd
            except Exception:
                pass
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

    if target_hwnd:
        try:
            user32.ShowWindow(target_hwnd, 9)  # SW_RESTORE
            user32.SetForegroundWindow(target_hwnd)
            time.sleep(0.06)
            return target_hwnd
        except Exception:
            pass
    return None

def _send_keys_direct(keys: List[int]):
    """
    Press and release virtual keys with correct standard keyboard flags.
    Standard keys (Ctrl, Shift, Alt, W, T) use flag=0 for KeyDown and flag=0x0002 for KeyUp.
    """
    # KeyDown in forward order
    for k in keys:
        scan_code = user32.MapVirtualKeyW(k, 0)
        user32.keybd_event(k, scan_code, 0, 0)
        time.sleep(0.02)
    time.sleep(0.04)
    # KeyUp in reverse order
    for k in reversed(keys):
        scan_code = user32.MapVirtualKeyW(k, 0)
        user32.keybd_event(k, scan_code, KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)

@tool(description="Close the active/current tab in the web browser (Chrome, Brave, Edge, Firefox, etc.) using Ctrl+W.")
def close_active_tab() -> str:
    """Close the current tab in the active browser window."""
    try:
        _focus_browser()
        _send_keys_direct([VK_CONTROL, VK_W])
        return "Closed the active browser tab."
    except Exception as e:
        return f"Failed to close tab: {e}"

@tool(description="Reopen the most recently closed tab in the browser using Ctrl+Shift+T.")
def reopen_closed_tab() -> str:
    """Reopen previously closed tab."""
    try:
        _focus_browser()
        _send_keys_direct([VK_CONTROL, VK_SHIFT, VK_T])
        return "Reopened the closed browser tab."
    except Exception as e:
        return f"Failed to reopen tab: {e}"

@tool(description="Switch to the next tab in the active browser or editor using Ctrl+Tab.")
def next_browser_tab() -> str:
    """Switch to next tab."""
    try:
        _focus_browser()
        _send_keys_direct([VK_CONTROL, VK_TAB])
        return "Switched to the next tab."
    except Exception as e:
        return f"Failed to switch tab: {e}"

@tool(description="Switch to the previous tab in the active browser using Ctrl+Shift+Tab.")
def previous_browser_tab() -> str:
    """Switch to previous tab."""
    try:
        _focus_browser()
        _send_keys_direct([VK_CONTROL, VK_SHIFT, VK_TAB])
        return "Switched to the previous tab."
    except Exception as e:
        return f"Failed to switch tab: {e}"

@tool(description="Close or exit the currently focused window or application using Alt+F4.")
def close_active_window() -> str:
    """Close the currently focused window or app."""
    try:
        _send_keys_direct([VK_MENU, VK_F4])
        return "Closed the active application window."
    except Exception as e:
        return f"Failed to close window: {e}"

@tool(description="Close, exit, or terminate a specific running application by name (e.g. Chrome, Spotify, Brave, Notepad, Calculator, Discord, Steam, VSCode).")
def close_application_by_name(app_name: str) -> str:
    """
    Close or terminate a running application by name.
    app_name: Name of the application to close (e.g. 'spotify', 'chrome', 'brave', 'calculator', 'notepad')
    """
    q = app_name.lower().strip()
    aliases = {
        "spotify": "spotify",
        "chrome": "chrome",
        "google chrome": "chrome",
        "brave": "brave",
        "brave browser": "brave",
        "edge": "msedge",
        "microsoft edge": "msedge",
        "vscode": "code",
        "vs code": "code",
        "code": "code",
        "calculator": "calculator",
        "calc": "calculator",
        "notepad": "notepad",
        "discord": "discord",
        "steam": "steam",
        "telegram": "telegram",
        "vlc": "vlc",
        "terminal": "windowsterminal",
    }
    target_stem = aliases.get(q, q)

    if target_stem in ("explorer", "file explorer", "files"):
        _send_keys_direct([VK_MENU, VK_F4])
        return "Closed active File Explorer window."

    closed_count = 0
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pname = proc.info['name'].lower()
                if target_stem in pname or pname.startswith(target_stem):
                    proc.terminate()
                    closed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if closed_count > 0:
            return f"Closed {app_name.title()} ({closed_count} process instances terminated)."
        else:
            _send_keys_direct([VK_MENU, VK_F4])
            return f"Requested to close {app_name}."
    except Exception as e:
        return f"Failed to close {app_name}: {e}"

@tool(description="Minimize the currently active window.")
def minimize_active_window() -> str:
    """Minimize active window."""
    try:
        user32.keybd_event(VK_LWIN, 0, KEYEVENTF_EXTENDEDKEY, 0)
        time.sleep(0.02)
        user32.keybd_event(VK_D, 0, 0, 0)
        time.sleep(0.04)
        user32.keybd_event(VK_D, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        user32.keybd_event(VK_LWIN, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
        return "Minimized the window."
    except Exception as e:
        return f"Failed to minimize: {e}"
