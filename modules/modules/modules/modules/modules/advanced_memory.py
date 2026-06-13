# modules/advanced_memory.py
"""
Advanced memory system with vector embedding (semantic search) + fact storage
Requires: pip install chromadb sqlite-utils sentence-transformers
"""

import os
import json
import hashlib
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

# Try to import ChromaDB for vector search
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

class AdvancedMemory:
    def __init__(self, persist_dir: str = "~/.nexcorix/memory_db"):
        """
        Inisialisasi memory system dengan SQLite + ChromaDB (opsional)
        """
        self.persist_dir = os.path.expanduser(persist_dir)
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # SQLite untuk metadata dan fakta
        self.sql_path = os.path.join(self.persist_dir, "metadata.db")
        self.conn = sqlite3.connect(self.sql_path)
        self._init_sql()
        
        # ChromaDB untuk vector search (jika tersedia)
        self.client = None
        self.collection = None
        if CHROMA_AVAILABLE:
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"  # Model ringan, bisa diganti
            )
            self.collection = self.client.get_or_create_collection(
                name="nexcorix_memories",
                embedding_function=self.embed_fn
            )
    
    def _init_sql(self):
        """Inisialisasi tabel SQLite"""
        # Tabel untuk memori teks biasa
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT,
                importance INTEGER DEFAULT 1,
                timestamp REAL,
                user_id TEXT DEFAULT 'default',
                channel TEXT DEFAULT 'default'
            )
        """)
        # Tabel untuk fakta terstruktur (subject - predicate - object)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id TEXT PRIMARY KEY,
                subject TEXT,
                predicate TEXT,
                object TEXT,
                timestamp REAL,
                user_id TEXT DEFAULT 'default'
            )
        """)
        # Tabel untuk ringkasan percakapan (memory compaction)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS summaries (
                id TEXT PRIMARY KEY,
                summary TEXT,
                date_range TEXT,
                timestamp REAL
            )
        """)
        self.conn.commit()
    
    # ==================== MEMORY TEKS ====================
    def add(self, content: str, importance: int = 1, user_id: str = "default", channel: str = "default") -> str:
        """
        Tambah memori teks. Jika ChromaDB tersedia, akan disimpan juga sebagai vector.
        """
        mem_id = hashlib.md5(f"{content}{datetime.now().isoformat()}{user_id}".encode()).hexdigest()
        
        # Simpan ke SQLite
        self.conn.execute(
            "INSERT OR REPLACE INTO memories (id, content, importance, timestamp, user_id, channel) VALUES (?,?,?,?,?,?)",
            (mem_id, content, importance, datetime.now().timestamp(), user_id, channel)
        )
        self.conn.commit()
        
        # Simpan ke ChromaDB jika tersedia
        if self.collection:
            self.collection.upsert(
                documents=[content],
                metadatas=[{
                    "importance": importance,
                    "user_id": user_id,
                    "channel": channel,
                    "timestamp": datetime.now().timestamp()
                }],
                ids=[mem_id]
            )
        return mem_id
    
    def search(self, query: str, top_k: int = 5, user_id: Optional[str] = None) -> List[str]:
        """
        Cari memori relevan secara semantik (vector search) atau fallback ke LIKE
        """
        # Jika ChromaDB tersedia, gunakan semantic search
        if self.collection:
            where_filter = {"user_id": user_id} if user_id else None
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    where=where_filter
                )
                if results and results['documents'] and results['documents'][0]:
                    return results['documents'][0]
            except Exception as e:
                print(f"[Memory] ChromaDB error: {e}, fallback ke LIKE")
        
        # Fallback: pencarian teks biasa (LIKE)
        sql = "SELECT content FROM memories WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?"
        params = (f"%{query}%", top_k)
        if user_id:
            sql = "SELECT content FROM memories WHERE content LIKE ? AND user_id = ? ORDER BY timestamp DESC LIMIT ?"
            params = (f"%{query}%", user_id, top_k)
        cursor = self.conn.execute(sql, params)
        return [row[0] for row in cursor.fetchall()]
    
    def get_recent(self, limit: int = 10, user_id: Optional[str] = None) -> List[str]:
        """Ambil memori terbaru"""
        if user_id:
            cursor = self.conn.execute(
                "SELECT content FROM memories WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            )
        else:
            cursor = self.conn.execute("SELECT content FROM memories ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [row[0] for row in cursor.fetchall()]
    
    def delete_memory(self, memory_id: str) -> bool:
        """Hapus memori berdasarkan ID"""
        try:
            self.conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            self.conn.commit()
            if self.collection:
                self.collection.delete(ids=[memory_id])
            return True
        except:
            return False
    
    # ==================== FAKTA TERSTRUKTUR ====================
    def add_fact(self, subject: str, predicate: str, obj: str, user_id: str = "default") -> str:
        """
        Tambah fakta terstruktur (contoh: "Claw suka Python")
        """
        fact_id = hashlib.md5(f"{subject}{predicate}{obj}{user_id}".encode()).hexdigest()
        self.conn.execute(
            "INSERT OR REPLACE INTO facts (id, subject, predicate, object, timestamp, user_id) VALUES (?,?,?,?,?,?)",
            (fact_id, subject, predicate, obj, datetime.now().timestamp(), user_id)
        )
        self.conn.commit()
        # Otomatis tambahkan ke memori teks juga agar lebih mudah ditemukan
        self.add(f"Fakta: {subject} {predicate} {obj}", importance=2, user_id=user_id)
        return fact_id
    
    def get_facts(self, subject: Optional[str] = None, user_id: str = "default") -> List[Dict]:
        """Ambil fakta terstruktur"""
        if subject:
            cursor = self.conn.execute(
                "SELECT subject, predicate, object FROM facts WHERE subject = ? AND user_id = ?",
                (subject, user_id)
            )
        else:
            cursor = self.conn.execute(
                "SELECT subject, predicate, object FROM facts WHERE user_id = ?",
                (user_id,)
            )
        return [{"subject": r[0], "predicate": r[1], "object": r[2]} for r in cursor.fetchall()]
    
    def delete_fact(self, subject: str, predicate: str, obj: str, user_id: str = "default") -> bool:
        """Hapus fakta"""
        fact_id = hashlib.md5(f"{subject}{predicate}{obj}{user_id}".encode()).hexdigest()
        try:
            self.conn.execute("DELETE FROM facts WHERE id = ?", (fact_id,))
            self.conn.commit()
            return True
        except:
            return False
    
    # ==================== MEMORY COMPACTION ====================
    def add_summary(self, summary: str, date_range: str) -> str:
        """Simpan ringkasan percakapan (memory compaction)"""
        sum_id = hashlib.md5(f"{summary}{date_range}".encode()).hexdigest()
        self.conn.execute(
            "INSERT OR REPLACE INTO summaries (id, summary, date_range, timestamp) VALUES (?,?,?,?)",
            (sum_id, summary, date_range, datetime.now().timestamp())
        )
        self.conn.commit()
        return sum_id
    
    def get_summaries(self, limit: int = 5) -> List[str]:
        """Ambil ringkasan terbaru"""
        cursor = self.conn.execute("SELECT summary FROM summaries ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [row[0] for row in cursor.fetchall()]
    
    # ==================== UTILITY ====================
    def clear_all(self, user_id: Optional[str] = None):
        """Hapus semua memori (hati-hati!)"""
        if user_id:
            self.conn.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
            self.conn.execute("DELETE FROM facts WHERE user_id = ?", (user_id,))
            if self.collection:
                # Hapus dari ChromaDB: butuh list ID, cukup repot, jadi skip dulu
                pass
        else:
            self.conn.execute("DELETE FROM memories")
            self.conn.execute("DELETE FROM facts")
            self.conn.execute("DELETE FROM summaries")
            if self.collection:
                # Hapus semua koleksi? Lebih aman buat ulang
                self.client.delete_collection("nexcorix_memories")
                self.collection = self.client.create_collection("nexcorix_memories", embedding_function=self.embed_fn)
        self.conn.commit()
    
    def get_stats(self) -> Dict:
        """Statistik memory"""
        mem_count = self.conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        fact_count = self.conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
        return {
            "total_memories": mem_count,
            "total_facts": fact_count,
            "chroma_available": CHROMA_AVAILABLE and self.collection is not None
        }
