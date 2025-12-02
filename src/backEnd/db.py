import mysql.connector as db_driver
import src.backEnd.models as Model
from fastapi import FastAPI, HTTPException

###---------------------------------------------------------------------------------------
###     CONEXAO AO BANCO
###---------------------------------------------------------------------------------------

def get_connection():
    return db_driver.connect(
        host="bd",
        user="adm", 
        password="SECRET",
        database="seuCantinho",
        port=3306
    )

def estabilish_connection():
    conn = get_connection()
    cursor = conn.cursor()

    return conn, cursor

def abolish_connection(conn, cursor=None):
    if cursor:
        cursor.close()
    
    if conn and conn.is_connected():
        conn.close()

###---------------------------------------------------------------------------------------
###     MANIPULACAO DE DINHEIRO
###---------------------------------------------------------------------------------------

def update_money(renter_id, amount, withdraw, reserve_id):
    try:
        conn, cursor = estabilish_connection()
        
        if withdraw:
            cursor.execute(
                "UPDATE client SET wallet = wallet - %s WHERE id = %s AND wallet >= %s",
                (amount, renter_id, amount)
            )
        else:
            cursor.execute(
                "UPDATE client SET wallet = wallet + %s WHERE id = %s",
                (amount, renter_id)
            )

        rows_affected = cursor.rowcount
        if withdraw:
            amount = - amount
        if rows_affected == 0:
            conn.rollback()
            raise

        query = """
        INSERT INTO payments (value, renter_id, reserve_id)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (amount, renter_id, reserve_id))
        
        conn.commit()
    except db_driver.Error as e:
        if conn:
            conn.rollback()
        print (f"O ERRO FOI: {e}")
        raise HTTPException(status_code=403, detail="Saldo insuficiente!")
    finally:
        abolish_connection(conn, cursor)


###---------------------------------------------------------------------------------------
###     ALUGUEL
###---------------------------------------------------------------------------------------

def verify_availability_lock(conn, property_id, initTime, endTime):
    try:
        cursor = conn.cursor()
        
        query = """
        SELECT id, renter_id
        FROM property_reserves
        WHERE property_id = %s
        AND (
            initTime < %s AND endTime > %s
        )
        FOR UPDATE
        """

        cursor.execute(query, (property_id, endTime, initTime))

        conflict = cursor.fetchone()

    except db_driver.Error as e:
        print(f"Erro ao verificar disponibilidade de reserva no banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro ao verificar disponibilidade")

    finally:
        if cursor:
            cursor.close()

    if conflict:
        return {"id": conflict[0]}
    
    return None
    
def make_reservation(conn, user_id, property_id, initTime, endTime):
    try:
        cursor = conn.cursor()

        query = """
        INSERT INTO property_reserves (renter_id, property_id, initTime, endTime)
        VALUES (%s,%s,%s,%s)
        """

        cursor.execute(query, (user_id, property_id, initTime, endTime))

        new_reservation_id = cursor.lastrowid
    except db_driver.Error as e:
        print(f"Erro ao inserir reserva no banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar reserva")
    finally:
        if cursor:
            cursor.close()
        return new_reservation_id
    
def delete_reservation(user_id, property_id, initTime):
    try:
        conn, cursor = estabilish_connection()

        cursor.execute(
            "DELETE FROM property_reserves WHERE property_id = %s AND renter_id = %s AND initTime = %s",
            (property_id, user_id, initTime)
        )

        conn.commit()

    except db_driver.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro no banco de dados para deletar reserva: {e}")
        raise HTTPException(status_code=404, detail="Reserva não encontrada!")

    finally:
        abolish_connection(conn, cursor)

def getReserve (userId, property_id, initTime):
    try:
        conn, cursor = estabilish_connection()

        cursor.execute(
            "SELECT * FROM property_reserves WHERE renter_id = %d AND property_id = %d AND initTime = %s",
            (userId, property_id, initTime)
        )

        value = cursor.fetchone()
        return value
    except db_driver.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail="Erro ao buscar dados da reserva")
    finally:
        abolish_connection()

###---------------------------------------------------------------------------------------
###     PROPRIEDADE
###---------------------------------------------------------------------------------------

def property_value(property_id):
    try:
        conn, cursor = estabilish_connection()

        cursor.execute(
            "SELECT value_per_day FROM property WHERE id = %s",
            (property_id,)
        )

        row = cursor.fetchone()
        value = row[0] if isinstance(row, (tuple, list)) else row

        return int (value)

    except db_driver.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao verificar valor da propriedade: {e}")
        raise HTTPException(status_code=404, detail="Propriedade não encontrada!")
    finally:
        abolish_connection(conn, cursor)
        return value 
    
def find_property(address):
    try:
        conn, cursor = estabilish_connection()

        cursor.execute(
            "SELECT id FROM property WHERE address = %s",
            (address)
        )

        value = cursor.fetchone()

    except db_driver.Error as e:
        if conn:
            conn.rollback()
        print (f"Erro ao buscar a propriedade: {e}")
        raise HTTPException(status_code=404, detail="Propriedade não encontrada")
    finally:
        abolish_connection(conn, cursor)
    
    return value
        

def create_property(address, contact, property_name, value_per_day, capacity):
    try:
        conn, cursor = estabilish_connection()

        query = """
        INSERT INTO property (address, contact, property_name, value_per_day, capacity)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (address, contact, property_name, value_per_day, capacity))

        new_property_id = cursor.lastrowid

        conn.commit() 

        return new_property_id

    except db_driver.Error as e:
        print(f"Erro ao inserir no banco de propriedades: {e}")
        raise
    finally:
        abolish_connection(conn, cursor)
        
        
    
