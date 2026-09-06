"""
Browser Navigation & Web Operations Subsystem for Project Jarvis.
Enables intelligent website navigation, direct YouTube/Spotify media playback,
smart URL resolution, multi-browser targeting (Brave, Chrome, Edge, Firefox), and web searching.
"""

import os
import re
import shutil
import urllib.parse
import webbrowser
import subprocess
from typing import Optional, Dict, List
from tools.registry import tool

# Popular Web Applications & Domain Mappings
COMMON_WEBSITES: Dict[str, str] = {
    "youtube": "https://www.youtube.com",
    "yt": "https://www.youtube.com",
    "whatsapp": "https://web.whatsapp.com",
    "whatsapp web": "https://web.whatsapp.com",
    "gmail": "https://mail.google.com",
    "mail": "https://mail.google.com",
    "google mail": "https://mail.google.com",
    "email": "https://mail.google.com",
    "inbox": "https://mail.google.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "chatgpt": "https://chatgpt.com",
    "claude": "https://claude.ai",
    "gemini": "https://gemini.google.com",
    "reddit": "https://www.reddit.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "linkedin": "https://www.linkedin.com",
    "instagram": "https://www.instagram.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
    "spotify web": "https://open.spotify.com",
    "notion": "https://www.notion.so",
    "amazon": "https://www.amazon.com",
    "amazon india": "https://www.amazon.in",
    "flipkart": "https://www.flipkart.com",
    "discord": "https://discord.com/app",
    "google maps": "https://maps.google.com",
    "maps": "https://maps.google.com",
    "google drive": "https://drive.google.com",
    "drive": "https://drive.google.com",
    "google docs": "https://docs.google.com",
    "docs": "https://docs.google.com",
    "google sheets": "https://sheets.google.com",
    "sheets": "https://sheets.google.com",
    "canva": "https://www.canva.com",
    "figma": "https://www.figma.com",
    "huggingface": "https://huggingface.co",
    "stackoverflow": "https://stackoverflow.com",
    "stack overflow": "https://stackoverflow.com",
    "medium": "https://medium.com",
    "wikipedia": "https://www.wikipedia.org",
    "weather": "https://www.google.com/search?q=current+weather",
    "news": "https://news.google.com",
}

def _find_browser_exe(browser_name: str) -> Optional[str]:
    """Resolve full executable path for specified browser on Windows."""
    b = browser_name.lower().strip()
    
    paths_map = {
        "brave": [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ],
        "chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        ],
        "edge": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ],
        "firefox": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ]
    }
    
    key = "brave" if "brave" in b else ("chrome" if "chrome" in b else ("edge" if "edge" in b else ("firefox" if "firefox" in b else b)))
    
    if key in paths_map:
        for p in paths_map[key]:
            if os.path.exists(p):
                return p

    return shutil.which(b) or shutil.which(f"{b}.exe")

def normalize_target_url(target: str) -> str:
    """Resolve a user string into a fully qualified HTTPS URL."""
    cleaned = target.strip().lower()
    cleaned = re.sub(r'^(my|the)\s+', '', cleaned).strip()
    
    # 1. Check exact dictionary match
    if cleaned in COMMON_WEBSITES:
        return COMMON_WEBSITES[cleaned]
    
    # 2. Check if already a full URL
    if target.startswith("http://") or target.startswith("https://"):
        return target
        
    # 3. Check for domain extensions (e.g. youtube.com, github.com)
    domain_match = re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$', target.strip())
    if domain_match:
        return f"https://{target.strip()}"
        
    # 4. Fallback to Google Search
    encoded = urllib.parse.quote(target.strip())
    return f"https://www.google.com/search?q={encoded}"

def open_url_in_browser(url: str, browser: Optional[str] = None) -> bool:
    """Open URL using specified browser or system default."""
    if browser:
        exe = _find_browser_exe(browser)
        if exe:
            try:
                subprocess.Popen([exe, url])
                return True
            except Exception:
                pass

    # Try standard Python webbrowser handler
    try:
        if webbrowser.open(url, new=2):
            return True
    except Exception:
        pass

    # Fallback to Windows os.startfile / Start-Process
    try:
        os.startfile(url)
        return True
    except Exception:
        try:
            subprocess.Popen(["powershell", "-NoProfile", "-NonInteractive", "-Command", f"Start-Process '{url}'"], shell=True)
            return True
        except Exception:
            return False

