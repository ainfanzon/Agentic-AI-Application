import os
import random
import psycopg2
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

# 1. LOAD ENVIRONMENT VARIABLES FROM .ENV
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def seed_revenue_data():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in .env file.")
        return

    try:
        # CockroachDB uses the Postgres protocol, so psycopg2 works perfectly
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        print(f"Connected to CockroachDB: {DATABASE_URL.split('@')[-1].split('/')[0]}")

        # 2. PROMPT FOR USER INPUT
        print("\n🚀 Swarm Data Seeder: Monthly Revenue")
        start_date_input = input("Enter starting date (YYYY-MM-DD): ")
        
        try:
            start_date = datetime.strptime(start_date_input, "%Y-%m-%d").date()
            # Normalize to the first of the month for clean time-series analysis
            start_date = start_date.replace(day=1)
            end_date = datetime.now().date()
        except ValueError:
            print("❌ Invalid format. Use YYYY-MM-DD.")
            return

        # 3. DATA GENERATION
        categories = ['SaaS', 'Hardware', 'Software', 'Services','AI-Enhanced']
        current_month = start_date
        records = []

        print(f"📊 Generating monthly data until {end_date}...")

        while current_month <= end_date:
            for category in categories:
                # Generate base revenue with some variance
                base = random.uniform(25000, 45000)
                
                # Simulate a "Conference Demo" growth trend:
                # SaaS grows 4% monthly, Hardware stays flat, Services fluctuates
                months_passed = (current_month.year - start_date.year) * 12 + (current_month.month - start_date.month)
                
                if category == 'SaaS':
                    base = base * (1.04 ** months_passed) # 4% Compound Growth
                elif category == 'Services':
                    base = base * random.uniform(0.8, 1.2) # High volatility
                
                amount = round(base, 2)
                
                # Schema: month, amount, product_category (id is auto-gen)
                records.append((current_month, amount, category))
            
            # Increment month
            current_month += relativedelta(months=1)

        # 4. BATCH EXECUTION
        insert_query = """
            INSERT INTO public.revenue (month, amount, product_category)
            VALUES (%s, %s, %s)
        """
        
        cur.executemany(insert_query, records)
        conn.commit()

        print(f"✨ Successfully seeded {len(records)} rows into public.revenue.")
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    seed_revenue_data()
