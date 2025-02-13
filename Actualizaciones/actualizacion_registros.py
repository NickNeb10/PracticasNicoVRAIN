#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import os
import requests
import hashlib
from datetime import datetime

url = 'https://dadesobertes.gva.es/dataset/a8a4b590-772d-4cba-a15c-fe6eff346431/resource/4e454fb5-1ba1-4ccd-8191-cc9b3700e47b/download/certificacion-energetica-de-edificios-en-valencia.csv'
folder_path = '/home/nnebot/PracticasNicoVRAIN/Datos/RegistrosEnergeticos'

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
    current_date = datetime.now().strftime('%d-%m-%Y')
    file_name = f'registros_energeticos_{current_date}.csv'
    file_path = os.path.join(folder_path, file_name)
    
    new_file_hash = hashlib.md5(response.content).hexdigest()
    existing_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    if file_name not in existing_files:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"El archivo ha sido guardado como {file_name}.")
    else:
        print(f"El archivo {file_name} ya existe.")
else:
    print(f"Error al descargar el archivo: {response.status_code}")
