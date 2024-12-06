from functions.sql_utilities import SqlUtilities
import pandas as pd

# Esta clase se encarga de entregar un estado OK (1) o NO OK (0) para los tiempos de desaireación de las piezas en embolsado


class EstadoPiezas:

    def __init__(self):
        query = """SELECT Orden, AGPLevel, TXT_MATERIAL, DATE_NOTIF, HRA_NOTIF, CLV_MODEL 
        FROM VW_CAMBIOESTADO WITH(NOLOCK)
        WHERE DATE_NOTIF > DATEADD(day,-2, CAST(GETDATE() AS date))
        AND (CLV_MODEL = 'EMBOLSA' OR CLV_MODEL = 'DESAIRE')
        """
        self.cambioestado = SqlUtilities.get_database_com(query)
        # print(self.cambioestado) #Confirmación

    def añadir_columna_datetime(self):
        self.cambioestado["Date_Registro"] = pd.to_datetime(
            self.cambioestado["DATE_NOTIF"] + " " + self.cambioestado["HRA_NOTIF"]
        )

    def crear_dataframe_embolsado(self):
        self.df_embolsado = self.cambioestado[
            self.cambioestado["CLV_MODEL"] == "EMBOLSA"
        ][["Orden", "AGPLevel", "TXT_MATERIAL", "Date_Registro"]].rename(
            columns={"Date_Registro": "RegistroEmbolsa"}
        )

    def crear_dataframe_desaire(self):
        self.df_desaire = self.cambioestado[
            self.cambioestado["CLV_MODEL"] == "DESAIRE"
        ][["Orden", "AGPLevel", "TXT_MATERIAL", "Date_Registro"]].rename(
            columns={"Date_Registro": "RegistroDesaire"}
        )

    def merge_dataframes(self):
        self.df_merged = pd.merge(
            self.df_embolsado, self.df_desaire, on="Orden", how="left"
        )
        self.df_merged.drop(columns=["TXT_MATERIAL_y", "AGPLevel_y"], inplace=True)
        self.df_merged.rename(
            columns={"AGPLevel_x": "AGPLevel", "TXT_MATERIAL_x": "Vehiculo"},
            inplace=True,
        )

    def filtrar_merged(self):
        self.df_merged = self.df_merged[
            (self.df_merged["RegistroDesaire"].notnull())
            & (self.df_merged["RegistroDesaire"] > self.df_merged["RegistroEmbolsa"])
        ]

    def calcular_tiempo_desaireacion(self):
        self.df_merged["TiemposDesaireacion"] = (
            (
                self.df_merged["RegistroDesaire"] - self.df_merged["RegistroEmbolsa"]
            ).dt.total_seconds()
            / 60
        ) + 5

    def determinar_criterio(self):
        self.df_merged["Criterio"] = self.df_merged.apply(
            lambda row: (
                0
                if (row["AGPLevel"] > "04" and row["TiemposDesaireacion"] < 120)
                or (
                    row["Vehiculo"].startswith("UROVERSA")
                    and row["TiemposDesaireacion"] < 240
                )
                else 1
            ),
            axis=1,
        )

    def tratamiento_datos(self):
        self.añadir_columna_datetime()
        self.crear_dataframe_embolsado()
        self.crear_dataframe_desaire()
        self.merge_dataframes()
        self.filtrar_merged()
        self.calcular_tiempo_desaireacion()
        self.determinar_criterio()
        # print(self.df_merged[self.df_merged["Criterio"]==0]) #Confirmación
        return self.df_merged
