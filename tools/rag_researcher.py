"""
Autonomous RAG Web Research & Web Scraping Agent for Project Jarvis.
Performs:
1. Multi-source search (DuckDuckGo).
2. Deep webpage scraping with clean DOM / boilerplate removal.
3. Semantic passage chunking and relevance ranking (RAG).
4. Local LLM contextual synthesis with citations.
5. Permanent long-term memory caching into SQLite memory.
"""

import os
import re
import math
import time
import requests
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

from tools.registry import tool
from memory.db import Database

class WebRAGResearcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.db = Database()

    def scrape_url(self, url: str, timeout: int = 8) -> Dict[str, str]:
        """Scrape a webpage and return cleaned title and article content."""
        try:
            resp = requests.get(url, headers=self.headers, timeout=timeout)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Remove non-content elements
            for tag in soup(["script", "style", "nav", "header", "footer", "aside", "noscript", "svg", "form"]):
                tag.decompose()
                
            title = soup.title.string.strip() if soup.title and soup.title.string else url
            
            # Extract content from main body or article tags if available
            article = soup.find("article") or soup.find("main") or soup.body
            if not article:
                return {"url": url, "title": title, "content": ""}

            paragraphs = article.find_all(["p", "h1", "h2", "h3", "li"])
            text_blocks = []
            for p in paragraphs:
                t = p.get_text(separator=" ", strip=True)
                if len(t) > 25:  # Ignore micro fragments
                    text_blocks.append(t)
                    
            content = "\n".join(text_blocks)
            return {"url": url, "title": title, "content": content}
        except Exception as e:
            return {"url": url, "title": url, "content": f"Failed to scrape ({str(e)})"}

    def chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 60) -> List[str]:
        """Split text into overlapping semantic passages."""
        if not text:
            return []
        
        words = text.split()
        if len(words) <= 60:
            return [text]
            
        chunks = []
        i = 0
        step = 50  # ~50 words per chunk
        while i < len(words):
            chunk = " ".join(words[i:i + step])
            if len(chunk.strip()) > 30:
                chunks.append(chunk)
            i += max(1, step - 10)  # 10 words overlap
        return chunks

    def rank_passages(self, query: str, passages: List[Dict[str, str]], top_k: int = 5) -> List[Dict[str, str]]:
        """Rank passages using BM25-style term frequency and query coverage."""
        q_tokens = [w.lower() for w in re.findall(r'\b\w{3,}\b', query)]
        if not q_tokens:
            return passages[:top_k]

        scored = []
        for p in passages:
            text_lower = p["chunk"].lower()
            score = 0.0
            for qt in q_tokens:
                count = text_lower.count(qt)
                if count > 0:
                    score += (1.0 + math.log(count)) * 2.0
            
            # Boost matches containing full query keywords
            for i in range(len(q_tokens) - 1):
                bigram = f"{q_tokens[i]} {q_tokens[i+1]}"
                if bigram in text_lower:
                    score += 4.0

            scored.append((score, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        # Return top_k with non-zero or best scores
        return [item[1] for item in scored[:top_k]]

    def research_topic(self, query: str, max_sources: int = 10) -> Dict[str, any]:
        """
        Execute full RAG pipeline with parallel web scraping for up to 10 sources:
        1. Search web via DDGS.
        2. Concurrently scrape top 10 sources using thread pool.
        3. Extract & rank relevant passages across all 10 sources.
        4. Synthesize executive summary.
        """
        import concurrent.futures

        # 1. Search DuckDuckGo for top candidates
        search_results = []
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_sources + 4))
                for r in results:
                    href = r.get("href", "")
                    if href and not any(href.lower().endswith(ext) for ext in [".pdf", ".png", ".jpg", ".mp4"]):
                        search_results.append(r)
                    if len(search_results) >= max_sources:
                        break
        except Exception as e:
            return {
                "summary": f"Web search could not be reached: {e}",
                "sources": [],
                "passages": []
            }

        if not search_results:
            return {
                "summary": f"No web sources found for '{query}'.",
                "sources": [],
                "passages": []
            }

        # 2. Concurrently scrape each source in parallel
        all_passages = []
        scraped_sources = []
        
        def _fetch_source(res):
            url = res["href"]
            title = res.get("title", url)
            snippet = res.get("body", "")
            scraped = self.scrape_url(url, timeout=6)
            return res, scraped

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, len(search_results))) as executor:
            future_to_source = [executor.submit(_fetch_source, r) for r in search_results]
            for future in concurrent.futures.as_completed(future_to_source):
                try:
                    res, scraped = future.result()
                    url = res["href"]
                    title = res.get("title", url)
                    snippet = res.get("body", "")
                    content = scraped.get("content", "")

                    if len(content) > 100:
                        chunks = self.chunk_text(content)
                        for c in chunks:
                            all_passages.append({"source": title, "url": url, "chunk": c})
                        scraped_sources.append({"title": title, "url": url})
                    elif snippet:
                        all_passages.append({"source": title, "url": url, "chunk": snippet})
                        scraped_sources.append({"title": title, "url": url})
                except Exception:
                    pass

        # 3. RAG Retrieval: Rank passages against query (select top 15 rich passages)
        top_passages = self.rank_passages(query, all_passages, top_k=15)
        
        # 4. Context Synthesis via Local LLM (Ollama qwen2.5:1.5b)
        context_text = "\n\n".join([f"[{i+1}] Source: {p['source']}\n{p['chunk']}" for i, p in enumerate(top_passages)])
        
        synthesis = self._synthesize_with_llm(query, context_text, scraped_sources)
        
        # 5. Store key findings into permanent SQLite Memory
        try:
            self.db.insert_or_update_memory(
                topic=f"Research on {query}",
                content=f"Topic: {query} | Key Findings: {synthesis[:800]}",
                category="web_research"
            )
        except Exception:
            pass

        return {
            "query": query,
            "summary": synthesis,
            "sources": scraped_sources[:max_sources],
            "passages_used": len(top_passages)
        }

    def _synthesize_with_llm(self, query: str, context: str, sources: List[Dict[str, str]]) -> str:
        """Call local Ollama to synthesize detailed 8-15 pointwise answer with facts."""
        import ollama
        system_prompt = (
            "You are Jarvis, an elite AI research assistant.\n"
            "Synthesize comprehensive research findings across all scraped web sources.\n\n"
            "STRICT RULES:\n"
            "1. Output between 8 to 15 detailed, high-impact bullet points formatted with '• '.\n"
            "2. Cover all key aspects: core breakthroughs, technical specifications, benchmarks, architectural changes, and key takeaways.\n"
            "3. Each bullet point should be 1-2 informative, high-density sentences in plain, readable English.\n"
            "4. NEVER cite obscure internal code variables or compiler flags unless specifically requested.\n"
            "5. Put each bullet point on its own separate line.\n"
            "6. Absolutely NO conversational preamble, filler, or conclusion."
        )
        user_prompt = (
            f"User Query: {query}\n\n"
            f"Scraped Web Context across 10 sources:\n{context}\n\n"
            "Synthesize 8 to 15 comprehensive bullet points covering the full depth of the topic:"
        )
        
        try:
            response = ollama.chat(
                model="qwen2.5:1.5b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "repeat_penalty": 1.18,
                    "num_predict": 700
                }
            )
            raw = response['message']['content'].strip()
            # Ensure unique, clean newline spacing
            lines = [line.strip() for line in raw.split('\n') if line.strip()]
            unique_lines = []
            seen_prefixes = set()
            for line in lines:
                norm = re.sub(r'^[•\-\*]\s*', '', line).strip().lower()[:35]
                if norm and norm not in seen_prefixes:
                    seen_prefixes.add(norm)
                    unique_lines.append(line)
            return "\n\n".join(unique_lines[:12])
        except Exception as e:
            # Fallback heuristic summary if Ollama is unreachable
            top_facts = [p.split('\n')[-1] for p in context.split('\n\n')[:10]]
            return "\n\n".join([f"• {f}" for f in top_facts])

