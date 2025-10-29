"""Sovereign Memory System - Complete Implementation"""
from datetime import datetime
from typing import Dict, List, Optional
import json
import os


class MemoryLibrary:
    """Physically stores memory items in an in-memory dictionary."""

    def __init__(self) -> None:
        self.memories: Dict[str, Dict[str, object]] = {}

    def store(self, memory_id: str, content: str, metadata: Dict[str, object]) -> None:
        """Store a memory entry keyed by ``memory_id``."""
        self.memories[memory_id] = {
            "content": content,
            "metadata": dict(metadata) if metadata is not None else {},
            "timestamp": datetime.utcnow(),
        }

    def retrieve(self, memory_id: str) -> Optional[Dict[str, object]]:
        """Return the stored memory dictionary for ``memory_id`` if present."""
        return self.memories.get(memory_id)

    def list_all_ids(self) -> List[str]:
        """Return a list of all stored memory identifiers."""
        return list(self.memories.keys())


class PersistentMemoryLibrary(MemoryLibrary):
    """Extends MemoryLibrary to save to JSON file"""
    
    def __init__(self, storage_file="ai_memories.json"):
        super().__init__()
        self.storage_file = storage_file
        self.load_from_disk()
    
    def load_from_disk(self):
        """Load memories from file when system starts"""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                for memory_id, memory in data.items():
                    memory['timestamp'] = datetime.fromisoformat(memory['timestamp'])
                self.memories = data
    
    def save_to_disk(self):
        """Save all memories to file"""
        save_data = {}
        for memory_id, memory in self.memories.items():
            save_data[memory_id] = {
                'content': memory['content'],
                'metadata': memory['metadata'],
                'timestamp': memory['timestamp'].isoformat()
            }
        
        with open(self.storage_file, 'w') as f:
            json.dump(save_data, f, indent=2)
    
    def store(self, memory_id: str, content: str, metadata: Dict[str, object]) -> None:
        """Override store to automatically persist"""
        super().store(memory_id, content, metadata)
        self.save_to_disk()


class MemoryArchiver:
    """Interacts with the MemoryLibrary to store and retrieve memories."""

    def __init__(self, library: MemoryLibrary) -> None:
        self.library = library

    def save_memory(self, memory_id: str, content: str, metadata: Dict[str, object]) -> None:
        """Persist a memory via the underlying library."""
        self.library.store(memory_id, content, metadata)

    def load_memory(self, memory_id: str) -> Optional[Dict[str, object]]:
        """Retrieve a memory from the library."""
        return self.library.retrieve(memory_id)


class SearchableMemoryArchiver(MemoryArchiver):
    """Adds search functionality to the archiver"""
    
    def search_memories(self, query: str) -> List[Dict[str, object]]:
        """Search memory contents for the query string"""
        results = []
        for memory_id in self.library.list_all_ids():
            memory = self.library.retrieve(memory_id)
            if memory and query.lower() in memory['content'].lower():
                results.append(memory)
        return results


class MemoryLibrarian:
    """Decides whether a given memory should be kept or discarded."""

    def __init__(self, archiver: MemoryArchiver) -> None:
        self.archiver = archiver

    def decide_action(self, memory_data: Dict[str, object]) -> str:
        """Determine whether to keep or discard ``memory_data``."""
        metadata = memory_data.get("metadata", {}) if memory_data else {}
        if isinstance(metadata, dict):
            if metadata.get("type") == "preference":
                return "KEEP"
            if metadata.get("important") is True:
                return "KEEP"
        return "DISCARD"

    def purge_unimportant(self) -> None:
        """Report which stored memories should be kept or discarded."""
        for memory_id in self.archiver.library.list_all_ids():
            memory = self.archiver.load_memory(memory_id)
            decision = self.decide_action(memory if memory else {})
            verdict = "kept" if decision == "KEEP" else "discarded"
            print(f"Memory '{memory_id}' should be {verdict}.")


