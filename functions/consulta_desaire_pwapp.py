from functions.sql_utilities import SqlUtilities
from functions.log_manager import LogManager

# Esta clase lee desde la base de datos de registro de salida de desaire para retornar
# un dataframe que me permita hacer el registro de múltiples órdenes aprobadas a la
# salida de embolsado

log_manager = LogManager()

class BdPowerApp:

    @log_manager.log_errors(sector = 'BD_Desaireacion_SAP')
    def piezas_sin_cargar(self):
        query = """WITH OrdenesUnicas AS (
            SELECT DISTINCT Orden, Cargado_SAP
            FROM SF_Cargue_SAP_Desaire WITH(NOLOCK)
            WHERE Cargado_SAP = 0
        )
        SELECT OU.Orden, OU.Cargado_SAP, MIN(T.id) AS id, MIN(T.Id_operario) AS Id_operario
        FROM OrdenesUnicas OU
        JOIN SF_Cargue_SAP_Desaire T
        ON OU.Orden = T.Orden AND OU.Cargado_SAP = T.Cargado_SAP
        GROUP BY OU.Orden, OU.Cargado_SAP;
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
