"""
Universal Windows System Operations & Desktop Application Launcher for Project Jarvis.
Dynamically indexes all 190+ installed Windows applications (Win32 exes, Windows Store/UWP apps,
Start Menu shortcuts, and Desktop shortcuts) with fuzzy name matching and web-app fallbacks.
"""

import os
import re
import json
import time
import ctypes
import difflib
import threading
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from tools.registry import tool

# Common App Aliases to map short voice names to Windows Start App names
APP_ALIASES: Dict[str, str] = {
    "vscode": "visual studio code",
    "vs code": "visual studio code",
    "code": "visual studio code",
    "chrome": "google chrome",
    "brave": "brave",
    "brave browser": "brave",
    "calc": "calculator",
    "terminal": "terminal",
    "windows terminal": "terminal",
    "cmd": "command prompt",
    "powershell": "windows powershell",
    "explorer": "file explorer",
    "file explorer": "file explorer",
    "files": "file explorer",
    "settings": "settings",
    "mouse settings": "ms-settings:mousetouchpad",
    "mouse": "ms-settings:mousetouchpad",
    "touchpad settings": "ms-settings:devices-touchpad",
    "touchpad": "ms-settings:devices-touchpad",
    "sound settings": "ms-settings:sound",
    "audio settings": "ms-settings:sound",
    "display settings": "ms-settings:display",
    "display": "ms-settings:display",
    "bluetooth settings": "ms-settings:bluetooth",
    "bluetooth": "ms-settings:bluetooth",
    "wifi settings": "ms-settings:network-wifi",
    "wifi": "ms-settings:network-wifi",
    "network settings": "ms-settings:network",
    "windows update": "ms-settings:windowsupdate",
    "update settings": "ms-settings:windowsupdate",
    "installed apps": "ms-settings:appsfeatures",
    "apps settings": "ms-settings:appsfeatures",
    "battery settings": "ms-settings:powersleep",
    "power settings": "ms-settings:powersleep",
    "control panel": "control panel",
    "task manager": "task manager",
    "taskmgr": "task manager",
    "notepad": "notepad",
    "paint": "paint",
    "antigravity": "antigravity ide",
    "spotify": "spotify",
    "discord": "discord",
    "steam": "steam",
    "telegram": "telegram desktop",
    "whatsapp": "whatsapp",
}

