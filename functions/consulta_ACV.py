from functions.sql_utilities import SqlUtilities
import pandas as pd
import traceback


# Esta clase lee desde la base de datos, el estado de la ultima receta de las ACV
# Puede retornar un dataframe con valores booleanos
def log_errors(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.log_error(func.__name__, e)
            return None
    return wrapper

class Acv:

    def __init__(self):
        query = """SELECT * 
        FROM SF_CiclosLaminado WITH(NOLOCK)
        """
        self.estados_acv = SqlUtilities.get_database_sf(query)
        # print(self.estados_acv) #Confirmación
    @log_errors

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
        print(acv_ultimo_estado) #Confirmación
        return acv_ultimo_estado
    @log_errors

    def log_error(self, method_name, exception):
        with open("error_log.txt", "a") as error_file:
            with open("error_log.txt", "a") as error_file:
                error_file.write(f"Error en {method_name}: {str(exception)}\n")
