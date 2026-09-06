"""
Memory Manager & Recall Engine for Project Jarvis.
Provides unified semantic and episodic memory storage, tool hooks, and system prompt injection.
"""

from typing import List, Dict, Any, Optional
from memory.db import Database
from memory.vector_store import VectorStore
from tools.registry import tool

class MemoryManager:
    def __init__(self, db_path: Optional[str] = None):
        self.db = Database(db_path=db_path)
        self.vector_store = VectorStore()

    def remember(self, topic: str, content: str, category: str = "fact") -> str:
        """Store a fact or preference in long-term memory."""
        text_to_embed = f"{topic}: {content}"
        emb = self.vector_store.encode(text_to_embed)
        emb_blob = self.vector_store.serialize_embedding(emb)
        
        mem_id = self.db.insert_or_update_memory(
            topic=topic,
            content=content,
            category=category,
            embedding=emb_blob
        )
        return f"Memorized [{topic}]: '{content}' (Memory ID: {mem_id})"

    def recall(self, query: str, top_k: int = 4) -> str:
        """Retrieve memories relevant to a query."""
        all_mems = self.db.get_all_memories()
        if not all_mems:
            return "No memories stored yet."

        results = self.vector_store.search_top_k(query, all_mems, top_k=top_k)
        if not results:
            return f"No memories found matching '{query}'."

        formatted = []
        for mem, score in results:
            formatted.append(f"- **{mem.get('topic')}**: {mem.get('content')} (Match: {score*100:.0f}%)")
        return "\n".join(formatted)

    def forget(self, topic: str) -> str:
        """Delete a memory by topic name."""
        success = self.db.delete_memory(topic)
        if success:
            return f"Successfully removed memory about '{topic}'."
        return f"No memory found with topic '{topic}'."

    def list_all(self) -> str:
        """List all stored memories."""
        all_mems = self.db.get_all_memories()
        if not all_mems:
            return "Memory is currently empty."
        
        formatted = ["Stored Long-Term Memories:"]
        for m in all_mems:
            formatted.append(f"- [{m.get('category').upper()}] **{m.get('topic')}**: {m.get('content')}")
        return "\n".join(formatted)

    def get_prompt_context(self, query: str, top_k: int = 3) -> str:
        """Format top matching memories for dynamic system prompt injection."""
        all_mems = self.db.get_all_memories()
        if not all_mems:
            return ""

        results = self.vector_store.search_top_k(query, all_mems, top_k=top_k, threshold=0.30)
        if not results:
            return ""

        lines = [f"- {m.get('topic')}: {m.get('content')}" for m, _ in results]
        return "\n".join(lines)

# Global memory manager singleton
memory_manager = MemoryManager()

# Register Memory Tools for the AI Brain
@tool(description="Remember or save a user fact, preference, project path, or instruction into persistent long-term memory.")
def remember_user_fact(topic: str, fact_content: str, category: str = "fact") -> str:
    """
    Store a fact in long-term memory.
    topic: Short keyword or topic title (e.g. 'Project Jarvis Path', 'User Name', 'Coffee Preference')
    fact_content: The fact or preference details to remember
    category: Category tag ('fact', 'preference', 'project', 'routine')
    """
    return memory_manager.remember(topic=topic, content=fact_content, category=category)

@tool(description="Recall or search for saved user preferences, notes, or facts in long-term memory.")
def recall_user_facts(query: str) -> str:
    """
    Search saved memories.
    query: The query or topic to search for in memory
    """
    return memory_manager.recall(query=query)

@tool(description="Forget or delete a previously saved user memory or fact by topic name.")
def forget_user_fact(topic: str) -> str:
    """
    Delete a saved fact.
    topic: The topic name or key to delete from memory
    """
    return memory_manager.forget(topic=topic)

@tool(description="List all stored user memories, preferences, and facts.")
def list_all_user_memories() -> str:
    """List all stored memories."""
    return memory_manager.list_all()
