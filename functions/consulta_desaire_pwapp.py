from functions.sql_utilities import SqlUtilities
from functions.log_manager import LogManager

# Esta clase lee desde la base de datos de registro de salida de desaire para retornar
# un dataframe que me permita hacer el registro de múltiples órdenes aprobadas a la
# salida de embolsado

log_manager = LogManager()

class BdPowerApp:

    @log_manager.log_errors(sector = 'BD_Desaireacion_SAP')
    def piezas_sin_cargar(self):
        query = """SELECT * 
        FROM SF_Cargue_SAP_Desaire WITH(NOLOCK)
        WHERE Fecha_cargue_PowerAPP > DATEADD(day, -5, CAST(GETDATE() AS date)) AND
        Cargado_SAP = 0
        """
        self.piezas_sin_cargue_SAP = SqlUtilities.get_database_sf(query)
        return self.piezas_sin_cargue_SAP

    @log_manager.log_errors(sector = 'BD_Desaireacion_SAP')
    def modificar_estado_cargue_sap(self, primary_keys):
        primary_keys_str = ",".join([str(key) for key in primary_keys])
        query = f""" UPDATE SF_Cargue_SAP_Desaire
        SET Cargado_SAP = 1, Fecha_cargue_SAP = GETDATE()
        WHERE id IN ({primary_keys_str})
        """
        SqlUtilities.insert_database_sf(query)
