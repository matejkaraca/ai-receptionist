from fastapi import FastAPI 
from pydantic import BaseModel

app = FastAPI()

class Rezervacija(BaseModel):
    ime: str
    telefon: str
    datum: str
    vrijeme: str
    opis: str


@app.get("/")
def pocetna():
    return {"status":"Ana je Online"}

@app.get("/slots")
def slobodni_termini(datum: str):
    termini = ["09:00", "11:00", "14:00", "17:00"]
    return {"datum": datum, "slobodni_termini": termini }

@app.post("/book")
def rezerviraj(podaci: Rezervacija):
    return {
        "status": "rezervirano", 
        "ime": podaci.ime,
        "datum": podaci.datum,
        "vrijeme": podaci.vrijeme
    }
