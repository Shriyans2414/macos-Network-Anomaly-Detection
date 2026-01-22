from fastapi import FastAPI
from storage.state import read_state


app = FastAPI(title="Network Anomaly Detection API")

@app.get("/status")
def get_status():
    return read_state()

@app.get("/")
def root():
    return {"status": "Network Anomaly Detection API running"}
