import logging  # Modulo estandar para registrar eventos en un archivo o consola.
from datetime import datetime  # Capturar marcas de tiempo en los errores.
from functools import wraps  # Funciones decoradas


# LogManager es una clase diseñada para capturar y registrar errores de manera estructurada.
# Proporciona un decorador (@log_errors) que permite agregar trazabilidad de errores a métodos o funciones.


class LogManager:
    def __init__(self, log_file="error_log.txt"):
        self.logger = logging.getLogger(
            __name__
        )  # Obtiene un logger con el nombre del modulo actual.
        if (
            not self.logger.hasHandlers()
        ):  #Evita agregar múltiples manejadores al logger si ya están configurados.
            handler = logging.FileHandler(
                log_file
            )  #Define un manejador para escribir en el archivo especificado.
            #Formato de los mensajes en el archivo: incluye marca de tiempo, nivel de error y mensaje.
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)  #Aplica el formato al manejador.
            self.logger.addHandler(handler)  #Asocia el manejador con el logger.
            self.logger.setLevel(
                logging.ERROR
            )  #Configura el nivel mínimo de eventos a registrar (solo errores).

    def log_errors(self, func):
        #Decorador para registrar errores en una función o método.
        #Args:
            #func (callable): La función que será decorada.
        #Returns:
            #callable: Función decorada que incluye manejo de errores.

        @wraps(
            func
        )  #Preserva metadatos como __name__ y __doc__ de la función original.
        def wrapper(*args, **kwargs):
            try:
                return func(
                    *args, **kwargs
                )  #Llama a la función original con los mismos argumentos.
            except (
                Exception
            ) as e:  #Captura cualquier excepción que ocurra dentro de la función.
                #Obtiene el nombre de la clase si la función pertenece a un método de clase.
                class_name = args[0].__class__.__name__ if args else None
                #Registra información relevante del error, como la clase, método y mensaje.
                error_data = {
                    "class": class_name,
                    "method": func.__name__,
                    "error_message": str(
                        e
                    ),  #Convierte la excepción en una cadena legible.
                    "timestamp": datetime.now().isoformat(),  #Marca de tiempo del error.
                }
                self.logger.error(error_data)  # Escribe el error en el archivo de log.
                raise  #Re-lanza la excepción para no interrumpir el flujo de la aplicación.

        return wrapper
