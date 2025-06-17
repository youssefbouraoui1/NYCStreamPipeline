from datetime import timedelta,datetime
import requests
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator

default_args = {
    'owner': 'nycstream',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    dag_id= "fetching_incidents_data",
    start_date= datetime(2025,5,1),
    default_args=default_args,
    schedule='*/10 * * * *', 
    catchup=False
)

NYC_API = "https://data.cityofnewyork.us/resource/h9gi-nx95.json?$limit=100"
EXPRESS_API = "http://express:3000/api/v1/incidents" 

def fetch_and_send():
    response = requests.get(NYC_API)
    if response.status_code != 200:
        raise Exception("Failed to fetch data")
    
    data = response.json()
    print(f"✅ Fetched {len(data)} records")

    def fetch_and_send():
        response = requests.get(NYC_API)
        if response.status_code != 200:
            raise Exception("Failed to fetch data")
    
        data = response.json()
        print(f"✅ Fetched {len(data)} records")

        batch = []

        for incident in data:
            mapped = {
            "timestamp": f"{incident.get('crash_date', '')}T{incident.get('crash_time', '00:00')}:00Z",
            "crash_date": incident.get('crash_date',''),
            "crash_time": incident.get('crash_time', '00:00'),
            "borough": incident.get("borough", "UNKNOWN"),
            "latitude": float(incident["latitude"]) if "latitude" in incident else None,
            "longitude": float(incident["longitude"]) if "longitude" in incident else None,
            "street_name": incident.get("on_street_name", "UNKNOWN"),
            "injured_persons": int(incident.get("number_of_persons_injured", 0)),
            "killed_persons": int(incident.get("number_of_persons_killed", 0)),
            "vehicle_type": incident.get("vehicle_type_code1", "UNKNOWN")
            }
            batch.append(mapped)

    
        res = requests.post(EXPRESS_API, json={"data": batch})
        if res.status_code != 200:
            raise Exception(f"Failed to send batch: {res.status_code} - {res.text}")
        print("Sent full batch to Express API")


    
fetch_incident_data_task = PythonOperator(
    task_id = "fetch_and_send_data",
    python_callable=fetch_and_send,
    dag = dag,
)

