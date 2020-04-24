from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

app = FastAPI()

app.patient_id: int = 0
app.patient_db: dict = {} 

@app.get("/")
def root():
	return {"message": "Hello World during the coronavirus pandemic!"}

@app.get("/welcome")
def root2():
	return {"message": "Co u Ciebie słychać? Co nowego?"}
    
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
	id_patient = app.patient_id
	counter()
	app.patient_db[id_patient] = {"patient" : {"name": patient.name.upper(), "surname": patient.surename.upper()}}
	return {"id": id_patient, "patient": {"name": patient.name.upper(), "surname": patient.surename.upper()}}

@app.get('/patient/{pk}')
def read_patient(pk: int):
	if not pk in app.patient_db.keys():
		raise HTTPException(
			status_code=204)
	return app.patient_db[pk]["patient"]
