import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="igor", 
        password="!Igor2002",
        database="seuCantinho",
    )