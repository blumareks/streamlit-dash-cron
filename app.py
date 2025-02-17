import streamlit as st
import requests
import time
import threading
import datetime

from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Retrieve the database configuration from the environment

SDWAN_URL = os.getenv("SDWAN_URL")
RNA_URL =  os.getenv("RNA_URL")
ALERT_URL = os.getenv("ALERT_URL")

# Default polling intervals (in minutes)
default_intervals = {
    "policy_metrics": 1440,  # Daily
    "rna_service_data": 30,  # Every 30 minutes
    "rna_alerts": 5  # Every 5 minutes
}

# URLs to call
service_urls = {
    "policy_metrics": SDWAN_URL,
    "rna_service_data": RNA_URL,
    "rna_alerts": ALERT_URL
}

# Shared state for intervals
polling_intervals = default_intervals.copy()
log_messages = []

# Function to log messages
def log_message(service, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_messages.append(f"[{timestamp}] {service}: {message}")
    if len(log_messages) > 50:
        log_messages.pop(0)  # Keep log size manageable

# Function to call API
def call_service(service_name):
    url = service_urls[service_name]
    try:
        response = requests.get(url, timeout=60, verify=False)  # Skipping SSL verification for now
        log_message(service_name, f"Response {response.status_code}: {response.text[:100]}")  # Log first 100 chars
    except Exception as e:
        log_message(service_name, f"Error: {str(e)}")

# Function to run services in background
def service_runner(service_name):
    while True:
        call_service(service_name)
        time_now = datetime.datetime.now().strftime('%H:%M:%S') + "called service " + service_name
        print(time_now)
        time.sleep(polling_intervals[service_name] * 60)

# Start background threads
def start_threads():
    for service in polling_intervals.keys():
        thread = threading.Thread(target=service_runner, args=(service,), daemon=True)
        thread.start()

# Start service threads
start_threads()

# Streamlit UI
st.title("Service Polling Monitor")
st.write("This app calls various services at defined intervals and logs their responses.")

# User input to change intervals
st.sidebar.header("Update Polling Intervals (in minutes)")
new_intervals = {}
for service, interval in polling_intervals.items():
    new_intervals[service] = st.sidebar.number_input(f"{service.replace('_', ' ').title()}", min_value=1, value=interval)

if st.sidebar.button("Update Intervals"):
    polling_intervals.update(new_intervals)
    log_message("System", "Polling intervals updated")
    st.sidebar.success(f"Updated at {datetime.datetime.now().strftime('%H:%M:%S')}")

# Display logs
st.header("Service Logs")
st.text_area("Logs", "\n".join(log_messages), height=300)
