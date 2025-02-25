from functions.consulta_desaire_pwapp import BdPowerApp
from functions.log_manager import LogManager
import pandas as pd
import win32com.client  # Para acceder a SAP y ejecuta el script
import psutil  # Para verificar apps abiertas
import os
import time

# Esta clase se encarga de realizar la lectura de la base de datos transicional resultante de
# la powerapp de desaireación, para luego ejecutar de manera automática todas las notificaciones
# de las ordenes para el puesto de trabajo 15EMBOL KeyModel DESAIRE.

log_manager = LogManager()

class auto_sap:

    def __init__(self):
        self.self_papp = BdPowerApp()
        self.df_sin_cargar = pd.DataFrame(
            BdPowerApp.piezas_sin_cargar(self.self_papp)
        )
        if self.df_sin_cargar.empty:
            raise ValueError(
                "No hay piezas sin cargar en SAP."
            )  #Excepción para detener la ejecución

    @log_manager.log_errors(sector = 'Notificaciones Automáticas SAP')
    def sap_app_verification(self):
        for process in psutil.process_iter(["name"]):
            if (
                process.info["name"]
                and "saplogon.exe".lower() in process.info["name"].lower()
            ):
                return True
        return False

    @log_manager.log_errors(sector = 'Notificaciones Automáticas SAP')
    def sap_connection_login(self):
        SapGuiAuto = win32com.client.GetObject("SAPGUI")
        application = SapGuiAuto.GetScriptingEngine
        connection = application.OpenConnection("AGP ERP PRD O2", True)
        self.session = connection.Children(0)
        return self.session
        # Esta función retorna un objeto que da acceso de todas las ventanas abiertas de sap al script para iniciar sesion

    @log_manager.log_errors(sector = 'Notificaciones Automáticas SAP')
    def start_sap(self):
        if self.sap_app_verification():
            print("sap ya iniciado")
            self.sap_connection_login()
            self.session.findById("wnd[0]").maximize()
            self.session.findById("wnd[0]/usr/txtRSYST-BNAME").text = "DBARENO"
            self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = "Dibar461*"
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
            self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = "Dibar461*"
            self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").setFocus()
            self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").caretPosition = 8
            self.session.findById("wnd[0]").sendVKey(0)

    @log_manager.log_errors(sector = 'Notificaciones Automáticas SAP')
    def sap_connection(self):
        SapGuiAuto = win32com.client.GetObject("SAPGUI")
        application = SapGuiAuto.GetScriptingEngine
        connection = application.Children(0)
        self.session = connection.Children(0)
        return self.session
        # Esta función retorna un objeto que da acceso de todas las ventanas abiertas de sap al script luego de iniciar sesion

    @log_manager.log_errors(sector = 'Notificaciones Automáticas SAP')
    def seleccionar_trx(self):
        self.session.findById("wnd[0]").maximize()
        self.session.findById("wnd[0]/tbar[0]/okcd").text = (
            "ZPPP0002"  # llena el campo de la transacción
        )
        self.session.findById(
            "wnd[0]/tbar[0]/btn[0]"
        ).press()  # Presiona ejecutar (se puede oprimir enter tambien)

    @log_manager.log_errors(sector = 'Notificaciones Automáticas SAP')
    def seleccion_pto_trabajo(self, id_operario):
        self.session.findById("wnd[0]/usr/ctxtP_WERKS").text = "CO01"
        self.session.findById("wnd[0]/usr/ctxtP_ARBPL").text = "15EMBOL"
        self.session.findById("wnd[0]/usr/ctxtP_PERNR").text = (
            f"{id_operario}"  # Variable para id por operario
        )
        self.session.findById("wnd[0]/usr/ctxtP_PERNR").setFocus()
        self.session.findById("wnd[0]/usr/ctxtP_PERNR").caretPosition = 8
        self.session.findById(
            "wnd[0]/tbar[1]/btn[8]"
        ).press()  # Primer click a ejecutar
        self.session.findById(
            "wnd[0]/tbar[1]/btn[8]"
        ).press()  # Segundo click a ejecutar, da ingreso a nueva ventana

    @log_manager.log_errors(sector = 'Notificaciones Automáticas SAP')
    def crear_notificacion_pieza_desaire(self, pieza):
        self.session.findById(
            "wnd[0]/tbar[1]/btn[5]"
        ).press()  # Click agregar registros
        self.session.findById("wnd[1]/usr/ctxtZPPE_NOTIF_ADDREG-AUFNR").text = (
            f"{pieza}"
        )
        self.session.findById("wnd[1]/usr/txtZPPE_NOTIF_ADDREG-VORNR").text = "3100"
        self.session.findById("wnd[1]/usr/txtZPPE_NOTIF_ADDREG-VORNR").setFocus()
        self.session.findById("wnd[1]/usr/txtZPPE_NOTIF_ADDREG-VORNR").caretPosition = 4
        self.session.findById(
            "wnd[1]/tbar[0]/btn[0]"
        ).press()  # Da click a confimar enviar registro
        self.session.findById("wnd[0]").sendVKey(0)  # Presiona enter

    @log_manager.log_errors(sector = 'Notificaciones Automáticas SAP')
    def guardar_notificaciones(self):
        self.session.findById("wnd[0]/tbar[0]/btn[11]").press()  # Clickea guardar
        self.session.findById(
            "wnd[1]/usr/btnBUTTON_1"
        ).press()  # Confirma click guardar
        self.session.findById(
            "wnd[1]/tbar[0]/btn[0]"
        ).press()  # Click a confirmar log de ejecución
        self.session.findById(
            "wnd[0]/tbar[0]/btn[15]"
        ).press()  # Click a flecha arriba amarilla regresar
        self.session.findById(
            "wnd[0]/tbar[0]/btn[15]"
        ).press()  # Click a flecha arriba amarilla para salir de trx

    @log_manager.log_errors(sector = 'Notificaciones Automáticas SAP')
    def salir_sistema(self):
        self.session.findById("wnd[0]/mbar/menu[4]/menu[11]").select()
        self.session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()

    def ejecutar(self):
        self.start_sap()
        self.sap_connection()
        for id_operario in self.df_sin_cargar[
            "Id_operario"
        ].unique():  # agrupar las ordenes por operario y cargarlas juntas
            self.seleccionar_trx()
            self.seleccion_pto_trabajo(id_operario)
            piezas = self.df_sin_cargar[
                self.df_sin_cargar["Id_operario"] == id_operario
            ]
            primary_keys = piezas["id"].tolist()
            for _, pieza in piezas.iterrows():
                self.crear_notificacion_pieza_desaire(pieza=pieza["Orden"])
            self.guardar_notificaciones()
            BdPowerApp().modificar_estado_cargue_sap(
                primary_keys
            )  # actualiza bd para confirmar cargue SAP
        self.salir_sistema()
