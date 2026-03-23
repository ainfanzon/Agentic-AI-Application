import psycopg
from sentence_transformers import SentenceTransformer

# 1. Initialize the model (using the same 384-dim model from our schema)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Replace this with your actual connection string
DB_URL = "postgresql://root@localhost:26270/analysis?sslmode=disable"

# Diverse phrases to help the C-SPANN index determine its partitions
sample_data = [
    "User likes coffee and morning routines",
    "User lives in New York and works in tech",
    "System initialization and memory check",
    "Meeting scheduled for tomorrow at 5pm",
    "Project roadmap for the 2026 Q1 release",
    "Password reset request and security logs",
    "Hiking in the Pacific Northwest trails",
    "Technical error log regarding database connection",
    "Customer support chat regarding billing",
    "Vegetarian recipes for high-protein diets"
]

def seed_database():
    try:
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                print("🧹 Cleaning up old seed data (if any)...")
                cur.execute("DELETE FROM public.swarm_memory WHERE user_id LIKE 'seed_user_%'")
                
                print("🌱 Generating and inserting diverse embeddings...")
                for i, text in enumerate(sample_data):
                    # Generate raw embedding list
                    embedding_list = model.encode(text).tolist()
                    
                    # FIX: Manually format as a string with square brackets for CockroachDB
                    # Converting [0.1, 0.2] -> "[0.1, 0.2]"
                    vector_string = f"[{','.join(map(str, embedding_list))}]"
                    
                    cur.execute("""
                        INSERT INTO public.swarm_memory 
                        (user_id, memory_key, memory_value, embedding)
                        VALUES (%s, %s, %s, %s)
                    """, (f"seed_user_{i}", f"key_{i}", text, vector_string))
                
                conn.commit()
                print(f"✅ Successfully seeded {len(sample_data)} diverse memories.")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")

if __name__ == "__main__":
    seed_database()
