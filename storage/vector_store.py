import os
import json
import sqlite3
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

from config.settings import ResearchConfig
from research.state import ResearchSession

class VectorStore:
    """Local vector store for research sessions using SQLite and sentence transformers."""
    
    def __init__(self, config: ResearchConfig, db_path: str = "research_history.db"):
        self.config = config
        self.db_path = db_path
        self.model = None
        self._init_database()
    
    def _get_model(self) -> SentenceTransformer:
        """Lazy load the sentence transformer model."""
        if self.model is None:
            try:
                self.model = SentenceTransformer(self.config.embedding_model)
                # Move model to CPU to avoid meta tensor issues
                self.model = self.model.to('cpu')
            except Exception as e:
                print(f"Error loading embedding model: {e}")
                # Fallback to a simpler model
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.model = self.model.to('cpu')
        return self.model
    
    def _init_database(self):
        """Initialize SQLite database with tables for research sessions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create research sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS research_sessions (
                    id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    sources TEXT NOT NULL,  -- JSON array
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    config TEXT,  -- JSON object
                    embedding BLOB  -- Numpy array as bytes
                )
            """)
            
            # Create index on created_at for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON research_sessions(created_at)
            """)
            
            conn.commit()
    
    def _serialize_embedding(self, embedding: np.ndarray) -> bytes:
        """Serialize numpy array to bytes for storage."""
        return embedding.tobytes()
    
    def _deserialize_embedding(self, embedding_bytes: bytes) -> np.ndarray:
        """Deserialize bytes back to numpy array."""
        return np.frombuffer(embedding_bytes, dtype=np.float32)
    
    def add_session(self, session: ResearchSession) -> bool:
        """Add a research session to the vector store."""
        try:
            # Generate embedding for the topic and summary
            model = self._get_model()
            text_to_embed = f"{session.topic}\n\n{session.summary}"
            embedding = model.encode(text_to_embed, convert_to_numpy=True)
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO research_sessions 
                    (id, topic, summary, sources, created_at, completed_at, config, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.id,
                    session.topic,
                    session.summary,
                    json.dumps(session.sources),
                    session.created_at.isoformat(),
                    session.completed_at.isoformat() if session.completed_at else None,
                    json.dumps(session.config) if session.config else None,
                    self._serialize_embedding(embedding)
                ))
                conn.commit()
            
            return True
            
        except Exception as e:
            print(f"Error adding session to vector store: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[ResearchSession]:
        """Retrieve a specific research session by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, topic, summary, sources, created_at, completed_at, config
                    FROM research_sessions 
                    WHERE id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                if row:
                    return ResearchSession(
                        id=row[0],
                        topic=row[1],
                        summary=row[2],
                        sources=json.loads(row[3]),
                        created_at=datetime.fromisoformat(row[4]),
                        completed_at=datetime.fromisoformat(row[5]) if row[5] else None,
                        config=json.loads(row[6]) if row[6] else None
                    )
            
            return None
            
        except Exception as e:
            print(f"Error retrieving session: {e}")
            return None
    
    def get_recent_sessions(self, limit: int = 10) -> List[ResearchSession]:
        """Get recent research sessions."""
        try:
            sessions = []
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, topic, summary, sources, created_at, completed_at, config
                    FROM research_sessions 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
                
                for row in cursor.fetchall():
                    sessions.append(ResearchSession(
                        id=row[0],
                        topic=row[1],
                        summary=row[2],
                        sources=json.loads(row[3]),
                        created_at=datetime.fromisoformat(row[4]),
                        completed_at=datetime.fromisoformat(row[5]) if row[5] else None,
                        config=json.loads(row[6]) if row[6] else None
                    ))
            
            return sessions
            
        except Exception as e:
            print(f"Error retrieving recent sessions: {e}")
            return []
    
    def search_similar(self, query: str, limit: int = 5, threshold: float = 0.3) -> List[Tuple[ResearchSession, float]]:
        """Search for similar research sessions using vector similarity."""
        try:
            # Generate embedding for query
            model = self._get_model()
            query_embedding = model.encode(query, convert_to_numpy=True)
            
            # Get all sessions with embeddings
            results = []
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, topic, summary, sources, created_at, completed_at, config, embedding
                    FROM research_sessions 
                    WHERE embedding IS NOT NULL
                    ORDER BY created_at DESC
                """)
                
                for row in cursor.fetchall():
                    # Deserialize embedding
                    session_embedding = self._deserialize_embedding(row[7])
                    
                    # Calculate similarity
                    similarity = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        session_embedding.reshape(1, -1)
                    )[0][0]
                    
                    if similarity >= threshold:
                        session = ResearchSession(
                            id=row[0],
                            topic=row[1],
                            summary=row[2],
                            sources=json.loads(row[3]),
                            created_at=datetime.fromisoformat(row[4]),
                            completed_at=datetime.fromisoformat(row[5]) if row[5] else None,
                            config=json.loads(row[6]) if row[6] else None
                        )
                        results.append((session, similarity))
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]
            
        except Exception as e:
            print(f"Error searching similar sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a research session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM research_sessions WHERE id = ?", (session_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total sessions
                cursor.execute("SELECT COUNT(*) FROM research_sessions")
                total_sessions = cursor.fetchone()[0]
                
                # Sessions with embeddings
                cursor.execute("SELECT COUNT(*) FROM research_sessions WHERE embedding IS NOT NULL")
                sessions_with_embeddings = cursor.fetchone()[0]
                
                # Recent activity (last 7 days)
                cursor.execute("""
                    SELECT COUNT(*) FROM research_sessions 
                    WHERE created_at >= datetime('now', '-7 days')
                """)
                recent_sessions = cursor.fetchone()[0]
                
                return {
                    "total_sessions": total_sessions,
                    "sessions_with_embeddings": sessions_with_embeddings,
                    "recent_sessions": recent_sessions,
                    "embedding_model": self.config.embedding_model,
                    "embedding_dimension": self.config.embedding_dimension
                }
                
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def cleanup_old_sessions(self, keep_recent: int = 100) -> int:
        """Clean up old sessions, keeping only the most recent ones."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get count before cleanup
                cursor.execute("SELECT COUNT(*) FROM research_sessions")
                before_count = cursor.fetchone()[0]
                
                # Delete old sessions
                cursor.execute("""
                    DELETE FROM research_sessions 
                    WHERE id NOT IN (
                        SELECT id FROM research_sessions 
                        ORDER BY created_at DESC 
                        LIMIT ?
                    )
                """, (keep_recent,))
                
                conn.commit()
                
                # Get count after cleanup
                cursor.execute("SELECT COUNT(*) FROM research_sessions")
                after_count = cursor.fetchone()[0]
                
                return before_count - after_count
                
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")
            return 0

def create_vector_store(config: ResearchConfig) -> VectorStore:
    """Create a vector store instance."""
    return VectorStore(config)

