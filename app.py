# app.py

import pandas as pd
import numpy as np
import time
import os
from sqlalchemy import create_engine, text
import psycopg2

def get_engine(url):
    """Try connecting to the PostgreSQL engine until successful."""
    while True:
        try:
            print("🔄 Attempting to connect to PostgreSQL...")
            engine = create_engine(url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Successfully connected to PostgreSQL.")
            return engine
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            time.sleep(3)

if __name__ == "__main__":
    csv_file = 'data/titanic.csv'

    # 🧩 Load DB config from environment (with fallbacks)
    # host: must match your postgres service name in YAML
    # 'postgres' is the service name in the Kubernetes cluster
    db_config = {
        'user': os.getenv('POSTGRES_USER', 'user'),
        'password': os.getenv('POSTGRES_PASSWORD', 'password'),
        'host': os.getenv('POSTGRES_HOST', 'postgres'), 
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'dbname': os.getenv('POSTGRES_DB', 'mydb')
    }

    # 🧠 Build connection URL
    # postgresql+psycopg2://user:password@postgres:5432/mydb
    url = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"

    print("📄 Reading CSV file...")
    df = pd.read_csv(csv_file, index_col=False)
    print(f"✅ CSV loaded. Shape: {df.shape}")
    print(df.head())  

    engine = get_engine(url)

    print("⬆️ Uploading DataFrame to PostgreSQL table 'titanic'...")
    df.to_sql('titanic', engine, if_exists='replace', index=False)
    print("✅ Upload complete.")

    # verify by reading a few rows back
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM titanic"))
        count = result.scalar()
        print(f"📊 Row count in 'titanic' table: {count}")
        sample = conn.execute(text("SELECT * FROM titanic LIMIT 5")).fetchall()
        print("🧾 Sample rows:")
        for row in sample:
            print(row)

    print("🏁 ETL job completed successfully.")
    # Optional: Save the DataFrame to a local file for verification
    os.makedirs('output', exist_ok=True)
    df.to_csv('output/titanic_output.csv', index=False)
    print("💾 DataFrame saved to 'output/titanic_output.csv'.")
    
    # Keep the script running to allow inspection if needed
    # while True:
    #     time.sleep(60)  # sleep to keep the container alive