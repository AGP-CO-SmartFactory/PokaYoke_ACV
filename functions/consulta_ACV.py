from functions.sql_utilities import SqlUtilities
import pandas as pd


# Esta clase lee desde la base de datos, el estado de la ultima receta de las ACV
# Puede retornar un dataframe con valores booleanos


class Acv:

    def __init__(self):
        query = """SELECT * 
        FROM SF_CiclosLaminado WITH(NOLOCK)
        """
        self.estados_acv = SqlUtilities.get_database_sf(query)
        # print(self.estados_acv) #Confirmación

    def estado_acv(self):
        acv_ultimo_estado = self.estados_acv.loc[
            self.estados_acv.groupby("ID_acv")["Hora"].idxmax()
        ]
        acv_ultimo_estado["INACTIVO"] = (acv_ultimo_estado["Evento"] == "Final") & (
            acv_ultimo_estado["Etapa"] == "Finalizado"
        )
        acv_ultimo_estado = acv_ultimo_estado.drop(
            columns=["ID", "Consecutivo", "Evento", "Ciclo"], axis=0, inplace=False
        )
        # print(ultimo_estado) #Confirmación
        return acv_ultimo_estado
