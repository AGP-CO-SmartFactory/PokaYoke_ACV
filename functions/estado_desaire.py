from functions.sql_utilities import SqlUtilities
from functions.log_manager import LogManager
import pandas as pd
import warnings

warnings.filterwarnings("ignore")
# Esta clase se encarga de entregar un estado OK (1) o NO OK (0) para los tiempos de desaireación de las piezas en embolsado

log_manager = LogManager()


class EstadoPiezas:

    @log_manager.log_errors(sector="Notificaciones Automáticas SAP")
    def __init__(self):
        query_cambioestado = """SELECT CAST(Orden AS INT) AS Orden, AGPLevel, TXT_MATERIAL, DATE_NOTIF, HRA_NOTIF, CLV_MODEL, DESC_CLIENTE, FormulaCOD 
        FROM 
            VW_CAMBIOESTADO WITH(NOLOCK)
        WHERE 
            DATE_NOTIF > DATEADD(day,-2, CAST(GETDATE() AS date))
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
            AND (DEFECTO = 'Resistencia fuera de tolerancia' OR DEFECTO = 'Borde paquete no uniforme' OR DEFECTO = 'MALLA F.T' OR DEFECTO = 'Burbujas En Paquete' OR DEFECTO = 'Burbuja' OR DEFECTO = 'PC Expuesto')
            AND TIPO_NOTIF <> 'RECHAZO' """
        self.cambioestado = SqlUtilities.get_database_com(query_cambioestado)
        self.calendario = SqlUtilities.get_database_cal(query_calendario)
        self.retrabajos = SqlUtilities.get_database_com(query_retrabajos)

    @log_manager.log_errors(sector="Estado desaireación")
    def filtrar_piezas_cambioestado(
        self,
    ):  # esto con el fin de solo obtener las piezas que estén en el puesto de trabajo
        self.piezas_desaireadas = self.calendario[
            self.calendario["Orden"].isin(self.cambioestado["Orden"])
        ]

    @log_manager.log_errors(sector="Estado desaireación")
    def añadir_columna_datetime(self):
        self.cambioestado["Date_Registro"] = pd.to_datetime(
            self.cambioestado["DATE_NOTIF"] + " " + self.cambioestado["HRA_NOTIF"]
        )

    @log_manager.log_errors(sector="Estado desaireación")
    def crear_dataframe_embolsado(self):
        self.df_embolsado = self.cambioestado[
            self.cambioestado["CLV_MODEL"] == "EMBOLSA"
        ][
            [
                "Orden",
                "AGPLevel",
                "TXT_MATERIAL",
                "Date_Registro",
                "DESC_CLIENTE",
                "FormulaCOD",
            ]
        ].rename(
            columns={"Date_Registro": "RegistroEmbolsa"}
        )

    @log_manager.log_errors(sector="Estado desaireación")
    def crear_dataframe_desaire(self):
        self.df_desaire = self.calendario[
            [
                "Orden",
                "NivelAGP",
                "Vehiculo",
                "FechaRegistro",
                "ClienteDespacho",
                "Formula",
            ]
        ].rename(
            columns={"FechaRegistro": "RegistroDesaire", "ClienteDespacho": "Cliente"}
        )

    @log_manager.log_errors(sector="Estado desaireación")
    def merge_dataframes(self):
        self.df_merged = pd.merge(
            self.df_embolsado, self.df_desaire, on="Orden", how="left"
        )
        self.df_merged.drop(columns=["TXT_MATERIAL", "DESC_CLIENTE"], inplace=True)
        self.df_merged.rename(
            columns={
                "NivelAGP_x": "AGPLevel",
                "Vehiculo_x": "Vehiculo",
                "FormulaCOD": "Formula",
            },
            inplace=True,
        )

    @log_manager.log_errors(sector="Estado desaireación")
    def filtrar_merged(self):
        self.df_merged = self.df_merged[
            (self.df_merged["RegistroDesaire"].notnull())
            & (self.df_merged["RegistroDesaire"] > self.df_merged["RegistroEmbolsa"])
        ]

    @log_manager.log_errors(sector="Estado desaireación")
    def limpiar_agp_level(self):
        self.df_merged["AGPLevel"] = self.df_merged["AGPLevel"].replace("NA", None)
        self.df_merged = self.df_merged.dropna(subset=["AGPLevel"])

    @log_manager.log_errors(sector="Estado desaireación")
    def calcular_tiempo_desaireacion(self):
        self.df_merged["TiemposDesaireacion"] = (
            (
                self.df_merged["RegistroDesaire"] - self.df_merged["RegistroEmbolsa"]
            ).dt.total_seconds()
            / 60
        ) + 5

    @log_manager.log_errors(sector="Estado desaireación")
    def determinar_criterio(self):
        ordenes_retrabajos = set(self.retrabajos["Orden"])

        def criterio(row):
            if row["Orden"] in ordenes_retrabajos:
                return 1
            elif (
                (row["AGPLevel"] > "04" and row["TiemposDesaireacion"] < 120)
                or (
                    row["Cliente"].startswith("URO")
                    and row["TiemposDesaireacion"] < 240
                )
                or (
                    row["Cliente"].startswith("BENTELER")
                    and row["TiemposDesaireacion"] < 120
                )
                or (
                    (str(row["Formula"]).startswith("LL") or str(row["Formula"]).startswith("NP"))
                    and row["TiemposDesaireacion"] < 120
                )
            ):
                return 0
            else:
                return 1

        self.df_merged["Criterio"] = self.df_merged.apply(criterio, axis=1)

    @log_manager.log_errors(sector="Estado desaireación")
    def traer_tiempos_a_calendario(self):
        self.piezas_desaireadas = self.piezas_desaireadas.merge(
            self.df_merged, on="Orden", how="left"
        )
        self.piezas_desaireadas = self.piezas_desaireadas.drop_duplicates(
            subset=["Orden"], inplace=False
        )
        self.piezas_desaireadas = self.piezas_desaireadas.fillna(
            {
                "Orden": "NULL",
                "AGPLevel": "00",
                "Vehiculo": "No Encontrado",
                "Cliente": "No Encontrado",
                "Formula": "No Encontrado",
                "TiemposDesaireacion": 999,
                "Criterio": 1,
            }
        )
        self.piezas_desaireadas["Criterio"] = self.piezas_desaireadas[
            "Criterio"
        ].astype(int)

    @log_manager.log_errors(sector="Estado desaireación")
    def limpiar_duplicados_tabla(self):
        self.piezas_desaireadas.drop(
            columns=[
                "NivelAGP_x",
                "FechaRegistro",
                "ClienteDespacho",
                "Formula_y",
                "NivelAGP_y",
                "Vehiculo_y",
            ],
            inplace=True,
        )
        self.piezas_desaireadas.rename(
            columns={"Vehiculo_x": "Vehiculo", "Formula_x": "Formula"},
            inplace=True,
        )

    @log_manager.log_errors(sector="Estado desaireación")
    def identificar_registros_laminados(self):
        self.laminados = self.cambioestado.groupby('Orden').size().reset_index(name='Conteo') #Realiza un mapeo de los ultimos registros de embolsado durante dos días
        self.laminados = self.laminados[self.laminados['Conteo']>1]



    @log_manager.log_errors(sector="Estado desaireación")
    def eliminar_piezas_criterios_especificos(self):
        self.piezas_desaireadas = self.piezas_desaireadas[
            self.piezas_desaireadas["AGPLevel"] != 0
        ]
        self.piezas_desaireadas = self.piezas_desaireadas[
            ~self.piezas_desaireadas["Vehiculo"].str.contains("BMW X5 4D UTILITY")
        ]
        self.piezas_desaireadas = self.piezas_desaireadas[
            ~self.piezas_desaireadas['Orden'].isin(self.laminados['Orden'])
            ]

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
        self.identificar_registros_laminados()
        self.eliminar_piezas_criterios_especificos()
        return self.piezas_desaireadas

    @log_manager.log_errors(sector="Estado desaireación_BD_temporal")
    def cargar_datos_sql(self):
        truncatequery = "TRUNCATE TABLE SF_DesaireacionPiezas"
        SqlUtilities.insert_database_sf(truncatequery)

        for _, row in self.piezas_desaireadas.iterrows():
            query = f"""
            INSERT INTO SF_DesaireacionPiezas (Orden, NivelAGP, Vehiculo, TiemposDesaireacion, Criterio)
            VALUES ({row['Orden']}, {row['AGPLevel']}, '{row['Vehiculo']}', {row['TiemposDesaireacion']}, '{row['Criterio']}')
            """
            SqlUtilities.insert_database_sf(query)

#Esta clase se encarga de retorna un DF dónde el criterio de piezas en desaireación sea 0
class AlarmaDesaireacion:

    @log_manager.log_errors(sector="Alarma desaireación")
    def __init__(self):
        query = "SELECT * FROM SF_DesaireacionPiezas"
        self.base_registros_desaireacion = SqlUtilities.get_database_sf(query)

    @log_manager.log_errors(sector="Alarma desaireación")
    def filtrar_no_conformidades(self):
        no_conformidades = self.base_registros_desaireacion[
            self.base_registros_desaireacion["Criterio"] == 0
        ]
        return no_conformidades
