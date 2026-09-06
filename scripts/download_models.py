"""
Robust Model Downloader for Project Jarvis.
Downloads Kokoro ONNX model and voice weights with proper User-Agent headers.
"""

import sys
import os
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TTS_DIR = BASE_DIR / "models" / "tts"
TTS_DIR.mkdir(parents=True, exist_ok=True)

# Kokoro TTS models - GitHub releases & HuggingFace mirrors
MODELS = [
    {
        "name": "kokoro-v0_19.onnx",
        "dest": TTS_DIR / "kokoro-v0_19.onnx",
        "urls": [
            "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx",
            "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro-v0_19.onnx"
        ]
    },
    {
        "name": "voices.json",
        "dest": TTS_DIR / "voices.json",
        "urls": [
            "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.json",
            "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices.json"
        ]
    }
]

def download_with_headers(urls, destination: Path):
    if destination.exists() and destination.stat().st_size > 1000:
        print(f"[OK] Already exists: {destination.name} ({destination.stat().st_size / (1024*1024):.1f} MB)")
        return True

    for url in urls:
        print(f"[DOWNLOADING] {destination.name} from {url}...")
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=30) as response, open(destination, 'wb') as out_file:
                total_size = int(response.info().get('Content-Length', 0))
                downloaded = 0
                block_size = 1024 * 64
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    downloaded += len(buffer)
                    out_file.write(buffer)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"  -> {percent:.1f}% ({downloaded / (1024*1024):.1f}/{total_size / (1024*1024):.1f} MB)", end='\r')
            print(f"\n[SUCCESS] Saved {destination.name} ({destination.stat().st_size / (1024*1024):.1f} MB)")
            return True
        except Exception as e:
            print(f"\n[WARN] Failed from {url}: {e}. Trying next mirror...")
            if destination.exists():
                destination.unlink()
    return False

def main():
    print("=== Downloading Kokoro Neural Voice Models ===")
    for item in MODELS:
        download_with_headers(item["urls"], item["dest"])
    print("=== Model download complete ===")

if __name__ == "__main__":
    main()
