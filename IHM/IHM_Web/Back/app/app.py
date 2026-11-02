from fastapi import FastAPI
from Sensor import Sensor


sensors ={Sensor("42900")}



app = FastAPI()

@app.get("/")
def accueil():
    return {"message": "Bienvenue sur mon serveur IoT"}

@app.get("/temperature")
def temperature():
    return {"temperature": 22.5}