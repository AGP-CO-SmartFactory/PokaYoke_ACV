import pandas as pd
import win32com.client  # Para acceder a SAP y ejecuta el script
import psutil  # Para verificar apps abiertas

# from datetime import datetime
# import subprocess
import os
import time

# Esta clase se encarga de realizar la lectura de la base de datos transicional resultante de
# la powerapp de desaireación, para luego ejecutar de manera automática todas las notificaciones
# de las ordenes para el puesto de trabajo 15EMBOL KeyModel DESAIRE.


class auto_sap:

    def sap_app_verification(self):
        for process in psutil.process_iter(["name"]):
            if (
                process.info["name"]
                and "saplogon.exe".lower() in process.info["name"].lower()
            ):
                return True
        return False
    
    def sap_connection_login(self):
        SapGuiAuto = win32com.client.GetObject("SAPGUI")
        application = SapGuiAuto.GetScriptingEngine
        connection = application.OpenConnection("QAS 2023", True)
        self.session = connection.Children(0)
        return self.session
        # Esta función retorna un objeto que da acceso de todas las ventanas abiertas de sap al script para iniciar sesion

    def start_sap(self):
        if self.sap_app_verification():
            print("sap ya iniciado")
            self.sap_connection_login()
            self.session.findById("wnd[0]").maximize()
            self.session.findById("wnd[0]/usr/txtRSYST-BNAME").text = "DBARENO"
            self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = "Dibar461...."
            self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").setFocus()
            self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").caretPosition = 8
            self.session.findById("wnd[0]").sendVKey(0)
        else:
            os.startfile(
                r"C:\Program Files (x86)\SAP\FrontEnd\SapGui\saplogon.exe"
            )  # Buscar ruta SAP pc destino
            time.sleep(10)
            self.sap_connection_login()
            self.session.findById("wnd[0]").maximize()
            self.session.findById("wnd[0]/usr/txtRSYST-BNAME").text = "DBARENO"
            self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = "Dibar461...."
            self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").setFocus()
            self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").caretPosition = 8
            self.session.findById("wnd[0]").sendVKey(0)

    def seleccionar_trx(self):
        self.session.findById("wnd[0]").maximize()
        self.session.findById("wnd[0]/tbar[0]/okcd").text = (
            "ZPPP0002"  # llena el campo de la transacción
        )
        self.session.findById(
            "wnd[0]/tbar[0]/btn[0]"
        ).press()  # Presiona ejecutar (se puede oprimir enter tambien)

    def seleccion_pto_trabajo(self):
        self.session.findById("wnd[0]/usr/ctxtP_WERKS").text = "CO01"
        self.session.findById("wnd[0]/usr/ctxtP_ARBPL").text = "15EMBOL"
        self.session.findById("wnd[0]/usr/ctxtP_PERNR").text = (
            "108484"  # Variable para id por operario
        )
        self.session.findById("wnd[0]/usr/ctxtP_PERNR").setFocus()
        self.session.findById("wnd[0]/usr/ctxtP_PERNR").caretPosition = 8
        self.session.findById(
            "wnd[0]/tbar[1]/btn[8]"
        ).press()  # Primer click a ejecutar
        self.session.findById(
            "wnd[0]/tbar[1]/btn[8]"
        ).press()  # Segundo click a ejecutar, da ingreso a nueva ventana

    def crear_notificacion_pieza_desaire(self):
        self.session.findById(
            "wnd[0]/tbar[1]/btn[5]"
        ).press()  # Click agregar registros
        self.session.findById("wnd[1]/usr/ctxtZPPE_NOTIF_ADDREG-AUFNR").text = (
            "11018280"
        )
        self.session.findById("wnd[1]/usr/txtZPPE_NOTIF_ADDREG-VORNR").text = "3100"
        self.session.findById("wnd[1]/usr/txtZPPE_NOTIF_ADDREG-VORNR").setFocus()
        self.session.findById("wnd[1]/usr/txtZPPE_NOTIF_ADDREG-VORNR").caretPosition = 4
        self.session.findById(
            "wnd[1]/tbar[0]/btn[0]"
        ).press()  # Da click a confimar enviar registro
        self.session.findById("wnd[0]").sendVKey(0)  # Presiona enter
        self.session.findById("wnd[0]/tbar[0]/btn[11]").press()  # Clickea guardar
        self.session.findById(
            "wnd[1]/usr/btnBUTTON_1"
        ).press()  # Confirma click guardar
        self.session.findById(
            "wnd[1]/tbar[0]/btn[0]"
        ).press()  # Click a confirmar log de ejecución

    def salir_sistema(self):
        self.session.findById("wnd[0]/mbar/menu[0]/menu[11]").select()
        self.session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()

    def ejecutar(self):
        self.start_sap()
        self.sap_connection()
        self.seleccionar_trx()
        self.seleccion_pto_trabajo()
        self.crear_notificacion_pieza_desaire()
        self.salir_sistema()
