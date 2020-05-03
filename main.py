from fastapi import FastAPI, Request, HTTPException, Cookie, Depends, status, Response
from starlette.responses import RedirectResponse
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from hashlib import sha256
import aiosqlite



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
	if session_token not in app.session_tokens:
		response.status_code = status.HTTP_401_UNAUTHORIZED
		return MESSAGE_UNAUTHORIZED
	response.status_code = status.HTTP_302_FOUND
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
def logout(response: Response, session_token: str = Cookie(None)):
	if session_token not in app.session_tokens:
		response.status_code = status.HTTP_401_UNAUTHORIZED
		return MESSAGE_UNAUTHORIZED
	response.headers["Location"] = "/"
    response.status_code = status.HTTP_302_FOUND
	app.session_tokens.remove(session_token)
	

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
	response.status_code = status.HTTP_302_FOUND
	response.set_cookie(key="session_token", value=session_token)
	id_patient = app.patient_id
	counter()
	app.patient_db[id_patient] = {"patient" : {"name": patient.name.upper(), "surname": patient.surename.upper()}}
	return {"id": id_patient, "patient": {"name": patient.name.upper(), "surname": patient.surename.upper()}}
	response.status_code = status.HTTP_302_FOUND

@app.get('/patient/{pk}')
def read_patient(pk: int):
	if session_token not in app.session_tokens:
		raise HTTPException(status_code=401, detail="Unathorised")
	response.status_code = status.HTTP_302_FOUND
	if not pk in app.patient_db.keys():
		raise HTTPException(
			status_code=204)
	response.status_code = status.HTTP_302_FOUND
	return app.patient_db[pk]["patient"]
	response.status_code = status.HTTP_302_FOUND


#wyk4


@app.on_event("startup")
async def startup():
	router.db_connection = await aiosqlite.connect('chinook.db')

@app.on_event("shutdown")
async def shutdown():
	await router.db_connection.close()

@app.get("/tracks")
async def tracks(page: int = 0, per_page: int = 10):
	router.db_connection.row_factory = aiosqlite.Row
	cursor = await router.db_connection.execute("SELECT * FROM tracks ORDER BY TrackId LIMIT :per_page OFFSET :per_page*:page",
		{'page': page, 'per_page': per_page})
	tracks = await cursor.fetchall()
	return tracks

@app.get("/tracks/composers")
async def tracks_composers(response: Response, composer_name: str):
	router.db_connection.row_factory = lambda cursor, x: x[0]
	cursor = await router.db_connection.execute("SELECT Name FROM tracks WHERE Composer = ? ORDER BY Name",
		(composer_name, ))
	tracks = await cursor.fetchall()
	if len(tracks) == 0:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Cannot find any songs of that composer."}}
	return tracks

class Album(BaseModel):
	title: str
	artist_id: int

@app.post("/albums")
async def add_album(response: Response, album: Album):
	router.db_connection.row_factory = None
	cursor = await router.db_connection.execute("SELECT ArtistId FROM artists WHERE ArtistId = ?",
		(album.artist_id, ))
	result = await cursor.fetchone()
	if result is None:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Artist with that ID does not exist."}}
	cursor = await router.db_connection.execute("INSERT INTO albums (Title, ArtistId) VALUES (?, ?)",
		(album.title, album.artist_id))
	await router.db_connection.commit()
	response.status_code = status.HTTP_201_CREATED
	return {"AlbumId": cursor.lastrowid, "Title": album.title, "ArtistId": album.artist_id}

@app.get("/albums/{album_id}")
async def tracks_composers(response: Response, album_id: int):
	router.db_connection.row_factory = aiosqlite.Row
	cursor = await router.db_connection.execute("SELECT * FROM albums WHERE AlbumId = ?",
		(album_id, ))
	album = await cursor.fetchone()
	if album is None: # Not required by tests, but why not :)
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Album with that ID does not exist."}}
	return album

class Customer(BaseModel):
	company: str = None
	address: str = None
	city: str = None
	state: str = None
	country: str = None
	postalcode: str = None
	fax: str = None

@app.put("/customers/{customer_id}")
async def tracks_composers(response: Response, customer_id: int, customer: Customer):
	cursor = await router.db_connection.execute("SELECT CustomerId FROM customers WHERE CustomerId = ?",
		(customer_id, ))
	result = await cursor.fetchone()
	if result is None:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Customer with that ID does not exist."}}
	update_customer = customer.dict(exclude_unset=True)
	values = list(update_customer.values())
	if len(values) != 0:
		values.append(customer_id)
		query = "UPDATE customers SET "
		for key, value in update_customer.items():
			key.capitalize()
			if key == "Postalcode":
				key = "PostalCode"
			query += f"{key}=?, "
		query = query[:-2]
		query += " WHERE CustomerId = ?"
		cursor = await router.db_connection.execute(query, tuple(values))
		await router.db_connection.commit()
	router.db_connection.row_factory = aiosqlite.Row
	cursor = await router.db_connection.execute("SELECT * FROM customers WHERE CustomerId = ?",
		(customer_id, ))
	customer = await cursor.fetchone()
	return customer

@app.get("/sales")
async def tracks_composers(response: Response, category: str):
	if category == "customers":
		router.db_connection.row_factory = aiosqlite.Row
		cursor = await router.db_connection.execute(
			"SELECT invoices.CustomerId, Email, Phone, ROUND(SUM(Total), 2) AS Sum "
			"FROM invoices JOIN customers on invoices.CustomerId = customers.CustomerId "
			"GROUP BY invoices.CustomerId ORDER BY Sum DESC, invoices.CustomerId")
		stats = await cursor.fetchall()
		return stats
	if category == "genres":
		router.db_connection.row_factory = aiosqlite.Row
		cursor = await router.db_connection.execute(
			"SELECT genres.Name, SUM(Quantity) AS Sum FROM invoice_items "
			"JOIN tracks ON invoice_items.TrackId = tracks.TrackId "
			"JOIN genres ON tracks.GenreId = genres.GenreId "
			"GROUP BY tracks.GenreId ORDER BY Sum DESC, genres.Name")
		stats = await cursor.fetchall()
		return stats
	else:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Unsuported category."}}