@tool(description="Search for and play any song, video, music track, or topic directly on YouTube in the browser.")
def play_on_youtube(query: str, browser: Optional[str] = None) -> str:
    """
    Search and play a video or song on YouTube.
    query: The song title, video name, or channel to play (e.g. 'loser', 'Iron Man theme', 'lofi hip hop')
    browser: Optional browser to use ('brave', 'chrome', 'edge')
    """
    if not query or not query.strip():
        return "Please specify a song or video to search on YouTube."
        
    clean_q = re.sub(r'\b(on\s+youtube|in\s+youtube|play\s+|watch\s+|youtube\s+)\b', '', query, flags=re.IGNORECASE).strip()
    if not clean_q:
        clean_q = query.strip()

    q_encoded = urllib.parse.quote(clean_q)
    url = f"https://www.youtube.com/results?search_query={q_encoded}"
    
    success = open_url_in_browser(url, browser)
    if success:
        return f"Searching and opening '{clean_q}' on YouTube."
    else:
        return f"Failed to open YouTube search for '{clean_q}'."

@tool(description="Search for and play any song, track, artist, or album directly on Spotify.")
def play_on_spotify(query: str) -> str:
    """
    Search and play music on Spotify.
    query: The song title, artist, or album (e.g. 'loser', 'Daft Punk', 'Starboy')
    """
    if not query or not query.strip():
        return "Please specify a song or artist to search on Spotify."
        
    clean_q = re.sub(r'\b(on\s+spotify|in\s+spotify|play\s+|spotify\s+)\b', '', query, flags=re.IGNORECASE).strip()
    if not clean_q:
        clean_q = query.strip()

    q_encoded = urllib.parse.quote(clean_q)
    url = f"https://open.spotify.com/search/{q_encoded}"
    
    success = open_url_in_browser(url)
    if success:
        return f"Searching and opening '{clean_q}' on Spotify."
    else:
        return f"Failed to open Spotify search for '{clean_q}'."

@tool(description="Open any website or web application in the browser (e.g. 'Gmail', 'YouTube', 'WhatsApp Web', 'GitHub', 'ChatGPT', 'Netflix', 'Reddit', 'Amazon', or any URL). Supports targeting specific browsers like Brave or Chrome.")
def open_website(target: str, browser: Optional[str] = None) -> str:
    """
    Open a website, web app, or URL in the web browser.
    target: The website name or URL (e.g. 'Gmail', 'YouTube', 'WhatsApp', 'https://github.com', 'ChatGPT')
    browser: Optional specific browser name ('brave', 'chrome', 'edge', 'firefox')
    """
    if not target or not target.strip():
        return "Please provide a valid website name or URL."
        
    t_clean = target.lower().strip()
    
    if "youtube" in t_clean and len(t_clean) > 8:
        return play_on_youtube(target, browser)
    if "spotify" in t_clean and len(t_clean) > 8:
        return play_on_spotify(target)

    url = normalize_target_url(target)
    success = open_url_in_browser(url, browser)
    
    target_disp = target.title()
    browser_disp = f" in {browser.title()}" if browser else ""
    if success:
        return f"Successfully opened {target_disp}{browser_disp}."
    else:
        return f"Failed to launch browser for {url}."

@tool(description="Search Google, YouTube, DuckDuckGo, or GitHub and open the results page directly in the browser.")
def search_and_open_in_browser(query: str, engine: str = "google", browser: Optional[str] = None) -> str:
    """
    Perform a search query and display results in the web browser.
    query: The search term or topic (e.g. 'loser on youtube', 'latest AI news', 'Iron Man soundtrack')
    engine: Search engine to use ('google', 'youtube', 'spotify', 'duckduckgo', 'github')
    browser: Optional browser to use ('brave', 'chrome', 'edge')
    """
    if not query or not query.strip():
        return "Please provide a valid search query."
        
    q_lower = query.lower().strip()
    engine_lower = engine.lower().strip()
    
    if "youtube" in engine_lower or "on youtube" in q_lower or "in youtube" in q_lower:
        return play_on_youtube(query, browser)
    elif "spotify" in engine_lower or "on spotify" in q_lower:
        return play_on_spotify(query)
        
    q_encoded = urllib.parse.quote(query.strip())
    if "duck" in engine_lower:
        url = f"https://duckduckgo.com/?q={q_encoded}"
        target_name = "DuckDuckGo"
    elif "github" in engine_lower:
        url = f"https://github.com/search?q={q_encoded}"
        target_name = "GitHub"
    else:
        url = f"https://www.google.com/search?q={q_encoded}"
        target_name = "Google"
        
    success = open_url_in_browser(url, browser)
    if success:
        return f"Opened {target_name} search for '{query}'."
    else:
        return f"Failed to open browser search for '{query}'."
