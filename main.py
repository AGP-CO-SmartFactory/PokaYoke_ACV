import sys
from functions.consulta_ACV import Acv
from functions.estado_desaire import EstadoPiezas

def main(opcion):
    if opcion == "A":
        self=Acv()
        Acv.estado_acv(self)   

    elif opcion =="B":
        self=EstadoPiezas() 
        EstadoPiezas.tratamiento_datos(self)
    else:
        print("Opción no válida.")
        
if __name__ == "__main__":
    opcion = sys.argv[1]
    main(opcion)
