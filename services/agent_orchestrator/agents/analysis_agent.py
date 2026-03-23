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

async def analysis_agent(state: AnalystState):
    """
    Synthesizes SQL data and Web Research to generate a predictive 
    revenue chart and a strategic CFO-level report.
    """
    print("Analysis Agent: Synthesizing data and generating comparative chart...")
    
    data_context = state.get("data_context", [])
    print(f"DEBUG: Analysis Agent received context with {len(data_context)} items.")
    
    db_data = None
    web_results = ""
    
    try:
        for entry in data_context:
            if isinstance(entry, str):
                if "WEB RESEARCH FINDINGS" in entry or "Rule of 40" in entry:
                    web_results += "\n" + entry
                    continue
                if entry.strip().startswith(('{', '[')):
                    try:
                        parsed = json.loads(entry)
                        if isinstance(parsed, dict) and "rows" in parsed:
                            db_data = parsed["rows"]
                        elif isinstance(parsed, list):
                            db_data = parsed
                    except:
                        continue
            
            elif isinstance(entry, dict):
                if "rows" in entry:
                    db_data = entry["rows"]
                elif "formatted_result" in entry:
                    try:
                        db_data = json.loads(entry["formatted_result"])
                    except:
                        continue
                # FIX: Check for both 'amount' and 'total_amount' in single row dicts
                elif "amount" in entry or "total_amount" in entry: 
                    db_data = [entry]

        if not db_data:
            db_data = state.get("sql_results")

        if not db_data or len(db_data) == 0:
            raise ValueError("No numeric SQL data found in state. Check SQL Specialist output.")

        # 2. DATA PROCESSING & REGRESSION (ENHANCED RESILIENCE)
        df = pd.DataFrame(db_data)
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # --- COLUMN ALIAS FIX ---
        if 'month_str' in df.columns:
            df = df.rename(columns={'month_str': 'month'})
            
        # Standardize 'total_amount' (from SUM queries) to 'amount'
        if 'total_amount' in df.columns and 'amount' not in df.columns:
            df = df.rename(columns={'total_amount': 'amount'})
        
        if 'amount' not in df.columns:
            available = ", ".join(df.columns)
            raise KeyError(f"Required column 'amount' or 'total_amount' not found. Available: {available}")
        # ------------------------

        df['month'] = pd.to_datetime(df['month'])
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        df = df.groupby('month', as_index=False)['amount'].sum()
        df = df.sort_values('month').reset_index(drop=True)

        # --- LINEAR REGRESSION LOGIC ---
        full_display_df = df.copy()
        if len(df) > 1:
            df['month_ordinal'] = df['month'].map(datetime.toordinal)
            X = df[['month_ordinal']].values
            y = df['amount'].values
            
            model = LinearRegression().fit(X, y)
            df['prediction'] = model.predict(X)
            
            last_date = df['month'].max()
            future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, 4)]
            future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
            future_preds = model.predict(future_ordinals)
            
            forecast_df = pd.DataFrame({
                'month': future_dates,
                'amount': [np.nan] * 3,
                'prediction': future_preds
            })
            
            full_display_df = pd.concat([df, forecast_df], ignore_index=True, sort=False)

        # 3. PLOTTING
        plt.figure(figsize=(10, 6))
        plt.plot(df['month'], df['amount'], marker='o', label='Actual Revenue', linewidth=2, color='#1f77b4')
        
        if 'prediction' in full_display_df.columns:
            plt.plot(full_display_df['month'], full_display_df['prediction'], 
                     linestyle='--', color='#ff7f0e', label='Revenue Trend/Forecast')
        
        first_val = df['amount'].iloc[0] if not df['amount'].empty else 0
        plt.axhline(y=first_val * 1.15, color='#d62728', linestyle='--', label='2026 SaaS Benchmark (+15%)')
        
        plt.title("Revenue Intelligence: Actuals vs. Predictive Forecast")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        artifacts_dir = os.path.join(os.getcwd(), "artifacts")
        os.makedirs(artifacts_dir, exist_ok=True)
        chart_path = os.path.join(artifacts_dir, "revenue_trend.png")
        plt.savefig(chart_path)
        plt.close()

        # 4. LLM STRATEGIC SYNTHESIS
        llm = ChatOllama(model="llama3", temperature=0.1)
        safe_web = str(web_results).replace("{", "{{").replace("}", "}}")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Strategic SaaS CFO. Analyze internal data vs benchmarks."),
            ("human", "Data: {db}\nResearch: {web}\nQuestion: {query}")
        ])
        
        # Capture report results safely
        try:
            report_response = (prompt | llm).invoke({
                "db": df.to_dict(orient='records'),
                "web": safe_web,
                "query": state.get("question", "")
            })
            report = report_response.content
        except Exception as llm_err:
            report = f"Data was analyzed and chart generated, but the narrative report failed: {llm_err}"

        return {
            "analysis_results": report,
            "chart_artifact": chart_path,
            "last_df_data": full_display_df.to_dict(orient='records'), # Send back to Streamlit
            "next_step": "critic"
        }

    except Exception as e:
        print(f"AICA: Analysis Agent Error: {e}")
        return {
            "analysis_results": f"Analysis interrupted: {str(e)}",
            "next_step": "critic"
        }
