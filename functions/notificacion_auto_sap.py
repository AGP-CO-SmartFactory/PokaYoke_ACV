import pandas as pd
import win32com.client #Para acceder a SAP y ejecuta el script
from datetime import datetime
import subprocess
import os

#Esta clase se encarga de realizar la lectura de la base de datos transicional resultante de
#la powerapp de desaireación, para luego ejecutar de manera automática todas las notificaciones
#automaticas de las ordenes para el puesto de trabajo 15EMBOL KeyModel DESAIRE.

class auto_sap():

    def start_sap(self, sap_user, sap_psw):
        os.startfile(r'C:\Program Files (x86)\SAP\FrontEnd\SapGui\saplogon.exe') #Buscar ruta SAP pc destino

    def sap_connection(self):
        SapGuiAuto = win32com.client.GetObject('SAPGUI')
        application = SapGuiAuto.GetScriptingEngine
        connection = application.Children(0)
        session = connection.Children(0)
        return session
        #Esta función retorna un objeto que da acceso de todas las ventanas abiertas de sap al script
        

    def ejecutar(self):
        self.start_sap(sap_user = 'DBARENO', sap_psw = 'Dibar461....')
