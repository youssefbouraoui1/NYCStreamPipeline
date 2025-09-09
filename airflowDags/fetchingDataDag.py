from datetime import timedelta,datetime
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator

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
    print(f"Fetched {len(data)} records")

    batch = []

    for incident in data:
        mapped = {
            "timestamp": f"{incident.get('crash_date', '')}T{incident.get('crash_time', '00:00')}:00Z",
            "crash_date": incident.get('crash_date',''),
            "crash_time": incident.get('crash_time', '00:00'),
            "borough": incident.get("borough", "UNKNOWN"),
            "latitude": float(incident["latitude"]) if "latitude" in incident else None,
            "longitude": float(incident["longitude"]) if "longitude" in incident else None,
            "on_street_name": incident.get("on_street_name", "UNKNOWN"),
            "off_street_name": incident.get("off_street_name","UNKNOWN"),
            "cross_street_name": incident.get("cross_street_name"),
            "number_of_persons_injured": int(incident.get("number_of_persons_injured", 0)),
            "number_of_persons_killed": int(incident.get("number_of_persons_killed", 0)),
            "number_of_pedestrians_injured": int(incident.get("number_of_pedestrians_injured",0)),
            "number_of_pedestrians_killed": int(incident.get("number_of_pedestrians_killed",0)),
            "number_of_cyclist_injured": int(incident.get("number_of_cyclist_injured",0)),
            "number_of_cyclist_killed": int(incident.get("number_of_cyclist_killed",0)),
            "number_of_motorist_injured": int(incident.get("number_of_motorist_injured",0)),
            "number_of_motorist_killed": int(incident.get("number_of_motorist_killed",0)),
            "contributing_factor_vehicle_1": incident.get("contributing_factor_vehicle_1","UNKNOWN"),
            "contributing_factor_vehicle_2": incident.get("contributing_factor_vehicle_2","UNKNOWN"),
            "contributing_factor_vehicle_3": incident.get("contributing_factor_vehicle_3","UNKNOWN"),
            "contributing_factor_vehicle_4": incident.get("contributing_factor_vehicle_4","UNKNOWN"),
            "contributing_factor_vehicle_5": incident.get("contributing_factor_vehicle_5","UNKNOWN"),
            "vehicle_type_code1": incident.get("vehicle_type_code1","UNKNOWN"),
            "vehicle_type_code2": incident.get("vehicle_type_code2","UNKNOWN"),
            "vehicle_type_code_3": incident.get("vehicle_type_code_3","UNKNOWN"),
            "vehicle_type_code_4": incident.get("vehicle_type_code_4","UNKNOWN"),
            "vehicle_type_code_5": incident.get("vehicle_type_code_5","UNKNOWN"),
            "vehicle_type": incident.get("vehicle_type_code1", "UNKNOWN"),
            "collision_id": int(incident.get("collision_id",0))
        }
        batch.append(mapped)

    res = requests.post(EXPRESS_API, json={"data": batch})
    if res.status_code != 200:
        raise Exception(f" Failed to send batch: {res.status_code} - {res.text}")
    print("Sent full batch to Express API")



    
fetch_incident_data_task = PythonOperator(
    task_id = "fetch_and_send_data",
    python_callable=fetch_and_send,
    dag = dag,
)
