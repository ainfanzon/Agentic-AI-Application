import os
import psycopg
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# 1. Silencing the parallelism warnings for a cleaner demo log
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 2. OPTIONAL: Set HF_TOKEN if you want to bypass rate limits
# os.environ["HF_TOKEN"] = "your_token_here"

load_dotenv()

# Global model instance (loaded once on service start)
model = SentenceTransformer('all-MiniLM-L6-v2')

class VectorMemory:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

    def _format_vector(self, vector):
        """Formats a list of floats into CockroachDB's [0.1, 0.2] string format."""
        return f"[{','.join(map(str, vector))}]"

    def search(self, user_id, query_text, limit=5):
        """Semantic search using the <=> Cosine Distance operator."""
        # CPU WORK FIRST: Generate embedding before opening DB connection
        query_vector = model.encode(query_text).tolist()
        vector_str = self._format_vector(query_vector)

        # DB WORK SECOND: Fast connect/query/close to prevent timeouts
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

class VectorMemory:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

    def _format_vector(self, vector):
        """Formats a list of floats into CockroachDB's [0.1, 0.2] string format."""
        return f"[{','.join(map(str, vector))}]"

    def search(self, user_id, query_text, limit=5):
        """Semantic search using the <=> Cosine Distance operator."""
        # CPU WORK FIRST: Generate embedding before opening DB connection
        query_vector = model.encode(query_text).tolist()
        vector_str = self._format_vector(query_vector)

        # DB WORK SECOND: Fast connect/query/close to prevent timeouts
        with psycopg.connect(self.db_url, connect_timeout=10) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT memory_key, memory_value, full_report_text, 1 - (embedding <=> %s) as similarity
                    FROM public.swarm_memory
                    WHERE user_id = %s
                    ORDER BY embedding <=> %s ASC
                    LIMIT %s;
                """, (vector_str, user_id, vector_str, limit))
                return cur.fetchall()

    async def add_memory(self, user_id, key, value, full_report_text=None):
        """Vectorizes and stores a new memory, including the full report."""
        vector = model.encode(value).tolist()
        vector_str = self._format_vector(vector)

        with psycopg.connect(self.db_url, connect_timeout=10) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO public.swarm_memory (
                        user_id, memory_key, memory_value, full_report_text, embedding
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, memory_key) 
                    DO UPDATE SET 
                        memory_value = EXCLUDED.memory_value, 
                        full_report_text = EXCLUDED.full_report_text,
                        embedding = EXCLUDED.embedding;
                """, (user_id, key, value, full_report_text, vector_str))
            conn.commit()
