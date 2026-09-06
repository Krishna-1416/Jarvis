"""
Diagnostic test for Jarvis Persistent Episodic Memory & Vector Retrieval.
"""

import sys
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from memory.memory_manager import memory_manager
from core.router import BrainRouter

def main():
    print("=== [MEMORY] Testing Jarvis Persistent Episodic Memory ===")
    
    # 1. Store test facts
    print("\n1. Storing Facts in Long-Term Memory...")
    res1 = memory_manager.remember(
        topic="Favorite Project",
        content="Jarvis AI Assistant running locally on Windows RTX 3050A",
        category="project"
    )
    print(f"  Result: {res1}")

    res2 = memory_manager.remember(
        topic="Developer Name",
        content="Krishna, a software engineer and AI enthusiast",
        category="preference"
    )
    print(f"  Result: {res2}")

    # 2. List all memories
    print("\n2. Listing All Memories:")
    print(memory_manager.list_all())

    # 3. Vector Similarity Search
    print("\n3. Testing Semantic Search / Recall:")
    recall_res = memory_manager.recall("What is Krishna working on?")
    print(f"Query: 'What is Krishna working on?'\n{recall_res}")

    # 4. End-to-End LLM Memory Recall Test
    print("\n4. Testing Autonomous LLM Recall with BrainRouter:")
    router = BrainRouter()
    user_query = "Jarvis, what is my name and what is my favorite project?"
    print(f"User: {user_query}")
    
    mem_context = memory_manager.get_prompt_context(user_query)
    print(f"[Injected Context]:\n{mem_context}")
    
    reply = router.chat(user_query, extra_memory_facts=mem_context)
    print(f"Jarvis: {reply}\n")

    print("[SUCCESS] Memory Subsystem Diagnostics Complete.")

if __name__ == "__main__":
    main()
