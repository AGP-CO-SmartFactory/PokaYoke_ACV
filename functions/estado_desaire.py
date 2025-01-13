from functions.sql_utilities import SqlUtilities
from functions.log_manager import LogManager
import pandas as pd
import warnings

warnings.filterwarnings('ignore')
# Esta clase se encarga de entregar un estado OK (1) o NO OK (0) para los tiempos de desaireación de las piezas en embolsado

log_manager = LogManager()

class EstadoPiezas:

    def __init__(self):
        query_cambioestado = """SELECT CAST(Orden AS INT) AS Orden, AGPLevel, TXT_MATERIAL, DATE_NOTIF, HRA_NOTIF, CLV_MODEL, DESC_CLIENTE, FormulaCOD 
        FROM 
            VW_CAMBIOESTADO WITH(NOLOCK)
        WHERE 
            DATE_NOTIF > DATEADD(day,-7, CAST(GETDATE() AS date))
            AND (CLV_MODEL = 'EMBOLSA')
            AND ANULADO <> 'X'
            AND CTD_BUENA <> '1.000-'
        """
        query_calendario = """SELECT CAST(Orden AS INT) AS Orden, NivelAGP, Vehiculo, FechaRegistro, ClienteDespacho, Formula
        FROM 
            TCAL_CALENDARIO_COLOMBIA_DIRECT
        WHERE 
            KeyModel = 'DESAIRE'
            AND Vehiculo NOT LIKE '%PROBETAS%' """
        query_retrabajos = """SELECT CAST(Orden AS INT) AS Orden
        FROM 
            VW_CAMBIOESTADO WITH(NOLOCK)
        WHERE 
            DATE_NOTIF > DATEADD(day,-30, CAST(GETDATE() AS date))
            AND DEFECTO LIKE '%Resistencia fuera de tolerancia%'
            AND TIPO_NOTIF <> 'RECHAZO' """
        self.cambioestado = SqlUtilities.get_database_com(query_cambioestado)
        self.calendario = SqlUtilities.get_database_cal(query_calendario)
        self.retrabajos = SqlUtilities.get_database_com(query_retrabajos)

    def filtrar_piezas_cambioestado(self): #esto con el fin de solo obtener las piezas que estén en el puesto de trabajo
        self.piezas_desaireadas = self.calendario[self.calendario['Orden'].isin(self.cambioestado['Orden'])]

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
        self.df_desaire = self.calendario[["Orden", "NivelAGP", "Vehiculo", "FechaRegistro", 'ClienteDespacho', 'Formula']].rename(
            columns={"FechaRegistro": "RegistroDesaire", "ClienteDespacho" : "Cliente"}
        )


    def merge_dataframes(self):
        self.df_merged = pd.merge(
            self.df_embolsado, self.df_desaire, on="Orden", how="left"
        )
        self.df_merged.drop(columns=["TXT_MATERIAL", "DESC_CLIENTE"], inplace=True)
        self.df_merged.rename(
            columns={"NivelAGP_x": "AGPLevel", "Vehiculo_x": "Vehiculo", "FormulaCOD":"Formula"},
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

    def determinar_criterio(self):
        ordenes_retrabajos = set(self.retrabajos['Orden'])
        self.df_merged["Criterio"] = self.df_merged.apply(
            lambda row: (
                1 
                if row["Orden"] in ordenes_retrabajos
                else 0
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
                    str(row["Formula"]).startswith("LL")
                    and row["TiemposDesaireacion"] < 120
                )
                else 1
            ),
            axis=1,
        )

    def traer_tiempos_a_calendario(self):
        self.piezas_desaireadas = self.piezas_desaireadas.merge(self.df_merged, on = 'Orden', how='left')
        self.piezas_desaireadas = self.piezas_desaireadas.drop_duplicates(subset = ['Orden'], inplace=False)
        self.piezas_desaireadas = self.piezas_desaireadas.fillna({
            'Orden': 'NULL',
            'AGPLevel': '00',
            'Vehiculo': 'No Encontrado',
            'Cliente' : 'No Encontrado',
            'Formula' : 'No Encontrado',
            'TiemposDesaireacion': 999, 
            'Criterio': 1
        })
        self.piezas_desaireadas['Criterio'] = self.piezas_desaireadas['Criterio'].astype(int)

    def limpiar_duplicados_tabla(self):
        self.piezas_desaireadas.drop(columns=["NivelAGP_x", "FechaRegistro", "ClienteDespacho", "Formula_y", "NivelAGP_y", "Vehiculo_y"], inplace=True)
        self.piezas_desaireadas.rename(
            columns={"Vehiculo_x": "Vehiculo", "Formula_x":"Formula"},
            inplace=True,
        )

    def eliminar_piezas_nivel_0(self):
        self.piezas_desaireadas = self.piezas_desaireadas[self.piezas_desaireadas["NivelAGP"] != 0]

    @log_manager.log_errors(sector = 'Estado desaireación')
    def tratamiento_datos(self):

        self.filtrar_piezas_cambioestado()
        self.añadir_columna_datetime()
        self.crear_dataframe_embolsado()
        self.crear_dataframe_desaire()
        self.merge_dataframes()
        self.filtrar_merged()
        self.limpiar_agp_level()
        self.calcular_tiempo_desaireacion()
        self.determinar_criterio()
        self.traer_tiempos_a_calendario()
        self.limpiar_duplicados_tabla()
        self.eliminar_piezas_nivel_0()
        return self.piezas_desaireadas
    
    @log_manager.log_errors(sector = 'Estado desaireación_BD_temporal')
    def cargar_datos_sql(self):
        truncatequery = "TRUNCATE TABLE SF_DesaireacionPiezas"
        SqlUtilities.insert_database_sf(truncatequery)

        for _, row in self.piezas_desaireadas.iterrows():
            query =  f"""
            INSERT INTO SF_DesaireacionPiezas (Orden, NivelAGP, Vehiculo, TiemposDesaireacion, Criterio)
            VALUES ({row['Orden']}, {row['AGPLevel']}, '{row['Vehiculo']}', {row['TiemposDesaireacion']}, '{row['Criterio']}')
            """
            SqlUtilities.insert_database_sf(query)


class AlarmaDesaireacion():

    @log_manager.log_errors(sector = 'Alarma desaireación')
    def __init__(self):
        query = "SELECT * FROM SF_DesaireacionPiezas"
        self.base_registros_desaireacion = SqlUtilities.get_database_sf(query)
    
    @log_manager.log_errors(sector = 'Alarma desaireación')
    def filtrar_no_conformidades(self):
        no_conformidades = self.base_registros_desaireacion[self.base_registros_desaireacion["Criterio"] == 0]     
        return no_conformidades
    

