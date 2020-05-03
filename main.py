# main.py
##############################################################################################################################
##############################################################################################################################
#####################       ASSIGNMENT 1       ###############################################################################
##############################################################################################################################
##############################################################################################################################

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

class PatientRq(BaseModel):
	name: str
	surname: str

class PatientResp(BaseModel):
	id: int
	patient: dict

app = FastAPI()
app.ID = 0
app.patients = {}

### TASK 1 ###################################################################################################################

@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}

### TASK 2 ###################################################################################################################

@app.get("/method")
@app.put("/method")
@app.post("/method")
@app.delete("/method")
def get_method(rq: Request):
    return {"method": str(rq.method)}

### TASK 3 ###################################################################################################################

#@app.post("/patient", response_model=PatientResp)
def receive_patient(rq: PatientRq):
	if app.ID not in app.patients.keys():
		app.patients[app.ID] = rq.dict()
		app.ID += 1
	return PatientResp(id=app.ID, patient=rq.dict())

### TASK 4 ###################################################################################################################
	
#@app.get("/patient/{pk}")
async def return_patient(pk: int):
    if pk in app.patients.keys():
    	return app.patients[pk]
    else:
    	raise HTTPException(status_code=204, detail="Item not found")

##############################################################################################################################
##############################################################################################################################
#####################       ASSIGNMENT 3       ###############################################################################
##############################################################################################################################
##############################################################################################################################

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, Response, Cookie, status
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from hashlib import sha256
import secrets

app.secret_key = "very constant and random secret, best 64 characters, here it is."
app.session_tokens = []
templates = Jinja2Templates(directory="templates")

### TASK 1 & 4 #######################################################

@app.get("/welcome")
def do_welcome(request: Request, session_token: str = Cookie(None)):
	if session_token not in app.session_tokens:
		raise HTTPException(status_code=401, detail="Unathorised")
	return templates.TemplateResponse("item.html", {"request": request, "user": "trudnY"})

### TASK 2 ####################################################################################################################

