from functions.sql_utilities import SqlUtilities
import pandas as pd

# imports para pruebas de codigo
from datetime import datetime

# Esta clase lee desde la base de datos de registro de salida de desaire para retornar
# un dataframe que me permita hacer el registro de múltiples órdenes aprobadas a la
# salida de embolsado


class BdPowerApp:

    def piezas_sin_cargar(self):
        query = """SELECT * 
        FROM SF_Cargue_SAP_Desaire WITH(NOLOCK)
        WHERE Fecha_cargue_PowerAPP > DATEADD(day, -5, CAST(GETDATE() AS date))
        AND Cargado_SAP = 0
        """
        self.piezas_sin_cargue_SAP = SqlUtilities.get_database_sf(query)
        return self.piezas_sin_cargue_SAP

    def modificar_estado_cargue_sap(primary_keys):
        primary_keys_str = ",".join([str(key) for key in primary_keys])
        query = f""" UPDATE SF_Cargue_SAP_Desaire
        SET Cargado_SAP = 1, Fecha_cargue_SAP = GETDATE()
        WHERE id IN ({primary_keys_str})
        """
        SqlUtilities.insert_database_sf(query)
