"""Simple Sovereign Memory System implementation.
"""
from datetime import datetime
from typing import Dict, List, Optional


class MemoryLibrary:
    """Physically stores memory items in an in-memory dictionary."""

    def __init__(self) -> None:
        self.memories: Dict[str, Dict[str, object]] = {}

    def store(self, memory_id: str, content: str, metadata: Dict[str, object]) -> None:
        """Store a memory entry keyed by ``memory_id``.

        Each stored memory includes the original content, metadata, and a timestamp
        marking when the memory was saved.
        """
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


class MemoryLibrarian:
    """Decides whether a given memory should be kept or discarded."""

    def __init__(self, archiver: MemoryArchiver) -> None:
        self.archiver = archiver

    def decide_action(self, memory_data: Dict[str, object]) -> str:
        """Determine whether to keep or discard ``memory_data``.

        ``memory_data`` is expected to include a ``metadata`` dictionary containing
        classification details about the memory.
        """
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


if __name__ == "__main__":
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