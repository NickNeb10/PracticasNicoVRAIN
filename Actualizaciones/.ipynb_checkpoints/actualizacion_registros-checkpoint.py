#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import os
import requests
import hashlib
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

url = 'https://dadesobertes.gva.es/dataset/a8a4b590-772d-4cba-a15c-fe6eff346431/resource/4e454fb5-1ba1-4ccd-8191-cc9b3700e47b/download/certificacion-energetica-de-edificios-en-valencia.csv'
folder_path = os.path.join("Datos", "RegistrosEnergeticos")

if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print(f"{Fore.GREEN}✅ Directorio creado en {folder_path}")

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
    existing_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
    existing_hashes = {}
    for existing_file in existing_files:
        file_hash = get_file_hash(existing_file)
        if file_hash:
            existing_hashes[existing_file] = file_hash
    
    if new_file_hash in existing_hashes.values():
        print(f"{Fore.YELLOW}⚠️ El fichero descargado es igual a uno existente. No se descarga un nuevo fichero.")
    else:
        current_date = datetime.now().strftime('%d-%m-%Y')
        file_name = f'registros_energeticos_{current_date}.csv'
        file_path = os.path.join(folder_path, file_name)

        if os.path.exists(file_path):
            print(f"{Fore.RED}⚠️ El archivo {file_name} ya existe en el directorio.")
        else:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"{Fore.GREEN}✅ El archivo ha sido guardado como {file_name}.")
else:
    print(f"{Fore.RED}⚠️ Error al descargar el archivo: {response.status_code}")
