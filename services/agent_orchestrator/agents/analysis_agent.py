import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from services.agent_orchestrator.state import AnalystState

# Set matplotlib to headless mode for server environments
plt.switch_backend('Agg')

def analysis_agent(state: AnalystState):
    print("📊 Analysis Agent: Synthesizing data and generating comparative chart...")
    
    data_context = state.get("data_context", [])
    print(f"DEBUG: Analysis Agent received context with {len(data_context)} items.")
    
    # 1. HYPER-RESILIENT DATA EXTRACTION
    db_data = None
    web_results = ""
    
    for entry in data_context:
        if isinstance(entry, str):
            if "WEB RESEARCH FINDINGS" in entry:
                web_results = entry
                continue
            if entry.strip().startswith(('{', '[')):
                try:
                    parsed = json.loads(entry)
                    if isinstance(parsed, dict) and "rows" in parsed:
                        db_data = parsed["rows"]
                        break
                    elif isinstance(parsed, list) and len(parsed) > 0:
                        db_data = parsed
                        break
                except Exception as e:
                    print(f"⚠️ Failed to parse JSON string: {e}")
        
        elif isinstance(entry, dict):
            if "rows" in entry:
                db_data = entry["rows"]
                break
            elif "formatted_result" in entry:
                try:
                    db_data = json.loads(entry["formatted_result"])
                    break
                except:
                    continue
            
        elif isinstance(entry, list) and len(entry) > 0 and isinstance(entry[0], dict):
            db_data = entry
            break

    if not db_data or len(db_data) == 0:
        print("❌ Analysis Agent: Data extraction failed.")
        return {
            "analysis_results": "Data Visualization Unavailable: The agent could not parse the database rows.",
            "next_step": "critic"
        }

    # 2. DATA PROCESSING & REGRESSION
    try:
        df = pd.DataFrame(db_data)
        # Clean columns to prevent "duplicate key" issues during naming
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        if 'month_str' in df.columns:
            df = df.rename(columns={'month_str': 'month'})
        
        df['month'] = pd.to_datetime(df['month'])
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Aggregation: Ensures unique dates before regression
        df = df.groupby('month', as_index=False)['amount'].sum()
        df = df.sort_values('month').reset_index(drop=True)

        # --- LINEAR REGRESSION LOGIC ---
        if len(df) > 1:
            df['month_ordinal'] = df['month'].map(datetime.toordinal)
            X = df[['month_ordinal']].values
            y = df['amount'].values
            
            model = LinearRegression().fit(X, y)
            df['prediction'] = model.predict(X)
            
            # Forecast next 3 months
            last_date = df['month'].max()
            future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, 4)]
            future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
            future_preds = model.predict(future_ordinals)
            
            forecast_df = pd.DataFrame({
                'month': future_dates,
                'amount': [np.nan] * 3,
                'prediction': future_preds
            })
            
            # FIX: Robust Concatenation
            # We reset indices and drop duplicates to prevent "cannot assemble" error
            full_display_df = pd.concat([df, forecast_df], ignore_index=True, sort=False)
            full_display_df = full_display_df.loc[:, ~full_display_df.columns.duplicated()].copy()
        else:
            full_display_df = df.copy()

        # 3. PLOTTING
        plt.figure(figsize=(10, 6))
        plt.plot(df['month'], df['amount'], marker='o', label='Actual Revenue', linewidth=2, color='#1f77b4')
        
        if 'prediction' in full_display_df.columns:
            plt.plot(full_display_df['month'], full_display_df['prediction'], 
                     linestyle='--', color='#ff7f0e', label='Revenue Trend/Forecast')
        
        # Benchmark line logic
        first_val = df['amount'].iloc[0] if not df['amount'].empty else 0
        benchmark_val = first_val * 1.15 
        plt.axhline(y=benchmark_val, color='#d62728', linestyle='--', label='2026 SaaS Benchmark (15% Growth)')
        
        plt.title("Revenue Trend & 3-Month Forecast vs Industry Benchmark")
        plt.xlabel("Month")
        plt.ylabel("Revenue ($)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save Artifact
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_file_dir, "../../.."))
        artifacts_dir = os.path.join(project_root, "artifacts")
        os.makedirs(artifacts_dir, exist_ok=True)
        chart_path = os.path.join(artifacts_dir, "revenue_trend.png")
        
        plt.savefig(chart_path)
        plt.close()
        
    except Exception as e:
        print(f"❌ Plotting/Regression Error: {e}")
        # Return partial success so the swarm doesn't loop; let the Critic explain the failure
        return {
            "analysis_results": f"Analysis Error: {str(e)}. However, raw data was captured.",
            "next_step": "critic"
        }

    # 4. LLM STRATEGIC SYNTHESIS
    llm = ChatOllama(model="llama3", temperature=0.2)
    system_prompt = "You are a Strategic SaaS CFO. Analyze internal data vs benchmarks. Provide 3 recommendations."
    
    # Escape braces for LangChain prompt safety
    safe_web = str(web_results).replace("{", "{{").replace("}", "}}")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Internal Data: {db}\n\nWeb Research: {web}\n\nQuestion: {query}")
    ])
    
    analysis_report = (prompt | llm).invoke({
        "db": df.to_dict(orient='records'),
        "web": safe_web,
        "query": state["question"]
    }).content

    return {
        "analysis_results": analysis_report,
        "last_df_data": full_display_df.to_dict(orient='records'),
        "next_step": "critic"
    }
