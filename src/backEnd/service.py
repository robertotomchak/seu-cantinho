"""
    Camada Service
    Envia informações para o Controller, chama camada de repositório para obter dados
    OBS: Regras de negócio podem ser vistas na documentação de cada função
"""

from fastapi import FastAPI, HTTPException
from src.backEnd.db import get_connection 
import src.backEnd.db as db
import src.backEnd.models as Model
from datetime import datetime

###---------------------------------------------------------------------------------------
###     UTILS
###---------------------------------------------------------------------------------------

# função auxiliar para atualizações parciais (PUT)
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

# retorna quantos dias tem entre duas datas
def get_days (initTime, endTime):
    DATE_FORMAT = "%Y-%m-%d"

    initTime = datetime.strptime(initTime, DATE_FORMAT).date()
    endTime = datetime.strptime(endTime, DATE_FORMAT).date()
    duration = endTime - initTime
    return duration.days

###---------------------------------------------------------------------------------------
###     PAGAMENTOS
###---------------------------------------------------------------------------------------

# realiza o pagamento de uma reserva
# OBS: passa conexão como argumento para o Repository
def pay_up (conn, user_id, amount, reservation_id):
    db.update_money(conn, user_id, amount, True, reservation_id)
    return {"message": "Pagamento realizado com sucesso!"}

# realiza o pagamento de uma reserva
# OBS: não cria uma conexão, passando essa responsabilidade para o Repository
def instant_pay_up(user_id, amount, reservation_id):
    db.instante_update_money(user_id, amount, True, reservation_id)
    return {"message": "Pagamento realizado com sucesso!"}

# realiza o extorno de uma reserva
# OBS: passa conexão como argumento para o Repository
def retrieve_money (conn, user_id, amount, reservation_id):
    db.update_money(conn, user_id, amount, False, reservation_id)
    return {"message": "Extorno realizado com sucesso!"}

# realiza o extorno de uma reserva
# OBS: não cria uma conexão, passando essa responsabilidade para o Repository
def instant_retrieve_money (user_id, amount, reservation_id):
    db.instante_update_money(user_id, amount, False, reservation_id)
    return {"message": "Extorno realizado com sucesso!"}

###---------------------------------------------------------------------------------------
###     RESERVAS
###---------------------------------------------------------------------------------------

# realiza uma reserva
# REGRAS DE NEGÓCIO: 
# 1. período de estadia deve ser válido (dia fim após dia começo)
# 2. pagamento é feito automaticamente
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

# deleta uma reserva
# REGRAS DE NEGÓCIO:
# 1. o registro do pagamento é mantido no banco de dados
def delete_reserve (reserva_id):
    try:
        data = db.getReserve(reserva_id)
        print ("BUSCA FOI")
        db.delete_reservation(reserva_id)   #tenta cancelar a reserva
        print ("DELECAO EM SI FOI")
        instant_retrieve_money(data[1], db.property_value(data[2]) * get_days(data[3], data[4]), reservation_id=None) #se foi cancelado, retorna o valor
        return {"message": "Reserva deletada com sucesso!"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Server could not erase reservation")
    
# retorna as reservas de um usuário
def getReserves (userId):
    return db.getMyReserves(userId)

###---------------------------------------------------------------------------------------
###     PROPRIEDADES
###---------------------------------------------------------------------------------------
    
# encontra uma propriedade, com base no seu endereço
def find_property(address):
    return db.find_property(address)
    
# adiciona uma propriedade no sistema
def create_property (address, contact, property_name, value_per_day, capacity):
    try:
        db.create_property(address, contact, property_name, value_per_day, capacity)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao criar propriedade no banco")
    finally:
        return {"message": "Propriedade registrada com sucesso!"}
    
# deleta uma propriedade, com base no seu id
def delete_property (property_id):
    try:
        db.delete_property(property_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao deletar a propriedade")
    finally:
        return {"message": "Propriedade deletada com sucesso!"}

# atualiza alguns campos de uma propriedade, com base no seu id
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
    
# retorna todas as propriedades presentes no sistema
def getProperties():
    return db.getPropertiesDB()
    
###---------------------------------------------------------------------------------------
###     CLIENTES
###---------------------------------------------------------------------------------------

# encontra um cliente, com base no seu cpf
def find_cpf(cpf):
    return db.find_client(cpf)
    
# cria um cliente no sistema
def create_client (email, password, cpf, numeroTel, nome, isAdmin, filial, wallet):
    try:
        db.create_client(email, password, cpf, numeroTel, nome, isAdmin, filial, wallet)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao criar cliente no banco")
    finally:
        return {"message": "Cliente registrado com sucesso!"}
    
# deleta um cliente, com base no seu id
def delete_client (client_id):
    try:
        db.delete_client(client_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao deletar o cliente")
    finally:
        return {"message": "Cliente deletado com sucesso!"}

# atualiza alguns campos de um cliente, com base no seu cpf
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

# valida um login
def validarLogin(data):
    return db.validarLogin(data)

# cadastra um usuário
def cadastrarUsuario(data):
    return db.cadastrarUsuario(data)