import sys
from functions.consulta_ACV import Acv
from functions.estado_desaire import EstadoPiezas, AlarmaDesaireacion
from functions.verificar_historico_embolsado import Cumplimiento_registro_embolsados

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
        AlarmaDesaireacion.filtrar_no_conformidades(self)
    
    elif opcion == 'DobleRegistro':

        self = Cumplimiento_registro_embolsados()
        validas, invalidas = Cumplimiento_registro_embolsados.ejecutar_revision(self)
        invalidas.to_excel('invalidas.xlsx', index= False)
        validas.to_excel('validas.xlsx', indes= False)


    else:
        print("Opción no válida.")
    

        
if __name__ == "__main__":
    opcion = sys.argv[1]
    main(opcion)