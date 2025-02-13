#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import os
import requests
import hashlib

url = 'https://dadesobertes.gva.es/dataset/a8a4b590-772d-4cba-a15c-fe6eff346431/resource/4e454fb5-1ba1-4ccd-8191-cc9b3700e47b/download/certificacion-energetica-de-edificios-en-valencia.csv'
file_path = '/home/nnebot/PracticasNicoVRAIN/Datos/registros_energeticos.csv'

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
    old_file_hash = get_file_hash(file_path)

    if old_file_hash != new_file_hash:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print("El archivo ha sido actualizado.")
    else:
        print("El archivo no ha cambiado.")
else:
    print(f"Error al descargar el archivo: {response.status_code}")