class AppIndexer:
    """Discovers and caches all installed Windows applications dynamically."""
    def __init__(self):
        self._apps: Dict[str, str] = {}  # {Normalized_Name: AppID_or_Path}
        self._display_names: Dict[str, str] = {}  # {Normalized_Name: Official_Display_Name}
        self._lock = threading.Lock()
        self._is_indexed = False
        threading.Thread(target=self.refresh_index, daemon=True).start()

    def refresh_index(self):
        """Query Windows Get-StartApps and file shortcuts to index all apps."""
        with self._lock:
            temp_apps = {}
            temp_display = {}
            try:
                # 1. Query Windows Get-StartApps via PowerShell
                cmd = "Get-StartApps | Select-Object Name, AppID | ConvertTo-Json -Compress"
                p = subprocess.run(
                    ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if p.stdout.strip():
                    raw_data = json.loads(p.stdout)
                    if isinstance(raw_data, dict):
                        raw_data = [raw_data]
                    for item in raw_data:
                        name = item.get("Name", "").strip()
                        aid = item.get("AppID", "").strip()
                        if name and aid:
                            norm = name.lower()
                            temp_apps[norm] = aid
                            temp_display[norm] = name
            except Exception as e:
                print(f"[AppIndexer] Error indexing Get-StartApps: {e}")

            # 2. Add Desktop & User Start Menu Shortcuts
            user_home = Path.home()
            shortcut_dirs = [
                user_home / "Desktop",
                Path("C:/Users/Public/Desktop"),
                user_home / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs",
                Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs")
            ]

            for sdir in shortcut_dirs:
                if sdir.exists():
                    try:
                        for item in sdir.glob("**/*"):
                            if item.suffix.lower() in (".lnk", ".url", ".exe") and not item.name.startswith("Uninstall"):
                                stem = item.stem.lower()
                                if stem not in temp_apps:
                                    temp_apps[stem] = str(item)
                                    temp_display[stem] = item.stem
                    except Exception:
                        pass

            self._apps = temp_apps
            self._display_names = temp_display
            self._is_indexed = True
            print(f"[AppIndexer] [OK] Indexed {len(self._apps)} installed Windows applications.")

    def find_app(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Match a spoken query to an installed app name and launch target.
        Returns: (Official_Name, AppID_or_Path) or (None, None)
        """
        if not self._is_indexed:
            self.refresh_index()

        q = query.lower().strip()
        # Resolve common voice alias
        q_target = APP_ALIASES.get(q, q)

        with self._lock:
            # 1. Exact match
            if q_target in self._apps:
                return self._display_names[q_target], self._apps[q_target]
            if q in self._apps:
                return self._display_names[q], self._apps[q]

            # 2. Word Boundary / Prefix / Substring match
            for norm_name, aid in self._apps.items():
                if q_target == norm_name or norm_name.startswith(q_target) or f" {q_target} " in f" {norm_name} ":
                    return self._display_names[norm_name], aid

            # 3. Contains match
            for norm_name, aid in self._apps.items():
                if q_target in norm_name:
                    return self._display_names[norm_name], aid

            # 4. Fuzzy close match
            all_keys = list(self._apps.keys())
            matches = difflib.get_close_matches(q_target, all_keys, n=1, cutoff=0.55)
            if matches:
                matched_key = matches[0]
                return self._display_names[matched_key], self._apps[matched_key]

        return None, None

    def list_apps(self, filter_str: Optional[str] = None) -> List[str]:
        """Return list of display names of all installed apps."""
        with self._lock:
            if not filter_str:
                return sorted(list(self._display_names.values()))
            f_clean = filter_str.lower().strip()
            return sorted([
                disp for norm, disp in self._display_names.items() 
                if f_clean in norm
            ])

# Global singleton app indexer
app_indexer = AppIndexer()

def _get_audio_endpoint():
    """Get Windows master audio endpoint volume controller with COM thread initialization."""
    try:
        import pythoncom
        pythoncom.CoInitialize()
        from pycaw.pycaw import AudioUtilities
        speakers = AudioUtilities.GetSpeakers()
        return speakers.EndpointVolume
    except Exception as e:
        print(f"[SystemOps] Error accessing speakers volume: {e}")
        return None

# ==================== UNIVERSAL APP LAUNCHER ====================

@tool(description="Launch or open any installed Windows application (e.g. Spotify, VS Code, Brave, Chrome, Discord, Steam, Calculator, Terminal, Notepad, Settings, Antigravity IDE, etc.). For websites or web apps like YouTube or WhatsApp, automatically opens them in the browser.")
def launch_application(app_name: str) -> str:
    """
    Launch any desktop application or web service installed on Windows.
    app_name: The name of the application or website to open
    """
    name_clean = app_name.lower().strip()
    
    # 1. Check if target is a media query or website
    from tools.browser_ops import COMMON_WEBSITES, open_website, play_on_youtube, play_on_spotify
    if "youtube" in name_clean and len(name_clean) > 8:
        return play_on_youtube(app_name)
    if "spotify" in name_clean and len(name_clean) > 8:
        return play_on_spotify(app_name)
    # 2. Check direct Windows Settings / URI aliases
    if name_clean in APP_ALIASES and APP_ALIASES[name_clean].startswith("ms-settings:"):
        try:
            os.startfile(APP_ALIASES[name_clean])
            return f"Successfully opened {name_clean.title()}."
        except Exception:
            pass

    # 3. Search Universal Windows App Index
    official_name, target = app_indexer.find_app(app_name)
    
    if official_name and target:
        try:
            # Check if target is a file path (.exe, .lnk)
            if "\\" in target or "/" in target or target.endswith(".exe") or target.endswith(".lnk"):
                try:
                    os.startfile(target)
                    return f"Successfully opened {official_name}."
                except Exception:
                    subprocess.Popen(f'explorer.exe "{target}"', shell=True)
                    return f"Successfully launched {official_name}."
            else:
                # Target is a Windows Store / UWP AppID (e.g. Google.AntigravityIDE, Microsoft.WindowsCalculator)
                subprocess.Popen(["powershell", "-NoProfile", "-NonInteractive", "-Command", f"Start-Process 'shell:AppsFolder\\{target}'"], shell=True)
                return f"Successfully opened {official_name}."
        except Exception as e:
            pass

    # 3. Direct protocol / executable fallback
    try:
        os.startfile(app_name)
        return f"Successfully opened {app_name}."
    except Exception:
        pass

    # 4. Fallback to Web App if available
    if name_clean in COMMON_WEBSITES:
        return open_website(name_clean)

    return f"Could not find an installed application named '{app_name}'. You can ask me to search for it online or open it in your browser."

@tool(description="List or search all installed applications on this Windows PC.")
def list_installed_applications(filter_query: Optional[str] = None) -> str:
    """
    List installed apps.
    filter_query: Optional search keyword to filter app names (e.g. 'code', 'player', 'adobe')
    """
    apps = app_indexer.list_apps(filter_query)
    if not apps:
        return f"No installed applications found matching '{filter_query}'."
    
    sample = apps[:30]
    total = len(apps)
    list_str = "\n".join(f"- {a}" for a in sample)
    if total > 30:
        list_str += f"\n... and {total - 30} more applications."
    return f"Found {total} installed applications:\n{list_str}"

# ==================== VOLUME CONTROLS ====================

@tool(description="Set the Windows master audio volume level as a percentage from 0 to 100.")
def set_system_volume(level: int) -> str:
    """Set master volume percentage (0 to 100)."""
    level = max(0, min(100, int(level)))
    endpoint = _get_audio_endpoint()
    if endpoint is None:
        return "Audio volume controller (pycaw) is unavailable."
    
    try:
        endpoint.SetMasterVolumeLevelScalar(level / 100.0, None)
        endpoint.SetMute(0, None)
        return f"Master volume set to {level}%."
    except Exception as e:
        return f"Failed to set volume: {e}"

@tool(description="Get the current Windows audio volume level and mute status.")
def get_system_volume() -> str:
    """Get current master audio volume level."""
    endpoint = _get_audio_endpoint()
    if endpoint is None:
        return "Audio volume controller is unavailable."
    try:
        current_scalar = endpoint.GetMasterVolumeLevelScalar()
        is_muted = endpoint.GetMute()
        pct = int(round(current_scalar * 100))
        status = f"{pct}% (Muted)" if is_muted else f"{pct}%"
        return f"Current master volume is {status}."
    except Exception as e:
        return f"Failed to get volume status: {e}"

@tool(description="Increase the Windows master volume by a specified percentage step (default 10%).")
def increase_system_volume(delta: int = 10) -> str:
    """Increase master volume by delta percent."""
    endpoint = _get_audio_endpoint()
    if endpoint is None:
        return "Audio volume controller is unavailable."
    try:
        curr = int(round(endpoint.GetMasterVolumeLevelScalar() * 100))
        new_val = min(100, curr + delta)
        endpoint.SetMasterVolumeLevelScalar(new_val / 100.0, None)
        endpoint.SetMute(0, None)
        return f"Increased volume to {new_val}%."
    except Exception as e:
        return f"Failed to increase volume: {e}"

@tool(description="Decrease the Windows master volume by a specified percentage step (default 10%).")
def decrease_system_volume(delta: int = 10) -> str:
    """Decrease master volume by delta percent."""
    endpoint = _get_audio_endpoint()
    if endpoint is None:
        return "Audio volume controller is unavailable."
    try:
        curr = int(round(endpoint.GetMasterVolumeLevelScalar() * 100))
        new_val = max(0, curr - delta)
        endpoint.SetMasterVolumeLevelScalar(new_val / 100.0, None)
        return f"Decreased volume to {new_val}%."
    except Exception as e:
        return f"Failed to decrease volume: {e}"

@tool(description="Mute or unmute the master audio output.")
def toggle_audio_mute(mute: Optional[bool] = None) -> str:
    """Mute or unmute master volume."""
    endpoint = _get_audio_endpoint()
    if endpoint is None:
        return "Audio volume controller is unavailable."
    try:
        current_mute = endpoint.GetMute()
        target_mute = (not current_mute) if mute is None else (1 if mute else 0)
        endpoint.SetMute(target_mute, None)
        return f"Master audio {'muted' if target_mute else 'unmuted'}."
    except Exception as e:
        return f"Failed to toggle mute: {e}"

# ==================== BRIGHTNESS CONTROLS ====================

@tool(description="Set the screen / display brightness level as a percentage from 0 to 100.")
def set_system_brightness(level: int) -> str:
    """Set screen brightness percentage (0 to 100)."""
    level = max(0, min(100, int(level)))
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(level)
        return f"Screen brightness set to {level}%."
    except Exception as e:
        try:
            cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})"
            subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd], capture_output=True, timeout=3)
            return f"Screen brightness set to {level}%."
        except Exception as e2:
            return f"Failed to adjust brightness: {e}"

@tool(description="Get the current screen / display brightness level.")
def get_system_brightness() -> str:
    """Get current screen brightness level."""
    try:
        import screen_brightness_control as sbc
        current = sbc.get_brightness()
        val = current[0] if isinstance(current, list) and current else current
        return f"Current screen brightness is {val}%."
    except Exception as e:
        return f"Could not retrieve brightness: {e}"

@tool(description="Increase the screen brightness by a specified percentage step (default 10%).")
def increase_system_brightness(delta: int = 10) -> str:
    """Increase screen brightness by delta percent."""
    try:
        import screen_brightness_control as sbc
        current = sbc.get_brightness()
        curr_val = current[0] if isinstance(current, list) and current else 50
        new_val = min(100, curr_val + delta)
        sbc.set_brightness(new_val)
        return f"Increased brightness to {new_val}%."
    except Exception as e:
        return f"Failed to increase brightness: {e}"

@tool(description="Decrease the screen brightness by a specified percentage step (default 10%).")
def decrease_system_brightness(delta: int = 10) -> str:
    """Decrease screen brightness by delta percent."""
    try:
        import screen_brightness_control as sbc
        current = sbc.get_brightness()
        curr_val = current[0] if isinstance(current, list) and current else 50
        new_val = max(0, curr_val - delta)
        sbc.set_brightness(new_val)
        return f"Decreased brightness to {new_val}%."
    except Exception as e:
        return f"Failed to decrease brightness: {e}"

# ==================== SYSTEM METRICS & SECURITY ====================

@tool(description="Lock the Windows workstation immediately for security.")
def lock_workstation() -> str:
    """Lock the Windows desktop workstation."""
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Workstation locked successfully."
    except Exception as e:
        return f"Failed to lock workstation: {e}"

@tool(description="Get system battery status, CPU usage, and RAM usage stats.")
def get_system_stats() -> str:
    """Get battery, CPU, and RAM metrics."""
    import psutil
    try:
        cpu_pct = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        
        bat_str = "No battery detected (Desktop/AC)"
        if battery:
            plugged = "Plugged in (Charging)" if battery.power_plugged else "Discharging"
            bat_str = f"{battery.percent}% ({plugged})"
            
        return (
            f"System Statistics:\n"
            f"- CPU Usage: {cpu_pct}%\n"
            f"- RAM Usage: {mem.percent}% ({mem.used // (1024*1024)} MB used / {mem.total // (1024*1024)} MB total)\n"
            f"- Battery: {bat_str}"
        )
    except Exception as e:
        return f"Failed to retrieve system stats: {e}"
