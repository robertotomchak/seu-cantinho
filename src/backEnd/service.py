from fastapi import FastAPI, HTTPException
from src.backEnd.db import get_connection 
import src.backEnd.db as db

def pay_up (user_id, amount):
    db.update_money(user_id, amount, True)
    return {"message": "Pagamento realizado com sucesso!"}

def retrieve_money (user_id, amount):
    db.update_money(user_id, amount, False)
    return {"message": "Extorno realizado com sucesso!"}

def make_reserve (user_id, property_id, initTime, endTime):
    conn = get_connection()
    conn.autocommit = False
    
    try:
        conflict = db.verify_availability_lock(conn, property_id, initTime, endTime)

        if conflict:
            conn.rollback()
            raise HTTPException(status_code=409, detail="Propriedade reservada para o periodo desejado!")
        
        reservation_id = db.make_reservation(conn, user_id, property_id, initTime, endTime)

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
        db.delete_reservation(user_id, property_id, initTime)
        db.update_money(user_id, db.property_value(property_id), False)
    except Exception as e:  #AQUI TALVEZ SEJA INTERESSANTE RETORNAR UM ERRO ESPECIFICO SE A RESERVA NAO FOR DO USER OU SE NAO ACHAR
        raise HTTPException(status_code=500, detail="Server could not erase reservation")
    finally: 
        return {"message": "Reserva deletada com sucesso!"}