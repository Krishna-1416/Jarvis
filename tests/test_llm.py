"""
Diagnostic test for Ollama Local LLM (qwen2.5:1.5b) and Function Calling Integration.
"""
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from core.router import BrainRouter

def main():
    print("=== [BRAIN] Testing Jarvis Brain Router (Ollama Qwen 2.5 1.5B) ===")
    
    router = BrainRouter()
    
    # 1. YouTube Specific Song Search
    print("\n1. Testing 'open loser on YouTube':")
    prompt1 = "Jarvis, open loser on YouTube"
    print(f"User: {prompt1}")
    reply1 = router.chat(prompt1)
    print(f"Jarvis: {reply1}\n")

    # 2. General Website Opening
    print("\n2. Testing General Website Opening:")
    prompt2 = "Jarvis, open GitHub for me"
    print(f"User: {prompt2}")
    reply2 = router.chat(prompt2)
    print(f"Jarvis: {reply2}\n")

    print("[SUCCESS] Local LLM & Tool Calling Diagnostic Completed.")

if __name__ == "__main__":
    main()
