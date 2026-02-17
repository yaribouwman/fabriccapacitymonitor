# Fabric Capacity Metrics Extraction Notebook
# This notebook queries the Capacity Metrics semantic model and pushes data to your monitoring API

import sempy.fabric as fabric
import requests
from datetime import datetime, timedelta
import json

# Configuration - Set these as notebook parameters or environment variables
API_URL = "https://your-monitoring-api.azurecontainerapps.io"
INGEST_KEY = "your-ingest-key-here"
CAPACITY_NAME = "your-capacity-name"

# Time window for metrics (last 15 minutes)
end_time = datetime.utcnow()
start_time = end_time - timedelta(minutes=15)

# Query the Capacity Metrics semantic model
# This requires Capacity Admin role in your Fabric tenant
dax_query = f"""
EVALUATE
SUMMARIZECOLUMNS(
    'CU'.TimePoint,
    "CU_Utilization_Pct", AVERAGE('CU'[CU Utilization %]),
    "Overloaded_Minutes", SUM('CU'[Overloaded Minutes]),
    "Throttled_Operations", SUM('Operations'[Throttled Count])
)
ORDER BY 'CU'[TimePoint] DESC
"""

try:
    df = fabric.evaluate_dax(
        dataset="Capacity Metrics",
        dax_string=dax_query
    )
    
    if df.empty:
        print("No metrics data retrieved")
    else:
        latest_row = df.iloc[0]
        
        payload = {
            "capacity_name": CAPACITY_NAME,
            "collected_at": datetime.utcnow().isoformat() + "Z",
            "metrics": [
                {
                    "name": "CU_Utilization_Pct",
                    "value": float(latest_row["CU_Utilization_Pct"]),
                    "aggregation": "Average"
                },
                {
                    "name": "Overloaded_Minutes",
                    "value": float(latest_row["Overloaded_Minutes"]),
                    "aggregation": "Total"
                },
                {
                    "name": "Throttled_Operations",
                    "value": float(latest_row["Throttled_Operations"]),
                    "aggregation": "Total"
                }
            ]
        }
        
        headers = {
            "X-Ingest-Key": INGEST_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_URL}/api/ingest",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 202:
            print(f"Successfully pushed {len(payload['metrics'])} metrics")
            print(f"CU Utilization: {payload['metrics'][0]['value']:.2f}%")
        else:
            print(f"Failed to push metrics: {response.status_code}")
            print(response.text)

except Exception as e:
    print(f"Error: {str(e)}")
