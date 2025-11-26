import mysql.connector
import mysql.connector as db_driver

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="igor", 
        password="!Igor2002",
        database="seuCantinho",
    )

def verify_availability_lock(conn, property_id, initTime, endTime):
    try:
        cursor = conn.cursor()
        
        query = """
        SELECT id, renter_id
        FROM property_reserves
        WHERE property_id = %s
        AND (
            initTime > %s OR endTime < %s
        )
        FOR UPDATE
        """

        cursor.execute(query, (property_id, endTime, initTime))

        conflict = cursor.fetchone()
        cursor.close()
    except mysql.Error as e:
        print(f"Erro ao verificar disponibilidade de reserva no banco de dados: {e}")
        raise

    finally:
        if conflict:
            return {"id": conflict[0], "renter_id": conflict[1]}    #nao sei se retorna o renter_id     
                                                                    #parece me ser falha de seguranca
        if cursor:
            cursor.close()
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
    except mysql.Error as e:
        print(f"Erro ao inserir reserva no banco de dados: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        return new_reservation_id
    
def delete_reservation(user_id, property_id, initTime):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE * FROM property_reserves WHERE property_id = %s AND renter_id = %s AND initTime = %s",
            (property_id, user_id, initTime)
        )

        cursor.commit()

    except mysql.Error as e:
        cursor.rollback()
        print(f"Erro no banco de dados para deletar reserva: {e}")
        raise

    finally:
        cursor.close()
        conn.close()

def update_money (user_id, amount, withdraw):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if withdraw:
            cursor.execute(
                "UPDATE client SET wallet = wallet - %s WHERE id = %s AND wallet >= %s",
                (amount, user_id, amount)
            )
        else:
            cursor.execute(
                "UPDATE client SET wallet = wallet + %s WHERE id = %s AND wallet >= %s",
                (amount, user_id, amount)
            )            

        rows_affected = cursor.rowcount
        if rows_affected == 0:
            conn.rollback()
            raise
        
        conn.commit()
    except mysql.Error as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def property_value (property_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT value FROM property WHERE id = %s",
        (property_id)
    )

    value = cursor.fetchone()

    cursor.close()
    conn.close()

    return value 