from fastapi import FastAPI, Request, HTTPException, Cookie, Depends, status, Response
from starlette.responses import RedirectResponse
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from hashlib import sha256

app = FastAPI()

app.patient_id: int = 0
app.patient_db: dict = {} 

app.secret_key = "gOoMDQ9oFM9LqC3noS9lgfHibuYNR2BaUOKbEfftpjAtSi8s2ejnKNYBjeQSo7qq"
app.users={"tRudnY": "PaC13Nt"}
app.sessions={}
security = HTTPBasic()
app.session_tokens = []

@app.get("/")
def root():
	return {"message": "Hello World during the coronavirus pandemic!"}

@app.get("/welcome")
def root2():
	return {"message": "Co u Ciebie słychać? Co nowego?"}


@app.get("/login")
def get_current_user(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "trudnY")
    correct_password = secrets.compare_digest(credentials.password, "PaC13Nt")
    if not (correct_username and correct_password):
        raise HTTPException(
        	status_code=401, detail="Incorrect email or password")
    session_token = sha256(bytes(f"{credentials.username}{credentials.password}{app.secret_key}", encoding='utf8')).hexdigest()
    app.session_tokens.append(session_token)
    response.set_cookie(key="session_token", value=session_token)
    response.headers["Location"] = "/welcome"
    response.status_code = status.HTTP_302_FOUND 

@app.post("/logout")
def logout(*, response: Response, session_token: str = Cookie(None)):
	if session_token not in app.session_tokens:
		raise HTTPException(status_code=401, detail="Unathorised")
	app.session_tokens.remove(session_token)
	response = RedirectResponse(url = "/")
	return response

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
	if session_token not in app.session_tokens:
		raise HTTPException(status_code=401, detail="Unathorised")
	id_patient = app.patient_id
	counter()
	app.patient_db[id_patient] = {"patient" : {"name": patient.name.upper(), "surname": patient.surename.upper()}}
	return {"id": id_patient, "patient": {"name": patient.name.upper(), "surname": patient.surename.upper()}}

@app.get('/patient/{pk}')
def read_patient(pk: int):
	if session_token not in app.session_tokens:
		raise HTTPException(status_code=401, detail="Unathorised")
	if not pk in app.patient_db.keys():
		raise HTTPException(
			status_code=204)
	return app.patient_db[pk]["patient"]
