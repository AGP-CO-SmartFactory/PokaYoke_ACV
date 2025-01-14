from functions.sql_utilities import SqlUtilities
from functions.log_manager import LogManager
import pandas as pd
import warnings 


warnings.filterwarnings('ignore')


#Este código existe con la función de poder verificar por días que las ordenes tengan
#tanto registro de embolsado como registro de desaireación, esto debido a que se presentaron
#no conformidades en el proceso que dañaban la lógica para el bloqueo de autoclaves

log_manager = LogManager()

class Cumplimiento_registro_embolsados:

    @log_manager.log_errors(sector = 'Verificar registros embolsa/desaire')
    def __init__(self):
        query_historico = """
                    SELECT 
                        CE.ORDEN, 
                        CE.PTO_TRABAJO, 
                        CE.CLV_MODEL, 
                        CE.DATE_NOTIF,
                        CE.HRA_NOTIF
                    FROM 
                        [Comercial].[dbo].[VW_CAMBIOESTADO] AS CE WITH (NOLOCK)
                    WHERE 
                        CE.DATE_NOTIF = '20241213'
                        AND CE.PTO_TRABAJO = '15EMBOL'
                        AND CE.TIPO_NOTIF = 'APROBADO'
                 """
        self.historico_embolsado = SqlUtilities.get_database_com(query_historico)

    @log_manager.log_errors(sector = 'Verificar registros embolsa/desaire')
    def filtrar_keymodel(self):
        self.filtro_embolsa = self.historico_embolsado[self.historico_embolsado['CLV_MODEL'] == 'EMBOLSA']
        self.filtro_desaire = self.historico_embolsado[self.historico_embolsado['CLV_MODEL'] == 'DESAIRE']

    @log_manager.log_errors(sector = 'Verificar registros embolsa/desaire')
    def criterio_registro_completo(self):
        self.ordenes_embolsa = set(self.filtro_embolsa['ORDEN'])
        self.ordenes_desaire = set(self.filtro_desaire['ORDEN'])
        self.ordenes_validas = self.ordenes_embolsa & self.ordenes_desaire

    @log_manager.log_errors(sector = 'Verificar registros embolsa/desaire')
    def crear_df_ordenes_resultados(self):
        self.df_ordenes_validas = self.historico_embolsado[self.historico_embolsado['ORDEN'].isin(self.ordenes_validas)]
        self.df_ordenes_invalidas = self.historico_embolsado[~self.historico_embolsado['ORDEN'].isin(self.ordenes_validas)]
        
    def ejecutar_revision(self):
        self.filtrar_keymodel()
        self.criterio_registro_completo()
        self.crear_df_ordenes_resultados()
        return self.df_ordenes_validas, self.df_ordenes_invalidas


