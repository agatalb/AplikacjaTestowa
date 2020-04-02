from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

app.patient_id: int = 0
# app.patient_db: dict 

@app.get("/")
def root():
	return {"message": "Hello World during the coronavirus pandemic!"}
    
@app.api_route("/method", methods = ["GET", "POST", "DELETE", "PUT"])  


def fun(request: Request):
	return {"method":request.method}


class Patient(BaseModel):
	name: str
	surename: str

def counter():
	app.patient_id += 1

@app.post("/patient")
def create_patient(patient: Patient):
	counter()
	return {"id": app.patient_id, "patient": {"name": patient.name.upper(), "surname": patient.surename.upper()}}
