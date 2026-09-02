import uuid
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
import chromadb
from app.config import settings
from app.utils.logger import logger


class LongTermMemory:
    """Manages semantic (vector) long-term memory operations using ChromaDB."""

    def __init__(self, chroma_dir: Optional[Path] = None):
        self.chroma_dir = chroma_dir or settings.db.chromadb_dir
        self.client: Optional[chromadb.PersistentClient] = None
        self.collection: Optional[Any] = None

    def initialize(self) -> None:
        """Initializes the ChromaDB persistent client and collection. Call on startup."""
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        try:
            # PersistentClient stores vectors locally on disk
            self.client = chromadb.PersistentClient(path=str(self.chroma_dir))
            # Retrieve or construct the primary collection
            self.collection = self.client.get_or_create_collection(name="jarvis_memories")
            logger.info(f"ChromaDB initialized successfully at {self.chroma_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise e

    async def add_memory(
        self,
        text: str,
        category: str,
        metadata: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None
    ) -> str:
        """Asynchronously index a document in ChromaDB."""
        if not self.collection:
            self.initialize()

        mem_id = memory_id or str(uuid.uuid4())
        # Attach the structural classification tag
        meta = {"category": category}
        if metadata:
            meta.update(metadata)

        await asyncio.to_thread(self._add_memory_sync, text, meta, mem_id)
        return mem_id

    def _add_memory_sync(self, text: str, metadata: dict, mem_id: str) -> None:
        if self.collection is None:
            raise RuntimeError("ChromaDB collection is not initialized.")
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[mem_id]
        )

    async def search_memories(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Asynchronously search the closest semantic memories matching the query string."""
        if not self.collection:
            self.initialize()

        where = {"category": category} if category else None
        return await asyncio.to_thread(self._search_memories_sync, query, where, limit)

    def _search_memories_sync(
        self,
        query: str,
        where: Optional[dict],
        limit: int
    ) -> List[Dict[str, Any]]:
        if self.collection is None:
            raise RuntimeError("ChromaDB collection is not initialized.")
        
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=where
        )

        memories = []
        if not results or not results.get("documents") or not results["documents"][0]:
            return memories

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        ids = results["ids"][0]
        distances = results.get("distances", [[]])[0]

        for i in range(len(documents)):
            memories.append({
                "id": ids[i],
                "text": documents[i],
                "metadata": metadatas[i],
                "distance": distances[i] if i < len(distances) else None
            })
        return memories

    async def delete_memory(self, memory_id: str) -> None:
        """Asynchronously delete a memory item by ID."""
        if not self.collection:
            self.initialize()
        await asyncio.to_thread(self._delete_memory_sync, memory_id)

    def _delete_memory_sync(self, memory_id: str) -> None:
        if self.collection is None:
            raise RuntimeError("ChromaDB collection is not initialized.")
        self.collection.delete(ids=[memory_id])

    async def clear_all(self) -> None:
        """Asynchronously delete all indexed memories inside the collection."""
        if not self.collection:
            self.initialize()
        await asyncio.to_thread(self._clear_all_sync)

    def _clear_all_sync(self) -> None:
        if self.collection is None:
            raise RuntimeError("ChromaDB collection is not initialized.")
        all_data = self.collection.get()
        if all_data and all_data.get("ids"):
            self.collection.delete(ids=all_data["ids"])


# Shared instance
long_term_mem = LongTermMemory()
