#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import os
import requests
import hashlib
from datetime import datetime

url = 'https://dadesobertes.gva.es/dataset/a8a4b590-772d-4cba-a15c-fe6eff346431/resource/4e454fb5-1ba1-4ccd-8191-cc9b3700e47b/download/certificacion-energetica-de-edificios-en-valencia.csv'
folder_path = '/home/gti/PracticasNicoVRAIN/Datos/RegistrosEnergeticos'

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

def get_file_hash(file_path):
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash
    except FileNotFoundError:
        return None

response = requests.get(url)

if response.status_code == 200:
    new_file_hash = hashlib.md5(response.content).hexdigest()
    
    # Buscar en todos los ficheros existentes si alguno tiene el mismo hash
    existing_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    file_exists_same = False
    for existing_file in existing_files:
        existing_file_path = os.path.join(folder_path, existing_file)
        if get_file_hash(existing_file_path) == new_file_hash:
            file_exists_same = True
            break

    if file_exists_same:
        print("El fichero descargado es igual a uno existente. No se descarga un nuevo fichero.")
    else:
        current_date = datetime.now().strftime('%d-%m-%Y')
        file_name = f'registros_energeticos_{current_date}.csv'
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"El archivo ha sido guardado como {file_name}.")
else:
    print(f"Error al descargar el archivo: {response.status_code}")