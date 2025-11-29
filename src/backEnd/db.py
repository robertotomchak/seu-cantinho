import mysql.connector as db_driver
import src.backEnd.models as Model
from fastapi import FastAPI, HTTPException

###---------------------------------------------------------------------------------------
###     CONEXAO AO BANCO
###---------------------------------------------------------------------------------------

def get_connection():
    return db_driver.connect(
        host="localhost",
        user="igor", 
        password="!Igor2002",
        database="seuCantinho",
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

def update_money (user_id, amount, withdraw):
    try:
        conn, cursor = estabilish_connection()
        
        if withdraw:
            cursor.execute(
                "UPDATE client SET wallet = wallet - %s WHERE id = %s AND wallet >= %s",
                (amount, user_id, amount)
            )
        else:
            cursor.execute(
                "UPDATE client SET wallet = wallet + %s WHERE id = %s",
                (amount, user_id, amount)
            )            

        rows_affected = cursor.rowcount
        if rows_affected == 0:
            conn.rollback()
            raise
        
        conn.commit()
    except db_driver.Error as e:
        if conn:
            conn.rollback()
        raise
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
        raise

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
        raise
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

###---------------------------------------------------------------------------------------
###     PROPRIEDADE
###---------------------------------------------------------------------------------------

def property_value (property_id):
    try:
        conn, cursor = estabilish_connection()

        cursor.execute(
            "SELECT value_per_day FROM property WHERE id = %s",
            (property_id)
        )

        value = cursor.fetchone()

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
        

def create_property(address, contact, property_name, value_per_day):
    try:
        conn, cursor = estabilish_connection()

        query = """
        INSERT INTO property (address, contact, property_name, value_per_day)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (address, contact, property_name, value_per_day))

        new_property_id = cursor.lastrowid
    except db_driver.Error as e:
        print(f"Erro ao inserir no banco de propriedades: {e}")
        raise
    finally:
        abolish_connection(conn, cursor)

        return new_property_id
    
def delete_property(property_id):
    try:
        conn, cursor = estabilish_connection()

        cursor.execute("DELETE FROM property WHERE property_id = %s",
                       (property_id)
        )

        conn.commit()

    except db_driver.Error as e:
        if conn:
            conn.rollback()
        print (f"Erro ao deletar a propriedade: {e}")
        raise HTTPException(status_code=404, detail="Propriedade não encontrada!")
    finally:
        abolish_connection(conn, cursor)

def update_property(property_id, statement, values):
    try:
        conn, cursor = estabilish_connection()

        sql_query = """
        UPDATE property
        SET {statement}
        WHERE id = %s
        """

        cursor.execute(sql_query, tuple(values))

        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Propriedade não encontrada!")

        conn.commit()

        return {"message": "Propriedade atualizada com sucesso!"}
    except db_driver.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao atualizar propriedade: {e}")
        raise
    finally:
        abolish_connection(conn, cursor)