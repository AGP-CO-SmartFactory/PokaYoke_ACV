import sqlalchemy
from sqlalchemy import create_engine
import pyodbc
import os, sys, json, warnings
import pandas as pd


class SqlUtilities:
    def connect_sql(credenciales):

        with open(credenciales, "r") as file:
            credenciales = json.load(file)
            server_c = credenciales.get("SERVER")
            db_c = credenciales.get("DB")
            driver_c = credenciales.get("DRIVER")
            user_c = credenciales.get("USER")
            password_c = credenciales.get("PASSWORD")

        # Conexión SQL para recibir datos
        conn = pyodbc.connect(
            f"Driver={driver_c};"
            f"Server={server_c};"
            f"Database={db_c};"
            f"UID={user_c};"
            f"PWD={password_c};"
            "Trusted_Connections=yes"
        )

        # Conexión SQL para enviar datos
        connection_url = sqlalchemy.URL.create(
            "mssql+pyodbc",
            username=user_c,
            password=password_c,
            host=server_c,
            database=db_c,
            port=1433,
            query={
                "driver": driver_c,
                "TrustServerCertificate": "yes",
            },
        )
        engine = sqlalchemy.create_engine(connection_url)
        connection = engine.connect()
        return conn

    def get_database_calendar(query: str):
        file_path = "data_loader/datos_calendar.json"
        conn = SqlUtilities.connect_sql(file_path)
        bd = pd.read_sql(sql=query, con=conn)
        return bd
    
    def get_database_sf(query: str):
        file_path = "data_loader/datos_sf.json"
        conn = SqlUtilities.connect_sql(file_path)
        bd = pd.read_sql(sql=query, con=conn)
        return bd
    
    def get_database_com(query: str):
        file_path = "data_loader/datos_com.json"
        conn = SqlUtilities.connect_sql(file_path)
        bd = pd.read_sql(sql=query, con=conn)
        return bd