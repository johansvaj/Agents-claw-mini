import hashlib
try:
    import chromadb
    from chromadb.utils import embedding_functions
    ADV_MEMORY_AVAILABLE = True
except ImportError:
    ADV_MEMORY_AVAILABLE = False

class AdvancedMemory:
    def __init__(self, persist_dir: str = "~/.nexcorix/adv_memory"):
        if not ADV_MEMORY_AVAILABLE:
            raise ImportError("chromadb not installed")
        import os
        self.persist_dir = os.path.expanduser(persist_dir)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection("advanced_memory", embedding_function=self.embed_fn)
    def add(self, text: str, metadata: dict = None):
        mem_id = hashlib.md5(f"{text}{metadata}".encode()).hexdigest()
        self.collection.upsert(documents=[text], metadatas=[metadata or {}], ids=[mem_id])
    def search(self, query: str, top_k: int = 5):
        results = self.collection.query(query_texts=[query], n_results=top_k)
        return results['documents'][0] if results['documents'] else []
