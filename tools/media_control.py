"""
Media Playback & Windows Multimedia Keys Subsystem for Project Jarvis.
Sends virtual hardware media keys for Spotify, YouTube, Chrome, Edge, VLC, and Windows media players.
Supports play/pause, next/previous tracks, forward/rewind, and hardware volume key simulation.
"""

import time
import ctypes
from typing import Optional
from tools.registry import tool

# Windows Virtual Key Codes for Multimedia & Navigation
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_LEFT = 0x25
VK_RIGHT = 0x27
VK_SPACE = 0x20

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002

def _send_virtual_key(vk_code: int):
    """Send keydown and keyup for a virtual hardware key code."""
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
    time.sleep(0.02)
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)

@tool(description="Toggle Play, Pause, or Resume for currently active media player (Spotify, YouTube, VLC, browser video).")
def media_play_pause() -> str:
    """Toggle media play/pause."""
    try:
        _send_virtual_key(VK_MEDIA_PLAY_PAUSE)
        return "Toggled media Play/Pause."
    except Exception as e:
        return f"Failed to toggle media playback: {e}"

@tool(description="Skip to the next audio track, music track, or video (Next video on YouTube / Next track on Spotify).")
def media_next_track() -> str:
    """Skip to next media track/video."""
    try:
        _send_virtual_key(VK_MEDIA_NEXT_TRACK)
        return "Skipped to the next track/video."
    except Exception as e:
        return f"Failed to skip track: {e}"

@tool(description="Go back to the previous audio track or video (Previous video on YouTube / Previous track on Spotify).")
def media_previous_track() -> str:
    """Go back to previous media track/video."""
    try:
        _send_virtual_key(VK_MEDIA_PREV_TRACK)
        return "Returned to the previous track/video."
    except Exception as e:
        return f"Failed to return to previous track: {e}"

@tool(description="Fast forward the currently playing video or media by a few seconds (Right arrow / skip ahead).")
def media_fast_forward(seconds: int = 5) -> str:
    """Fast forward video/audio."""
    try:
        repeats = max(1, seconds // 5)
        for _ in range(repeats):
            _send_virtual_key(VK_RIGHT)
            time.sleep(0.05)
        return f"Fast-forwarded video by ~{seconds} seconds."
    except Exception as e:
        return f"Failed to fast-forward: {e}"

@tool(description="Rewind the currently playing video or media by a few seconds (Left arrow / step back).")
def media_rewind(seconds: int = 5) -> str:
    """Rewind video/audio."""
    try:
        repeats = max(1, seconds // 5)
        for _ in range(repeats):
            _send_virtual_key(VK_LEFT)
            time.sleep(0.05)
        return f"Rewound video by ~{seconds} seconds."
    except Exception as e:
        return f"Failed to rewind: {e}"

@tool(description="Stop media playback completely.")
def media_stop() -> str:
    """Stop media playback."""
    try:
        _send_virtual_key(VK_MEDIA_STOP)
        return "Stopped media playback."
    except Exception as e:
        return f"Failed to stop media: {e}"
