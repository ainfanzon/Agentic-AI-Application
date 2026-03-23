import os
import psycopg
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Silence the HF Hub warning for cleaner demo logs
os.environ["TOKENIZERS_PARALLELISM"] = "false"

load_dotenv()

# Global model instance - loaded once on service start
model = SentenceTransformer('all-MiniLM-L6-v2')

class VectorMemory:
    def __init__(self):
        # Ensure your .env has the correct port (usually 26257)
        self.db_url = os.getenv("DATABASE_URL")

    def _format_vector(self, vector):
        """Formats a list of floats into CockroachDB's [0.1, 0.2] string format."""
        return f"[{','.join(map(str, vector))}]"

    def search(self, user_id, query_text, limit=5):
        """Semantic search using the <=> Cosine Distance operator."""
        # 1. CPU-intensive work: Generate the embedding first
        query_vector = model.encode(query_text).tolist()
        vector_str = self._format_vector(query_vector)

        # 2. Database work: Open connection ONLY when ready to query
        # Added connect_timeout to handle local node latency
        with psycopg.connect(self.db_url, connect_timeout=10) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT memory_key, memory_value, 1 - (embedding <=> %s) as similarity
                    FROM public.swarm_memory
                    WHERE user_id = %s
                    ORDER BY embedding <=> %s ASC
                    LIMIT %s;
                """, (vector_str, user_id, vector_str, limit))
                return cur.fetchall()

    def add_memory(self, user_id, key, value):
        """Vectorizes and stores a new memory."""
        # 1. CPU-intensive work: Generate the embedding first
        vector = model.encode(value).tolist()
        vector_str = self._format_vector(vector)

        # 2. Database work: Open connection ONLY when ready to write
        with psycopg.connect(self.db_url, connect_timeout=10) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO public.swarm_memory (user_id, memory_key, memory_value, embedding)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id, memory_key) 
                    DO UPDATE SET 
                        memory_value = EXCLUDED.memory_value, 
                        embedding = EXCLUDED.embedding,
                        last_accessed = CURRENT_TIMESTAMP;
                """, (user_id, key, value, vector_str))
            conn.commit()
