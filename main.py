import sys
from functions.consulta_ACV import Acv
from functions.estado_desaire import EstadoPiezas, AlarmaDesaireacion
from functions.verificar_historico_embolsado import Cumplimiento_registro_embolsados
from functions.send_email import SendEmail
from functions.notificacion_auto_sap import auto_sap

def main(opcion):
    if opcion == "EstadoACV":
        self=Acv()
        Acv.estado_acv(self)   

    elif opcion =="EstadoPiezas":
        self=EstadoPiezas() 
        EstadoPiezas.tratamiento_datos(self)
        EstadoPiezas.cargar_datos_sql(self)
    
    elif opcion =="NoConformidades":
        self = AlarmaDesaireacion()
        tabla_nc = AlarmaDesaireacion.filtrar_no_conformidades(self)
        if not tabla_nc.empty:
            SendEmail.mail_nc_acv(tabla_nc)
    
    elif opcion == 'DobleRegistro':
        self = Cumplimiento_registro_embolsados()
        validas, invalidas = Cumplimiento_registro_embolsados.ejecutar_revision(self)
        invalidas.to_excel('invalidas.xlsx', index= False)
        validas.to_excel('validas.xlsx', index= False)
    
    elif opcion == 'SAP':
        self = auto_sap()
        auto_sap.ejecutar(self)
        
if __name__ == "__main__":
    opcion = sys.argv[1]
    main(opcion)