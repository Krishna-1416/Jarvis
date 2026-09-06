"""
Create Jarvis Desktop Shortcut on Windows.
"""

import os
import subprocess
from pathlib import Path

desktop = Path(os.environ["USERPROFILE"]) / "Desktop"
jarvis_dir = Path(__file__).resolve().parent.parent
target_bat = jarvis_dir / "run_jarvis.bat"
shortcut_path = desktop / "Jarvis AI Assistant.lnk"

# Copy updated bat to desktop as well
dest_bat = desktop / "run_jarvis.bat"
with open(target_bat, "r", encoding="utf-8") as src, open(dest_bat, "w", encoding="utf-8") as dst:
    dst.write(src.read())

ps_script = f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{str(shortcut_path)}')
$s.TargetPath = '{str(target_bat)}'
$s.WorkingDirectory = '{str(jarvis_dir)}'
$s.Description = 'Project Jarvis AI Desktop Assistant'
$s.Save()
"""

subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
print(f"[OK] Desktop Shortcut created at: {shortcut_path}")
print(f"[OK] Updated desktop launcher at: {dest_bat}")
