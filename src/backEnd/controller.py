from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.backEnd.db import get_connection 
import src.backEnd.service as service
import src.backEnd.models as models
import src.backEnd.db as db

app = FastAPI()

origins = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
]

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,  
        allow_methods=["*"],
        allow_headers=["*"],
)

# Servicos referentes ao login

@app.post("/login")
def POSTlogin(data: models.Login):

        return db.validarLogin(data)


@app.put("/login")
def atualizarLogin(data: models.Login):

        print("teste")  

@app.post("/signup")
def POSTsignup(data: models.ClientCreate):

        return db.cadastrarUsuario(data)

# Servicos referentes ao cadastro de espaco

@app.post("/properties/create")
def POSTreserve(data: models.PropertyCreate):

        return db.create_property(data.address, data.contact, data.property_name, data.value_per_day, data.capacity)

@app.put("/properties/update/{property_id}")
def PUTproperty(property_id: int, data: models.PropertyUpdate):
    
        return db.update_property(property_id, data)

@app.delete("/properties/delete/{property_id}")
def DELETEproperty(property_id: int):
        return db.delete_property(property_id)

@app.get("/properties/get/all")
def GETALLproperties():

        return db.getPropertiesDB()


@app.post("/reserve/create")
def POSTreserva(data: models.PropertyReserveCreate):

        return db.createReserve(data)

@app.get("/reserve/get/{user_id}")
def GETreserva(user_id: int):

        return db.getMyReserves(user_id);

@app.delete("/reserve/delete/{reserva_id}")
def delete_reserva(reserva_id: int):
    return db.delete_reserva(reserva_id)


#@app.post("/reserve/update")
#def PUTreserve(data: models.PropertyUpdate):
