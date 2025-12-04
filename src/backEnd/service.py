from fastapi import FastAPI, HTTPException
from src.backEnd.db import get_connection 
import src.backEnd.db as db
import src.backEnd.models as Model
from datetime import datetime

###---------------------------------------------------------------------------------------
###     UTILS
###---------------------------------------------------------------------------------------
def convert_update_model_requisitos(id, values):
    # dicionário sem None's
    updates = values.model_dump(exclude_none=True)

    # constrói as cláusulas da query com base nas chaves do dicionário
    set_clauses = [f"{field} = %s" for field in updates.keys()]

    # separa cláusulas com vírgula
    set_statement = ", ".join(set_clauses)

    # valores que serão atualizados
    update_values = list(updates.values())

    # inclui o id ao final para o WHERE
    query_values = update_values + [id]

    return query_values, set_statement

###---------------------------------------------------------------------------------------
###     PAGAMENTOS
###---------------------------------------------------------------------------------------

def pay_up (conn, user_id, amount, reservation_id):
    db.update_money(conn, user_id, amount, True, reservation_id)
    return {"message": "Pagamento realizado com sucesso!"}

def instant_pay_up(user_id, amount, reservation_id):
    db.instante_update_money(user_id, amount, True, reservation_id)
    return {"message": "Pagamento realizado com sucesso!"}

def retrieve_money (conn, user_id, amount, reservation_id):
    db.update_money(conn, user_id, amount, False, reservation_id)
    return {"message": "Extorno realizado com sucesso!"}

def instant_retrieve_money (user_id, amount, reservation_id):
    db.instante_update_money(user_id, amount, False, reservation_id)
    return {"message": "Extorno realizado com sucesso!"}

###---------------------------------------------------------------------------------------
###     RESERVAS
###---------------------------------------------------------------------------------------

def get_days (initTime, endTime):
    DATE_FORMAT = "%Y-%m-%d"

    initTime = datetime.strptime(initTime, DATE_FORMAT).date()
    endTime = datetime.strptime(endTime, DATE_FORMAT).date()
    duration = endTime - initTime
    return duration.days

def make_reserve (user_id, property_id, initTime, endTime):
    conn = get_connection()
    conn.autocommit = False
    
    try:
        if (endTime < initTime):    #verifica se o periodo de estadia e valido
            conn.rollback()
            raise HTTPException(status_code=403, detail="Período de estadia inválido!")
        
        conflict = db.verify_availability_lock(conn, property_id, initTime, endTime)    #verifica se ha conflito de reservas

        if conflict:
            conn.rollback()
            raise HTTPException(status_code=409, detail="Propriedade reservada para o periodo desejado!")
        
        reservation_id = db.make_reservation(conn, user_id, property_id, initTime, endTime) #realiza a reserva

        pay_up(conn, user_id, get_days(initTime, endTime) * db.property_value(property_id), reservation_id)   #tenta realizar o pagamento
        
        conn.commit()
        return {"message": "Reserva criada com sucesso!", "reservation_id": reservation_id}
    
    except Exception as e:
        if conn:
            conn.rollback()

        if isinstance(e, HTTPException):
            raise e

        print(f"Erro inesperado {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar a reserva")
        
    finally:
        if conn:
            conn.close()

def delete_reserve (reserva_id):
    try:
        data = db.getReserve(reserva_id)
        conn = get_connection()
        print ("BUSCA FOI")
        db.delete_reservation(conn, reserva_id)   #tenta cancelar a reserva
        print ("DELECAO EM SI FOI")
        retrieve_money(conn, data[1], db.property_value(data[2]) * get_days(data[3], data[4]), reservation_id=None) #se foi cancelado, retorna o valor
        conn.commit()
        return {"message": "Reserva deletada com sucesso!"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Server could not erase reservation")
    finally:
        conn.close()
         
def getReserves (userId):
    return db.getMyReserves(userId)

###---------------------------------------------------------------------------------------
###     PROPRIEDADES
###---------------------------------------------------------------------------------------
    
def find_property(address):
    return db.find_property(address)
    
def create_property (address, contact, property_name, value_per_day, capacity):
    try:
        db.create_property(address, contact, property_name, value_per_day, capacity)
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

def update_property (id, values):
    try:
        query, statement = convert_update_model_requisitos(id, values)
        db.update_property(id, statement, query)
    except Exception as e:
        if e.isinstance(HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Erro desconhecido no servidor!")
    finally:
        return {"message": "Propriedade atualizada com sucesso!"}
    
###---------------------------------------------------------------------------------------
###     CLIENTES
###---------------------------------------------------------------------------------------

def find_cpf(cpf):
    return db.find_client(cpf)
    
def create_client (email, password, cpf, numeroTel, nome, isAdmin, filial, wallet):
    try:
        db.create_client(email, password, cpf, numeroTel, nome, isAdmin, filial, wallet)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao criar cliente no banco")
    finally:
        return {"message": "Cliente registrado com sucesso!"}
    
def delete_client (client_id):
    try:
        db.delete_client(client_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao deletar o cliente")
    finally:
        return {"message": "Cliente deletado com sucesso!"}

def update_client (cpf, values):
    try:
        id = find_cpf(cpf)
        query, statement = convert_update_model_requisitos(id, values)
        db.update_client(id, statement, query)
    except Exception as e:
        if e.isinstance(HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Erro desconhecido no servidor!")
    finally:
        return {"message": "Cliente atualizado com sucesso!"}

###---------------------------------------------------------------------------------------
###     LOGIN
###---------------------------------------------------------------------------------------

def validarLogin(data):
    return db.validarLogin(data)

def cadastrarUsuario(data):
    return db.cadastrarUsuario(data)

def getProperties():
    return db.getPropertiesDB()