def delete_property(property_id):
    try:
        conn, cursor = estabilish_connection()

        cursor.execute("DELETE FROM property WHERE id = %s", (property_id,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Propriedade não encontrada!")

        return {"mensagem": "Propriedade removida com sucesso!"}

    except db_driver.Error as e:
        print(f"Erro ao deletar propriedade: {e}")
        raise

    finally:
        abolish_connection(conn, cursor)

def update_property(property_id, statements, values):
    try:
        conn, cursor = estabilish_connection()

        # # transforma o modelo Pydantic em dict
        # fields = data.dict()

        # # filtra somente campos enviados
        # fields = {k: v for k, v in fields.items() if v is not None}

        # if not fields:
        #     raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

        # # monta SET dinamicamente
        # set_clause = ", ".join(f"{col} = %s" for col in fields.keys())

        # values = list(fields.values())
        # values.append(property_id)  # ID vai no WHERE

        sql = f"""
            UPDATE property
            SET {statements}
            WHERE id = %s
        """

        cursor.execute(sql, values)
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Propriedade não encontrada")

        return {"mensagem": "Propriedade atualizada com sucesso!"}

    except db_driver.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao atualizar propriedade: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar propriedade")

    finally:
        abolish_connection(conn, cursor)

def getPropertiesDB():

    try:
        conn, cursor = estabilish_connection()

        query = """
        SELECT 
            id,
            property_name,
            address,
            contact,
            value_per_day,
            capacity
        FROM property
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        # Pega os nomes das colunas
        columns = [col[0] for col in cursor.description]

        # Converte cada linha em um dict
        propriedades = [dict(zip(columns, row)) for row in rows]

        return propriedades

    except db_driver.Error as e:
        print(f"Erro ao puxar propriedades: {e}")
        raise

    finally:
        abolish_connection(conn, cursor)

###---------------------------------------------------------------------------------------
###     USUÁRIO
###---------------------------------------------------------------------------------------

def find_client(cpf):
    try:
        conn, cursor = estabilish_connection()

        cursor.execute(
            "SELECT id FROM client WHERE CPF = %s",
            (cpf)
        )

        value = cursor.fetchone()

    except db_driver.Error as e:
        if conn:
            conn.rollback()
        print (f"Erro ao buscar o cliente: {e}")
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    finally:
        abolish_connection(conn, cursor)
    
    return value

def create_client(email, password, cpf, numeroTel, nome, isAdmin, filial, wallet):
    try:
        conn, cursor = get_connection()
        query = """
            INSERT INTO client(email, password, cpf, numeroTel, nome, isAdmin, filial, wallet)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (email, password, cpf, numeroTel, nome, isAdmin, filial, wallet))
        conn.commit()
    except db_driver.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao criar client: {e}")
        raise
    finally:
        abolish_connection(conn, cursor)

def update_client(client_id, statements, values):
    try:
        conn, cursor = estabilish_connection()

        sql_query = """
        UPDATE client
        SET {statement}
        WHERE id = %s
        """

        cursor.execute(sql_query, tuple(values))

        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Cliente não encontrado!")

        conn.commit()

        return {"message": "Cliente atualizada com sucesso!"}
    except db_driver.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao atualizar cliente: {e}")
        raise
    finally:
        abolish_connection(conn, cursor)

def delete_client(client_id):
    try:
        conn, cursor = estabilish_connection()

        cursor.execute("DELETE FROM client WHERE client_id = %s",
                       (client_id)
        )

        conn.commit()

    except db_driver.Error as e:
        if conn:
            conn.rollback()
        print (f"Erro ao deletar o cliente: {e}")
        raise HTTPException(status_code=404, detail="Cliente não encontrado!")
    finally:
        abolish_connection(conn, cursor)

###---------------------------------------------------------------------------------------
###     LOGIN/CADASTRO
###---------------------------------------------------------------------------------------

def validarLogin(data: Model.Login):
    
        try:
            conn, cursor = estabilish_connection()

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
        except Exception as e:
            if e.isinstance(HTTPException):
                raise e
            raise HTTPException(status_code=500, detail="Erro desconhecido no servidor!")

def cadastrarUsuario(data: Model.ClientCreate):

        conn, cursor = estabilish_connection()

        cursor.execute(
                """
                INSERT INTO client (email, nome, cpf, isAdmin, filial, password, wallet, numeroTel)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (data.email, data.nome, data.CPF, data.isAdmin, data.filial, data.password, data.wallet, data.numeroTel)
        )

        conn.commit()

        novo_id = cursor.lastrowid

        abolish_connection()

        return {"mensagem": "Usuário criado com sucesso!", "id": novo_id}


###---------------------------------------------------------------------------------------
###     RESERVAS
###---------------------------------------------------------------------------------------

def createReserve(data: Model.PropertyReserveCreate):
    try:
        # Conexão com o banco
        conn, cursor = estabilish_connection()

        # 1 — Buscar capacidade da propriedade
        cursor.execute(
            "SELECT capacity FROM property WHERE id = %s",
            (data.property_id,)
        )

        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Propriedade não encontrada!")

        capacity = result[0]

        print("---- NOVA RESERVA RECEBIDA ----")
        print(f"Renter ID: {data.renter_id}")
        print(f"Property ID: {data.property_id}")
        print(f"Init Time: {data.initTime}")
        print(f"End Time: {data.endTime}")
        print(f"Capacity encontrada: {capacity}")
        print("--------------------------------")

        # 2 — Inserir na tabela property_reserves
        insert_query = """
            INSERT INTO property_reserves (renter_id, property_id, initTime, endTime, capacity)
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            insert_query,
            (data.renter_id, data.property_id, data.initTime, data.endTime, capacity)
        )

        conn.commit()

        novo_id = cursor.lastrowid

        return {"mensagem": "Reserva criada com sucesso!", "id": novo_id}

    except db_driver.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao criar reserva: {e}")
        raise HTTPException(status_code=500, detail="Erro no banco de dados.")

    finally:
        abolish_connection(conn, cursor)

def getMyReserves(renter_id: int):
    conn, cursor = estabilish_connection()
    cursor.execute(
        "SELECT * FROM property_reserves WHERE renter_id = %s",
        (renter_id,)
    )
    reservas = cursor.fetchall()
    abolish_connection(conn, cursor)
    return [
        {
            "id": r[0],
            "renter_id": r[1],
            "property_id": r[2],
            "initTime": r[3],
            "endTime": r[4],
            "capacity": r[5],
        }
        for r in reservas
    ]

def delete_reserva(reserva_id: int):
    try:
        conn, cursor = estabilish_connection()

        cursor.execute(
            "DELETE FROM property_reserves WHERE id = %s",
            (reserva_id,)
        )

        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Reserva não encontrada!")

        return {"mensagem": "Reserva removida com sucesso!"}

    except db_driver.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao deletar reserva: {e}")
        raise HTTPException(status_code=500, detail="Erro no banco.")

    finally:
        abolish_connection(conn, cursor)
