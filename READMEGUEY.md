To create a downloadable `README.md` file, I have formatted the content into a single, clean block below. You can copy this text, save it as a file named `README.md` in your project root, and it will be ready for your repository.

---

```markdown
# 🐝 Autonomous Analyst Swarm
### Multi-Agent SaaS Intelligence Platform (CockroachDB + Tavily + LangGraph)

This repository contains a decentralized multi-agent system designed to bridge the gap between internal database metrics and external market intelligence. The swarm automates the lifecycle of business data analysis: from planning and SQL execution to web research and visualization.

---

## 🏗 System Architecture

The swarm utilizes a **StateGraph** orchestration pattern. Instead of a linear script, agents hand off control based on a shared "State" object, allowing for loops, error correction, and hybrid data merging.

### The Workflow
1. **Planner** creates a roadmap.
2. **Schema Agent** maps the database.
3. **SQL Specialist** extracts the raw numbers.
4. **Web Researcher** fetches real-world benchmarks.
5. **Analysis Agent** synthesizes data and generates a `.png` chart.
6. **Critic** produces the final Executive Summary.

---

## 🤖 Agent Descriptions

| Agent | Technology | Primary Responsibility |
| :--- | :--- | :--- |
| **Planner** | Llama 3 | Analyzes the user query and generates a multi-step execution plan. |
| **Schema Agent** | SQLAlchemy | Inspects CockroachDB to provide table metadata to the swarm. |
| **SQL Specialist** | LangChain / SQL | Generates and executes dialect-specific SQL (Postgres/CockroachDB). |
| **Web Researcher**| Tavily AI | Searches for SaaS industry growth, CAGR, and market trends. |
| **Analysis Agent** | Pandas / Seaborn | Cleans data and generates "Internal vs. Benchmark" visualizations. |
| **Critic** | Llama 3 | Acts as the senior analyst to provide the final report and quality check. |

---

## 🚀 Sample Prompts

To see the swarm in action via the Streamlit dashboard, try the following inputs:

* **Market Comparison**: *"Show me a revenue trend for the last 6 months and compare our performance against current SaaS industry growth benchmarks for 2025-2026."*
* **Contextual Analysis**: *"Analyze our revenue from the last 6 months. Identify the month with the lowest revenue and search the web for any major market events that happened during that month to explain the dip."*
* **Future Projection**: *"Based on our revenue for the last half-year, what is our projected year-end total? Compare this projection with industry forecasts found on the web."*

---

## 🛠 Tech Stack

- **Orchestration**: [LangGraph](https://python.langchain.com/docs/langgraph)
- **Database**: CockroachDB (Local Cluster)
- **Web Search**: Tavily AI (AI-native search)
- **UI/UX**: Streamlit
- **LLM**: Llama 3 (Ollama)
- **Data Visualization**: Seaborn & Matplotlib (Agg Backend)

---

## 📂 Project Layout

```text
autonomous_analyst/
├── artifacts/            # Generated charts and reports
├── services/
│   └── agent_orchestrator/
│       ├── agents/       # Individual Python agent logic
│       ├── graph.py      # LangGraph state machine definition
│       └── state.py      # TypedDict Shared State schema
├── app.py                # Streamlit Dashboard UI
├── main.py               # Terminal-based entry point
└── .env                  # API Keys (TAVILY_API_KEY)

```

---

## ⚙️ Installation & Setup

1. **Clone the repo and install dependencies:**
```bash
uv add streamlit pandas seaborn langgraph langchain-ollama tavily-python python-dotenv

```


2. **Set up your environment variables:**
Create a `.env` file with your `TAVILY_API_KEY`.
3. **Run the Dashboard:**
```bash
uv run streamlit run app.py

```



---

*Developed as an authentic, adaptive AI collaboration.*

```

***

### 💡 Pro-Tip
Since you are using **Streamlit**, you can actually add a button to your dashboard that allows users to download this information as a PDF or text file directly from the browser! 

**Would you like me to add a "Download README" or "Download Report" button to your `app.py`?**

```
