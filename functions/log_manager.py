from pymongo import MongoClient, collection, database, DESCENDING
import logging  # Modulo estandar para registrar eventos en un archivo o consola.
from datetime import datetime  # Capturar marcas de tiempo en los errores.
from functools import wraps  # Funciones decoradas

#MongoConnector es una clase que permite la conexión a servidor de NoSQL para consultar y/o
#Insertar docuemntos para el almacenamiento de log_errors.

class MongoConnector:
    def __init__(self, credentials: dict):
        self.client = MongoClient(credentials["HOST"])
        self.db = self.get_database(credentials["DATABASE"])
        self.coll = self.get_collection(credentials["COLLECTION"])

    def get_database(self, db_name: str):
        return self.client[db_name]

    def get_collection(self, collection_name: str, db: database = None):
        if db is None:
            db = self.db
        return db[collection_name]

    def get_document(self, doc_filter: dict, collection: collection = None):
        if collection is None:
            collection = self.coll
        return collection.find_one(doc_filter)

    def insert_single_document(self, post: dict, collection: collection = None):
        if collection is None:
            collection = self.coll
        try:
            collection.insert_one(post)
            return True
        except Exception as e:
            logging.error(
                f"Se ha detectado el siguiente problema en MongoDB: {e}", exc_info=True
            )
            return False

    def update_document(
        self, doc_filter: dict, update: dict, collection: collection = None
    ):
        """Actualiza, a partir de un diccionario de valores, un documento en la colección especificada, con los filtros ingresados como parámetros

        Args:
            collection (collection): Colección de MongoDB y objeto de PyMongo
            doc_filter (dict): Filtros de la colección. Tienen que entregarse como un diccionario. Ej: {'color':'amarillo', 'edad': 25}
            update (dict): Valores a modificar en la colección. Se entregan como un diccionario. Ej: {'color': 'azul', 'edad': 27}

        """
        if not collection:
            collection = self.coll
        try:
            collection.update_one(doc_filter, {"$set": update})
            return True
        except Exception as e:
            logging.error(
                f"Se ha detectado el siguiente problema en MongoDB: {e}", exc_info=True
            )
            return False

    def get_last_document(self, doc_filter: dict, collection: collection = None):
        if not collection:
            collection = self.coll
        return collection.find_one(doc_filter, sort=[("_id", DESCENDING)])
    

# LogManager es una clase diseñada para capturar y registrar errores de manera estructurada.
# Proporciona un decorador (@log_errors) que permite agregar trazabilidad de errores a métodos o funciones.

class LogManager:

    def __init__(self, log_file='error.log'):
        logging.basicConfig(
            filename=log_file,
            level=logging.ERROR,
            format="%(asctime)s [%(levelname)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger(__name__)

    def log_errors(self, func):
        #Decorador para registrar errores de una función o método.
        #Args:
            #func (callable): La función que será decorada.
        #Returns:
            #callable: Función decorada que incluye manejo de errores.

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Obtener la clase y método que produjo el error
                class_name = args[0].__class__.__name__ if args else 'Global'
                method_name = func.__name__
                error_message = str(e)

                # Formatear el mensaje de error
                log_message = f"Class: {class_name}, Method: {method_name}, Error: {error_message}"

                # Registrar el error en el archivo
                self.logger.error(log_message)

                raise  # Re-lanzar la excepción para no interrumpir el flujo de la aplicación
        return wrapper
    



