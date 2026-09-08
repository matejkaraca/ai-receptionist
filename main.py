from fastapi import FastAPI 
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from supabase import create_client
import httpx

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

class Prijava(BaseModel):
    ime: str
    telefon: str
    opis: str

class Upit(BaseModel):
    datum: str



@app.get("/")
def pocetna():
    return {"status":"Ana je Online"}

@app.post("/slots")
def slobodni_termini(podaci: Upit):
    svi_termini = ["09:00", "11:00", "14:00", "17:00"]

    rezervacije = supabase.table("appointments").select("vrijeme").eq("datum", podaci.datum).eq("status", "booked").execute()

    zauzeti = [r["vrijeme"][:5] for r in rezervacije.data]

    slobodni = [t for t in svi_termini if t not in zauzeti]

    return {"datum": podaci.datum, "slobodni_termini": slobodni}


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

    try:
        r = httpx.post(os.getenv("N8N_WEBHOOK_URL"), json={
            "ime": podaci.ime,
            "telefon": podaci.telefon,
            "datum": podaci.datum,
            "vrijeme": podaci.vrijeme,
            "opis": podaci.opis
        }, timeout=5)
        print(f"n8n odgovor: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"n8n webhook nije uspio: {e}")

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

@app.post("/ticket")
def otvori_ticket(podaci: Prijava):
    postojeci = supabase.table("customers").select("*").eq("telefon", podaci.telefon).execute()

    if len(postojeci.data) > 0:
        customer_id = postojeci.data[0]["id"]
    else:
        novi = supabase.table("customers").insert({
            "ime": podaci.ime,
            "telefon": podaci.telefon
        }).execute()
        customer_id = novi.data[0]["id"]

    ticket = supabase.table("tickets").insert({
        "customer_id": customer_id,
        "opis": podaci.opis
    }).execute()

    return {
        "status": "otvoren",
        "ticket_id": ticket.data[0]["id"],
        "ime": podaci.ime
    }