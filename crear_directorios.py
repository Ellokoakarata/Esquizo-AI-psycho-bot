import os

def crear_init_files():
    # Definir los directorios donde queremos crear __init__.py
    directorios = ['handlers', 'utils']

    # Obtener el directorio actual
    directorio_actual = os.path.dirname(os.path.abspath(__file__))

    # Crear archivos __init__.py
    for directorio in directorios:
        ruta_directorio = os.path.join(directorio_actual, directorio)
        ruta_init = os.path.join(ruta_directorio, '__init__.py')
        
        if not os.path.exists(ruta_init):
            with open(ruta_init, 'w') as f:
                pass  # Crear archivo vacío
            print(f"Creado archivo: {ruta_init}")
        else:
            print(f"El archivo {ruta_init} ya existe.")

    print("Archivos __init__.py creados con éxito.")

if __name__ == "__main__":
    crear_init_files()
