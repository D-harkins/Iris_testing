from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
import pandas as pd
import json
import uvicorn
import numpy as np
import plotly.express as px
import plotly.io as pio
import os

# ✅ FastAPI Instance
app = FastAPI()

# ✅ Databricks API Details
DATABRICKS_INSTANCE = "https://ithaka-production.cloud.databricks.com"
TOKEN = os.getenv("DATABRICKS_ACCESS_TOKEN")
WAREHOUSE_ID = os.getenv("WAREHOUSE_ID")
API_URL = f"{DATABRICKS_INSTANCE}/api/2.0/sql/statements"

SQL_QUERY = """SELECT * FROM s_r.demo.iris_flowers"""

def query_databricks(sql_query: str):
    payload = {
        "statement": sql_query,
        "warehouse_id": WAREHOUSE_ID,
        "format": "JSON"
    }
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        return {"error": "Failed to fetch data from Databricks", "details": response.text}

    data = response.json()
    print(data)

    # ✅ Extract Data
    if "result" in data and "data_array" in data["result"] and "manifest" in data:
        columns = [col["name"] for col in data["manifest"]["schema"]["columns"]]
        rows = data["result"]["data_array"]
        df = pd.DataFrame(rows, columns=columns)
        return df.to_dict(orient="records")  # Return as JSON
    return {"error": "No data returned"}

@app.get("/fetch-data")
def fetch_data():
    """Fetch and return data from Databricks as JSON."""
    return query_databricks(SQL_QUERY)
@app.get("/plot-data")
def generate_plot():
    """Fetches data from FastAPI and returns a Plotly figure as JSON."""
    
    # Step 1: Fetch JSON data from FastAPI's existing endpoint
    API_URL = "http://127.0.0.1:8000/fetch-data"  # Ensure this points to your data endpoint
    response = requests.get(API_URL)
    
    if response.status_code != 200:
        return {"error": "Failed to retrieve data", "details": response.text}

    data = response.json()
    
    # Step 2: Convert JSON back to Pandas DataFrame
    df_iris = pd.DataFrame(data)

    # Step 5: Recreate the Plotly Stacked Bar Chart
    fig = px.scatter(
        df_iris,
        x="sepal_length",
        y="petal_length",
        color="species",
        title="Species, Sepal Length, Petal Length",
    )

    # Step 11: Convert Plotly figure to JSON and return it
    fig_json_str = fig.to_json()

    return JSONResponse(content=fig_json_str)
# ✅ Run FastAPI with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
