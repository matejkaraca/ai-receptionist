from fastapi import FastAPI 
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv ()

supabase = create_client (
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

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
    postojeci = supabase.table("customers").select("*").eq("telefon", podaci.telefon).execute()

    if len(postojeci.data) > 0:
        customer_id = postojeci.data[0]["id"]
    else:
        novi = supabase.table("customers").insert({
            "ime": podaci.ime,
            "telefon": podaci.telefon
        }).execute()
        customer_id = novi.data[0]["id"]

    supabase.table("appointments").insert({
        "customer_id": customer_id,
        "datum": podaci.datum,
        "vrijeme": podaci.vrijeme,
        "opis": podaci.opis
    }).execute()

    return {
        "status": "rezervirano",
        "ime": podaci.ime,
        "datum": podaci.datum,
        "vrijeme": podaci.vrijeme
    }

@app.get("/test-baza")
def test_baza():
    rezultat = supabase.table("customers").select("*").execute()
    return {"broj_kupaca": len(rezultat.data)}