class SimpleAIMemoryInterface:
    """Simple interface that any AI can use through plain text"""
    
    def __init__(self, archiver, librarian):
        self.archiver = archiver
        self.librarian = librarian
    
    def ai_save_memory(self, content, memory_type="general", important=False):
        """AI calls this to save a memory - returns the memory ID"""
        memory_id = f"memory_{len(self.archiver.library.memories) + 1}"
        metadata = {
            "type": memory_type,
            "important": important,
            "source": "ai_autonomous"
        }
        
        self.archiver.save_memory(memory_id, content, metadata)
        return f"Memory saved as {memory_id}"
    
    def ai_recall_memories(self, query=None):
        """AI calls this to recall memories - returns formatted text"""
        if query:
            memories = self.archiver.search_memories(query)
        else:
            memory_ids = self.archiver.library.list_all_ids()
            memories = [self.archiver.load_memory(mid) for mid in memory_ids]
            memories = [m for m in memories if m is not None]
        
        if not memories:
            return "No memories found."
        
        result = "RECALLED MEMORIES:\n"
        for memory in memories:
            result += f"- {memory['content']} (Type: {memory['metadata'].get('type', 'unknown')})\n"
        return result
    
    def ai_consult_librarian(self, content, context=None):
        """AI asks librarian whether to remember something"""
        test_memory = {
            "content": content,
            "metadata": {"context": context} if context else {}
        }
        decision = self.librarian.decide_action(test_memory)
        return f"Librarian decision: {decision}"


def test_original_system():
    """Test the original system functionality"""
    print("=== ORIGINAL SYSTEM TEST ===")
    library = MemoryLibrary()
    archiver = MemoryArchiver(library)
    librarian = MemoryLibrarian(archiver)

    # Store diverse memories
    archiver.save_memory(
        "morning_beverage",
        "I prefer coffee with oat milk in the morning.",
        {"type": "preference"},
    )
    archiver.save_memory(
        "project_deadline",
        "Submit the research proposal by Friday.",
        {"important": True, "type": "task"},
    )
    archiver.save_memory(
        "passing_thought",
        "Saw a blue jay during lunch.",
        {"type": "observation", "important": False},
    )

    # Evaluate each stored memory via the librarian helper
    librarian.purge_unimportant()


def test_enhanced_system():
    """Test the enhanced system with AI interface"""
    print("\n" + "="*50)
    print("ENHANCED SYSTEM TEST WITH AI INTERFACE")
    print("="*50)
    
    # Use the persistent library
    library = PersistentMemoryLibrary("sovereign_memories.json")
    archiver = SearchableMemoryArchiver(library)
    librarian = MemoryLibrarian(archiver)
    ai_interface = SimpleAIMemoryInterface(archiver, librarian)
    
    print("🤖 AI: I'm going to save some important memories...")
    
    # AI saves memories autonomously
    print(ai_interface.ai_save_memory(
        "User has a severe allergy to peanuts", 
        "health", 
        important=True
    ))
    
    print(ai_interface.ai_save_memory(
        "User enjoys reading science fiction and philosophy books",
        "preference",
        important=True  
    ))
    
    print(ai_interface.ai_save_memory(
        "It's currently raining outside",
        "observation", 
        important=False
    ))
    
    print("\n🤖 AI: Let me recall health-related information...")
    print(ai_interface.ai_recall_memories("allergy"))
    
    print("\n🤖 AI: Consulting librarian about a new memory...")
    print(ai_interface.ai_consult_librarian("User mentioned they love hiking on weekends"))
    
    print("\n🤖 AI: Here are all my current memories:")
    print(ai_interface.ai_recall_memories())
    
    print("\n📊 Librarian reviewing all stored memories:")
    librarian.purge_unimportant()
    
    print(f"\n💾 Memories saved to: sovereign_memories.json")
    print("✅ SOVEREIGN MEMORY SYSTEM IS OPERATIONAL!")


if __name__ == "__main__":
    test_original_system()
    test_enhanced_system()
