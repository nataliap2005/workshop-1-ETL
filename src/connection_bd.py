# src/connection_bd.py
import mysql.connector as mysql
from sqlalchemy import create_engine

def get_conn():
    return mysql.connect(host="localhost", user="root", password="root", port=3306)

def get_conn_db(db="hiring_dw"):
    return mysql.connect(host="localhost", user="root", password="root", port=3306, database=db)

def get_engine_db(db="hiring_dw"):
    url = f"mysql+mysqlconnector://root:root@localhost:3306/{db}"
    return create_engine(url, pool_pre_ping=True)
