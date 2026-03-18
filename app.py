import os
import certifi
import asyncio
import streamlit as st
import time
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from fpdf import FPDF
from services.agent_orchestrator.graph import app as swarm_app
from services.mcp_host import call_cockroach_mcp  # Added for memory retrieval

# SSL Fix for Anaconda/Requests
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Ensure artifacts directory exists
os.makedirs("artifacts", exist_ok=True)

load_dotenv()

st.set_page_config(page_title="Autonomous Analyst Swarm", page_icon="🐝", layout="wide")

# --- Helper Functions ---
async def get_recent_memories():
    """Fetches the latest 5 memories directly from CockroachDB for the UI."""
    try:
        query = "SELECT memory_value, created_at FROM swarm_memory ORDER BY created_at DESC LIMIT 5"
        memories = await call_cockroach_mcp("execute_query", {"query": query})
        
        parsed_memories = []
        if isinstance(memories, dict):
            # Try to get rows from the dict keys or formatted_result string
            rows = memories.get("rows") or memories.get("result")
            if not rows and memories.get("formatted_result"):
                try:
                    rows = json.loads(memories["formatted_result"])
                except:
                    pass
            
            if isinstance(rows, list):
                parsed_memories = rows
        return parsed_memories
    except Exception as e:
        return [{"memory_value": f"Error loading memory: {e}", "created_at": ""}]

def generate_pdf(report_text, chart_path=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Autonomous Analyst Swarm - Executive Report", 
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    clean_text = report_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 8, clean_text)
    if chart_path and os.path.exists(chart_path):
        pdf.ln(10)
        pdf.image(chart_path, x=15, w=180)
    return pdf.output()

# --- Sidebar Controls ---
with st.sidebar:
    st.header("🧠 Long-Term Memory")
    st.caption("Historical insights from CockroachDB")
    
    # Memory Monitor Section
    if st.button("🔄 Refresh Memory"):
        # run the async fetch in the streamlit context
        recent_mems = asyncio.run(get_recent_memories())
        if recent_mems:
            for i, m in enumerate(recent_mems):
                with st.expander(f"Insight {i+1}"):
                    st.write(m.get("memory_value", "No content"))
                    st.caption(f"Stored: {m.get('created_at', 'unknown')}")
        else:
            st.info("No memories found yet.")
    
    if st.button("🗑️ Wipe All Memory", type="secondary"):
        asyncio.run(call_cockroach_mcp("execute_query", {"query": "DELETE FROM swarm_memory"}))
        st.success("Brain wiped!")
        st.rerun()

    st.divider()
    st.header("Controls")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.current_data_table = None
        st.rerun()
    
    st.divider()
    st.markdown("### Industry Sources")
    st.markdown("- [G Squared Partners](https://www.gsquaredpartners.com)\n- [Vena Solutions](https://www.venasolutions.com)\n- [Benchmarkit](https://www.benchmarkit.ai)")

# --- Main UI ---
st.title("Autonomous Analyst Swarm")
st.markdown("Querying **CockroachDB** + Searching **Tavily** + Generating Insights")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_data_table" not in st.session_state:
    st.session_state.current_data_table = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about revenue trends..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        report_placeholder = st.empty()
        with st.status("Swarm is waking up...", expanded=True) as status:
            initial_state = {
                "question": prompt, "plan": [], "strategy": "HYBRID_PATH",
                "data_context": [], "schema_info": {}, "iteration": 0,
                "artifacts": [], "analysis_results": "", "memory_context": ""
            }

            async def run_swarm():
                final_content = "No report generated."
                async for output in swarm_app.astream(initial_state):
                    for node_name, state_update in output.items():
                        status.write(f"Node **{node_name}** completed.")
                        if "analysis_results" in state_update and state_update["analysis_results"]:
                            final_content = state_update["analysis_results"]
                        if "last_df_data" in state_update:
                            st.session_state.current_data_table = state_update["last_df_data"]
                return final_content

            result_text = asyncio.run(run_swarm())
            status.update(label="Swarm Analysis Complete!", state="complete", expanded=False)

        report_placeholder.markdown(result_text)
        st.session_state.messages.append({"role": "assistant", "content": result_text})

        # --- DATA TABLE WITH FORECAST ---
        if st.session_state.current_data_table:
            with st.expander("📊 View Analyzed Data & 3-Month Forecast", expanded=False):
                display_df = pd.DataFrame(st.session_state.current_data_table)
                if 'month' in display_df.columns:
                    display_df['month'] = pd.to_datetime(display_df['month']).dt.strftime('%Y-%m-%d')
                
                st.dataframe(
                    display_df, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "amount": st.column_config.NumberColumn("Actual Revenue", format="$%d"),
                        "prediction": st.column_config.NumberColumn("Trend Prediction", format="$%d"),
                        "month": "Date"
                    }
                )
                
                csv = display_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Data & Forecast CSV",
                    data=csv,
                    file_name=f"forecast_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

        # Chart Display
        chart_path = "artifacts/revenue_trend.png"
        if os.path.exists(chart_path):
            with open(chart_path, "rb") as f:
                st.image(f.read(), caption="Revenue Trend vs Benchmarks")
        else:
            st.info("No chart generated.")

        # --- Download Section ---
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            pdf_bytes = generate_pdf(result_text, chart_path if os.path.exists(chart_path) else None)
            st.download_button("Download PDF", data=bytes(pdf_bytes), file_name="Report.pdf", use_container_width=True)
        with col2:
            st.download_button("Download Text", data=result_text, file_name="Report.txt", use_container_width=True)
