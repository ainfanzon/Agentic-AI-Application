Markdown
# Long-Term Memory Service (Project: Nexus-Mem)

![Version](https://img.shields.io/badge/version-0.1.0--baseline-blue)
![Database](https://img.shields.io/badge/Database-CockroachDB-green)
![Language](https://img.shields.io/badge/Language-Python-ffd343)

## 📌 Overview
Nexus-Mem is a long-term memory retrieval system designed to store and recall historical user interactions. This baseline version (v0.1.0) utilizes traditional SQL pattern matching for information retrieval.

The project is currently undergoing a phased migration from **Keyword-based Search (ILIKE)** to **Semantic Vector Search** using CockroachDB's native vector capabilities.

---

## 🛠 Current Architecture (Baseline v0.1.0)
The current system relies on exact or partial string matching to retrieve historical context.

* **Search Engine:** CockroachDB `ILIKE` operator.
* **Logic:** Standard SQL pattern matching: `WHERE content ILIKE '%query%'`.
* **Pros:** Low computational overhead, easy to implement, deterministic.
* **Cons:** No conceptual understanding (e.g., searching "automobile" will not find "car").

### Data Schema
```sql
CREATE TABLE user_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
🚀 The Vector Migration Roadmap
We are transitioning to a High-Dimensional Vector Space to enable semantic memory retrieval.

Phase 1: Embedding Integration (Current)
Integrate sentence-transformers (Python) to convert text into 384-dimension vectors.

Update CockroachDB schema to include the VECTOR data type.

Phase 2: Indexing & Optimization
Implement C-SPANN (Approximate Nearest Neighbor) indexing.

Benchmark Cosine Similarity (<=>) vs. Euclidean Distance (<->).

Phase 3: Hybrid Search
Combine ILIKE keyword filtering with Vector Search for maximum precision.

🏗 Installation & Setup
Clone the repository:

Bash
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name
Install Baseline Dependencies:

Bash
pip install -r requirements.txt
Environment Variables:
Create a .env file with your CockroachDB connection string:

Code snippet
DATABASE_URL=postgresql://user:pass@host:port/dbname
📈 Evaluation Metrics
Success will be measured by comparing the Recall@K of the new Vector Search against this baseline. We aim to increase retrieval relevance for natural language queries by >40%.

Author: [Your Name/Handle]

Status: 🟠 Migration to Vector Search in Progress


---

### How to apply this to your repo:
1. Save the text above as `README.md` in your project root.
2. Run the following to update your baseline:
   ```bash
   git add README.md
   git commit -m "docs: add baseline README with vector migration roadmap"
   git push origin main
