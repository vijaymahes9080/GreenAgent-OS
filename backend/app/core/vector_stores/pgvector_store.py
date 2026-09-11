"""
pgvector Store Adapter for GreenAgent OS Semantic Cache
Connects to PostgreSQL pgvector extensions for scalable HNSW vector indexing.
"""
from typing import List, Dict, Any, Optional


class PgVectorSemanticStore:
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string

    def get_ddl_schema(self) -> str:
        """Returns the PostgreSQL DDL for setting up pgvector semantic caching."""
        return """
        CREATE EXTENSION IF NOT EXISTS vector;
        
        CREATE TABLE IF NOT EXISTS greenagent_semantic_cache (
            id VARCHAR(64) PRIMARY KEY,
            key_hash VARCHAR(64) UNIQUE NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            model VARCHAR(64) NOT NULL,
            embedding vector(128),
            hit_count INTEGER DEFAULT 0,
            tokens_saved INTEGER DEFAULT 0,
            energy_saved_joules FLOAT DEFAULT 0.0,
            carbon_saved_grams FLOAT DEFAULT 0.0,
            expires_at TIMESTAMPTZ NOT NULL
        );
        
        CREATE INDEX IF NOT EXISTS idx_semantic_cache_hnsw 
        ON greenagent_semantic_cache USING hnsw (embedding vector_cosine_ops);
        """
