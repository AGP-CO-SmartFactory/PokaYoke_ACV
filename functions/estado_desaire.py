from functions.sql_utilities import SqlUtilities
import pandas as pd
import warnings 

warnings.filterwarnings('ignore')
# Esta clase se encarga de entregar un estado OK (1) o NO OK (0) para los tiempos de desaireación de las piezas en embolsado

class EstadoPiezas:

    def __init__(self):
        query_cambioestado = """SELECT Orden, AGPLevel, TXT_MATERIAL, DATE_NOTIF, HRA_NOTIF, CLV_MODEL, DESC_CLIENTE, FormulaCOD 
        FROM 
            VW_CAMBIOESTADO WITH(NOLOCK)
        WHERE 
            DATE_NOTIF > DATEADD(day,-2, CAST(GETDATE() AS date))
            AND (CLV_MODEL = 'EMBOLSA' OR CLV_MODEL = 'DESAIRE')
            AND ANULADO <> 'X'
            AND CTD_BUENA <> '1.000-'
            AND Orden NOT IN (
                SELECT Orden
                FROM VW_CAMBIOESTADO WITH(NOLOCK)
                WHERE CLV_MODEL = 'ACV'
            )
        """
        query_calendario = """SELECT Orden
        FROM 
            TCAL_CALENDARIO_COLOMBIA_DIRECT
        WHERE 
            KeyModel = 'DESAIRE'"""
        self.cambioestado = SqlUtilities.get_database_com(query_cambioestado)
        self.calendario = SqlUtilities.get_database_cal(query_calendario)
    
    def filtrar_por_calendario(self): #esto con el fin de solo obtener las piezas que estén en el puesto de trabajo
        self.cambioestado = self.cambioestado[self.cambioestado['Orden'].isin(self.calendario['Orden'])]

    def añadir_columna_datetime(self):
        self.cambioestado["Date_Registro"] = pd.to_datetime(
            self.cambioestado["DATE_NOTIF"] + " " + self.cambioestado["HRA_NOTIF"]
        )

    def crear_dataframe_embolsado(self):
        self.df_embolsado = self.cambioestado[
            self.cambioestado["CLV_MODEL"] == "EMBOLSA"
        ][["Orden", "AGPLevel", "TXT_MATERIAL", "Date_Registro", 'DESC_CLIENTE', 'FormulaCOD']].rename(
            columns={"Date_Registro": "RegistroEmbolsa"}
        )

    def crear_dataframe_desaire(self):
        self.df_desaire = self.cambioestado[
            self.cambioestado["CLV_MODEL"] == "DESAIRE"
        ][["Orden", "AGPLevel", "TXT_MATERIAL", "Date_Registro", 'DESC_CLIENTE', 'FormulaCOD']].rename(
            columns={"Date_Registro": "RegistroDesaire"}
        )

    def merge_dataframes(self):
        self.df_merged = pd.merge(
            self.df_embolsado, self.df_desaire, on="Orden", how="left"
        )
        self.df_merged.drop(columns=["TXT_MATERIAL_y", "AGPLevel_y", "DESC_CLIENTE_y", "FormulaCOD_y"], inplace=True)
        self.df_merged.rename(
            columns={"AGPLevel_x": "AGPLevel", "TXT_MATERIAL_x": "Vehiculo", "DESC_CLIENTE_x" : "Cliente", "FormulaCOD_x":"Formula"},
            inplace=True,
        )

    def filtrar_merged(self):
        self.df_merged = self.df_merged[
            (self.df_merged["RegistroDesaire"].notnull())
            & (self.df_merged["RegistroDesaire"] > self.df_merged["RegistroEmbolsa"])
        ]

    def limpiar_agp_level(self):
        self.df_merged['AGPLevel'] = self.df_merged['AGPLevel'].replace('NA', None)
        self.df_merged = self.df_merged.dropna(subset=['AGPLevel'])

    def calcular_tiempo_desaireacion(self):
        self.df_merged["TiemposDesaireacion"] = (
            (
                self.df_merged["RegistroDesaire"] - self.df_merged["RegistroEmbolsa"]
            ).dt.total_seconds()
            / 60
        ) + 5
        #print(self.df_merged)

    def determinar_criterio(self):
        self.df_merged["Criterio"] = self.df_merged.apply(
            lambda row: (
                0
                if (row["AGPLevel"] > "04" and row["TiemposDesaireacion"] < 120)
                or (
                    row["Cliente"].startswith("URO")
                    and row["TiemposDesaireacion"] < 240
                )
                or (
                    row["Cliente"].startswith("BENTELER")
                    and row["TiemposDesaireacion"] < 120
                )
                or (
                    row["Formula"].startswith("LL")
                    and row["TiemposDesaireacion"] < 120
                )
                else 1
            ),
            axis=1,
        )

    def tratamiento_datos(self):

        self.filtrar_por_calendario()
        self.añadir_columna_datetime()
        self.crear_dataframe_embolsado()
        self.crear_dataframe_desaire()
        self.merge_dataframes()
        self.filtrar_merged()
        self.limpiar_agp_level()
        self.calcular_tiempo_desaireacion()
        self.determinar_criterio()
        #print(self.df_merged[self.df_merged["Criterio"]==1]) #Confirmación
        return self.df_merged

    def cargar_datos_sql(self):

        truncatequery = "TRUNCATE TABLE SF_DesaireacionPiezas"
        SqlUtilities.insert_database_sf(truncatequery)

        for _, row in self.df_merged.iterrows():
            query =  f"""
            INSERT INTO SF_DesaireacionPiezas (Orden, NivelAGP, Vehiculo, TiemposDesaireacion, Criterio)
            VALUES ({row['Orden']}, {row['AGPLevel']}, '{row['Vehiculo']}', {row['TiemposDesaireacion']}, '{row['Criterio']}')
        """
            SqlUtilities.insert_database_sf(query)
