"""
Test Autonomous RAG Web Research & Scraping Agent.
"""
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from tools.rag_researcher import deep_web_research, scrape_and_analyze_url
from core.router import BrainRouter

def main():
    print("=== [RAG WEB RESEARCH AGENT TEST] ===")
    
    # 1. Test live deep web research on a real technology topic
    query = "latest features of Python 3.13"
    print(f"\n1. Executing Deep RAG Research for: '{query}'...")
    research_output = deep_web_research(query, max_sources=2)
    print("\n--- Research Findings ---")
    print(research_output)
    
    # 2. Test BrainRouter Intent Dispatch
    print("\n2. Testing BrainRouter Intent Dispatch:")
    router = BrainRouter()
    
    test_queries = [
        "Jarvis, research quantum computing breakthroughs",
    ]
    for q in test_queries:
        print(f"\nUser: '{q}'")
        reply = router.chat(q)
        print(f"Jarvis: {reply}")

    print("\n[SUCCESS] RAG Web Research Diagnostic Completed.")

if __name__ == "__main__":
    main()
