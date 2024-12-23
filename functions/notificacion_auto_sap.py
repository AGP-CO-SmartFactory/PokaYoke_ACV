import pandas as pd
import win32com.client #Para acceder a SAP y ejecuta el script
import psutil #Para verificar apps abiertas
#from datetime import datetime
#import subprocess
import os
import time

#Esta clase se encarga de realizar la lectura de la base de datos transicional resultante de
#la powerapp de desaireación, para luego ejecutar de manera automática todas las notificaciones
#automaticas de las ordenes para el puesto de trabajo 15EMBOL KeyModel DESAIRE.

class auto_sap():
    
    def sap_app_verification(self):
        for process in psutil.process_iter(['name']):
            if process.info['name'] and 'saplogon.exe'.lower() in process.info['name'].lower():
                return True
        return False
    
    def start_sap(self):
        if self.sap_app_verification():
            os.startfile(r'C:\Program Files (x86)\SAP\FrontEnd\SapGui\saplogon.exe') #Buscar ruta SAP pc destino
        else:
            os.startfile(r'C:\Program Files (x86)\SAP\FrontEnd\SapGui\saplogon.exe') #Buscar ruta SAP pc destino
            time.sleep(10)

    def sap_connection(self):
        SapGuiAuto = win32com.client.GetObject('SAPGUI')
        application = SapGuiAuto.GetScriptingEngine
        connection = application.Children(0)
        self.session = connection.Children(0)
        return self.session
        #Esta función retorna un objeto que da acceso de todas las ventanas abiertas de sap al script

    def consulta_fin_turno(self):
        self.session.findById("wnd[0]").maximize()
        self.session.findById("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").selectedNode = "F00019"
        self.session.findById("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode("F00019")
        self.session.findById("wnd[0]/usr/ctxtP_WERKS-LOW").text = "CO01"
        self.session.findById("wnd[0]/usr/ctxtP_AUFNR-LOW").text = "11048497"
        self.session.findById("wnd[0]/usr/ctxtP_AUFNR-LOW").setFocus()
        self.session.findById("wnd[0]/usr/ctxtP_AUFNR-LOW").caretPosition = 8
        self.session.findById("wnd[0]/tbar[1]/btn[8]").press()
        self.session.findById("wnd[0]/tbar[0]/btn[3]").press()
        self.session.findById("wnd[0]/tbar[0]/btn[3]").press()
        self.session.findById("wnd[0]").close()
        self.session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()

    
    def ejecutar(self):
        self.start_sap()
        self.sap_connection()
        self.consulta_fin_turno()
    

