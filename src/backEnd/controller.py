from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.backEnd.db import get_connection 

app = FastAPI()

origins = [
        "http://localhost:9999",
        "http://127.0.0.1:9999",
]

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_methods=["*"],
        allow_headers=["*"],
)

class Login(BaseModel):
        email: str
        password: str

@app.post("/login")
def validarLogin(data: Login):
    
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
                "SELECT id, isAdmin, nome FROM client WHERE email = %s AND password = %s",
                (data.email, data.password)
        )

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
                usuario_id = row[0]
                isAdmin = row[1]
                nome = row[2]
                return {"mensagem": "Login OK", 
                "usuario_id": usuario_id,
                "isAdmin": isAdmin,
                "nome": nome
                }
        else:
                raise HTTPException(status_code=401, detail="Credenciais inválidas")

@app.put("/login")
def atualizarLogin(data: Login):

        print("papo")