# Singleton instance
_researcher = WebRAGResearcher()

@tool(description="Autonomous RAG Web Research Agent: searches the live web, scrapes top articles, extracts key passages via RAG, and synthesizes an accurate, fact-based answer with sources.")
def deep_web_research(topic: str, max_sources: int = 10) -> str:
    """
    Search and scrape the live internet to research a topic.
    topic: The topic, question, or technology to research (e.g. 'latest release of Python', 'what happened in SpaceX today', 'how does quantum computing work')
    max_sources: Number of web sources to scrape and analyze (default 10)
    """
    if not topic or not topic.strip():
        return "Please provide a valid topic to research on the web."
        
    res = _researcher.research_topic(topic.strip(), max_sources=max_sources)
    
    output = [res["summary"]]
    if res["sources"]:
        output.append("\n**Sources:**")
        for s in res["sources"]:
            output.append(f"- [{s['title']}]({s['url']})")
            
    return "\n".join(output)

@tool(description="Scrape and extract key knowledge and answers from a specific webpage URL using RAG.")
def scrape_and_analyze_url(url: str, focus_question: Optional[str] = None) -> str:
    """
    Scrape a specific URL and extract answers.
    url: Web URL to scrape
    focus_question: Optional specific question to answer from the page
    """
    scraped = _researcher.scrape_url(url)
    if not scraped["content"] or "Failed to scrape" in scraped["content"]:
        return f"Could not scrape {url}: {scraped['content']}"

    chunks = _researcher.chunk_text(scraped["content"])
    passages = [{"source": scraped["title"], "url": url, "chunk": c} for c in chunks]
    
    q = focus_question or scraped["title"]
    ranked = _researcher.rank_passages(q, passages, top_k=4)
    context = "\n\n".join([f"[{i+1}] {p['chunk']}" for i, p in enumerate(ranked)])
    
    summary = _researcher._synthesize_with_llm(q, context, [{"title": scraped["title"], "url": url}])
    return f"**Summary of {scraped['title']}** ({url}):\n\n{summary}"
