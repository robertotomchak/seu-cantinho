from fastapi import FastAPI, HTTPException
from src.backEnd.db import get_connection 
import src.backEnd.db as db

def pay_up (user_id, amount):
    db.update_money(user_id, amount, True)
    return {"message": "Pagamento realizado com sucesso!"}

def retrieve_money (user_id, amount):
    db.update_money(user_id, amount, False)
    return {"message": "Extorno realizado com sucesso!"}

def get_days (initTime, endTime):
    duration = (endTime - initTime)
    return duration.days

def make_reserve (user_id, property_id, initTime, endTime):
    conn = get_connection()
    conn.autocommit = False
    
    try:
        if (endTime < initTime):    #verifica se o periodo de estadia e valido
            conn.rollback()     #precisa aqui?
            raise HTTPException(status_code=403, detail="Período de estadia inválido!")
        
        pay_up(user_id, get_days(initTime, endTime) * db.property_value(property_id))   #tenta realizar o pagamento
        
        conflict = db.verify_availability_lock(conn, property_id, initTime, endTime)    #verifica se ha conflito de reservas

        if conflict:
            conn.rollback()
            raise HTTPException(status_code=409, detail="Propriedade reservada para o periodo desejado!")
        
        reservation_id = db.make_reservation(conn, user_id, property_id, initTime, endTime) #realiza a reserva

        conn.commit()
        return {"message": "Reserva criada com sucesso!", "reservation_id": reservation_id}
    
    except Exception as e:
        if conn:
            conn.rollback()

        if isinstance(e, HTTPException):
            raise

        print(f"Erro inesperado {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar a reserva")
        
    finally:
        if conn:
            conn.close()

def delete_reserve (user_id, property_id, initTime):
    try:
        db.delete_reservation(user_id, property_id, initTime)   #tenta cancelar a reserva
        db.update_money(user_id, db.property_value(property_id), False) #se foi cancelado, retorna o valor
    except Exception as e:  #AQUI TALVEZ SEJA INTERESSANTE RETORNAR UM ERRO ESPECIFICO SE A RESERVA NAO FOR DO USER OU SE NAO ACHAR
        raise HTTPException(status_code=500, detail="Server could not erase reservation")
    finally: 
        return {"message": "Reserva deletada com sucesso!"}
    
def find_property(address):
    return db.find_property
    
def create_property (address, contact, property_name, value_per_day):
    try:
        db.create_property(address, contact, property_name, value_per_day)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao criar propriedade no banco")
    finally:
        return {"message": "Propriedade registrada com sucesso!"}
    
def delete_property (property_id):
    try:
        db.delete_property(property_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao deletar a propriedade")
    finally:
        return {"message": "Propriedade deletada com sucesso!"}
    
def update_property (address, values):
    try:
        id = find_property(address)