@app.post("/login")
def get_current_user(response: Response, credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    correct_username = secrets.compare_digest(credentials.username, "trudnY")
    correct_password = secrets.compare_digest(credentials.password, "PaC13Nt")
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    session_token = sha256(bytes(f"{credentials.username}{credentials.password}{app.secret_key}", encoding='utf8')).hexdigest()
    app.session_tokens.append(session_token)
    response.set_cookie(key="session_token", value=session_token)
    response.headers["Location"] = "/welcome"
    response.status_code = status.HTTP_302_FOUND 

### TASK 3 ###################################################################################################################

@app.post("/logout")
def logout(*, response: Response, session_token: str = Cookie(None)):
	if session_token not in app.session_tokens:
		raise HTTPException(status_code=401, detail="Unathorised")
	app.session_tokens.remove(session_token)
	return RedirectResponse("/")

### TASK 5 ###################################################################################################################

@app.post("/patient")
def add_patient(response: Response, patient: PatientRq, session_token: str = Cookie(None)):
	if session_token not in app.session_tokens:
		raise HTTPException(status_code=401, detail="Unathorised")
	if app.ID not in app.patients.keys():
		app.patients[app.ID] = patient.dict()
		app.ID += 1
	response.set_cookie(key="session_token", value=session_token)
	response.headers["Location"] = f"/patient/{app.ID-1}"
	response.status_code = status.HTTP_302_FOUND

@app.get("/patient")
def display_patients(response: Response, session_token: str = Cookie(None)):
	if session_token not in app.session_tokens:
		raise HTTPException(status_code=401, detail="Unathorised")
	return app.patients
    

@app.get("/patient/{id}")
def display_patient(response: Response, id: int, session_token: str = Cookie(None)):
	if session_token not in app.session_tokens: 
		raise HTTPException(status_code=401, detail="Unathorised")
	response.set_cookie(key="session_token", value=session_token)
	if id in app.patients.keys():
		return app.patients[id]
	

@app.delete("/patient/{id}")
def delete_patient(response: Response, id: int, session_token: str = Cookie(None)):
	if session_token not in app.session_tokens: 
		raise HTTPException(status_code=401, detail="Unathorised")
	app.patients.pop(id, None)		
	response.status_code = status.HTTP_204_NO_CONTENT


##############################################################################################################################
##############################################################################################################################
#####################       ASSIGNMENT 4       ###############################################################################
##############################################################################################################################
##############################################################################################################################

import sqlite3

class AlbumRq(BaseModel):
	title: str
	artist_id: int


class AlbumResp(BaseModel):
	AlbumId: int
	Title: str
	ArtistId: int

### TASK 1 ###################################################################################################################

@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect('chinook.db')

@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close() 


@app.get("/tracks")
async def display_tracks(page: int = 0, per_page: int = 10):
	app.db_connection.row_factory = sqlite3.Row
	tracks = app.db_connection.execute(
		f"SELECT * FROM tracks LIMIT {per_page} OFFSET {page*per_page}"
		).fetchall()
	return tracks

### TASK 2 ###################################################################################################################

@app.get("/tracks/composers")
async def display_titles(composer_name: str):
	app.db_connection.row_factory = lambda cursor, row : row[0]
	tracks = app.db_connection.execute(
		"SELECT name FROM tracks WHERE composer = ? ORDER BY name",
		(composer_name,)).fetchall()
	if len(tracks) <= 0:
		raise HTTPException(status_code=404, detail={"error": "Item not found"})
	return tracks

### TASK 3 ###################################################################################################################

@app.post("/albums", response_model=AlbumResp)
async def insert_album(response: Response, rq: AlbumRq):
	artist = app.db_connection.execute("SELECT * FROM artists WHERE artistId = ?",
									 	(rq.artist_id,)).fetchall()
	if len(artist) <= 0:
		raise HTTPException(status_code=404, detail={"error": "Item not found"})
	cursor = app.db_connection.execute("INSERT INTO albums(title, artistId) VALUES (?,?)",
										(rq.title,rq.artist_id))
	app.db_connection.commit()
	response.status_code = 201
	return AlbumResp(AlbumId=cursor.lastrowid, Title=rq.title, ArtistId=rq.artist_id)


@app.get("/albums/{album_id}", response_model=AlbumResp)
async def display_album(album_id: int):
	app.db_connection.row_factory = sqlite3.Row
	album = app.db_connection.execute("SELECT * FROM albums WHERE albumId = ?",
									    (album_id,)).fetchall()
	if len(album) <= 0:
		raise HTTPException(status_code=404, detail={"error": "Item not found"})
	return AlbumResp(AlbumId=album_id, Title=album[0]["title"], ArtistId=album[0]["artistId"])

### TASK 4 ###################################################################################################################

@app.put("/customers/{customer_id}")
async def update_customer(customer_id: int, rq: dict = {}):
	app.db_connection.row_factory = sqlite3.Row
	customer = app.db_connection.execute("SELECT * FROM customers WHERE customerId = ?", 
											(customer_id,)).fetchall()
	if len(customer) <= 0:
		raise HTTPException(status_code=404, detail={"error": "Item not found"})
	query = "UPDATE customers SET "
	for key in rq: 
		query += f"{key} = \'{rq[key]}\', "
	query = query[:-2]
	query += " WHERE customerId = " + str(customer_id)
	app.db_connection.execute(query)
	app.db_connection.commit()
	return app.db_connection.execute("SELECT * FROM customers WHERE customerId = ?", 
											(customer_id,)).fetchone()

### TASK 5 & 6 ###################################################################################################################

@app.get("/sales")
async def display_stats(category: str):
	app.db_connection.row_factory = sqlite3.Row	
	stats = None	
	if category == "customers":
		stats = app.db_connection.execute('''
			SELECT c.customerId, email, phone, ROUND(SUM(total),2) AS Sum
			FROM customers c 
				JOIN invoices i ON c.customerId = i.customerId
			GROUP BY c.customerId
			ORDER BY Sum DESC, c.customerId;
			''').fetchall()
	elif category == "genres":
		stats = app.db_connection.execute('''
			SELECT g.name, SUM(quantity) AS Sum
			FROM genres g 
				JOIN tracks t ON t.genreId = g.genreId
				JOIN invoice_items ii ON ii.trackId = t.trackId
			GROUP BY g.name
			ORDER BY Sum DESC, g.name
			''').fetchall()
	else:
		raise HTTPException(status_code=404, detail={"error": "Item not found"})
	return stats

##################################################################################################################################