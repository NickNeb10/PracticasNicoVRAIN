#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import os
import requests
import hashlib
import pandas as pd
from bs4 import BeautifulSoup

pagina_url = "https://pegv.gva.es/auto/scpd/web/70403Construccion/aecv00186_v.html"
directorio_descargas = "/home/gti/PracticasNicoVRAIN/Datos"
base_url = "https://pegv.gva.es/auto/scpd/web/70403Construccion/"
nombre_archivo_local = "nuevas_edificaciones.xlsx"
ruta_archivo_local = os.path.join(directorio_descargas, nombre_archivo_local)
ruta_csv_local = os.path.join(directorio_descargas, "nuevas_edificaciones.csv")
ruta_hash = os.path.join(directorio_descargas, "hash_edificios.txt")

def obtener_enlace_excel(pagina_url, base_url):
    response = requests.get(pagina_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    enlace_excel = soup.find('a', href=True, string=lambda text: text and "Descàrrega" in text)

    if enlace_excel and enlace_excel['href'].endswith(".xlsx"):
        enlace_final = enlace_excel['href']
        if not enlace_final.startswith("http"):
            enlace_final = base_url + enlace_final  
        print(f"Enlace del archivo Excel encontrado: {enlace_final}")  
        return enlace_final
    
    return None

def calcular_hash(archivo):
    sha256 = hashlib.sha256()
    with open(archivo, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def archivo_actualizado(nuevo_archivo):
    if not os.path.exists(ruta_hash):
        return True  

    with open(ruta_hash, 'r') as f:
        hash_anterior = f.read().strip()

    hash_nuevo = calcular_hash(nuevo_archivo)
    return hash_nuevo != hash_anterior

def descargar_archivo(url, destino):
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print(f"Error al descargar el archivo: {response.status_code}")
        return
    
    if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' not in response.headers.get('Content-Type', ''):
        print("El archivo descargado no es un archivo Excel válido.")
        return
    
    with open(destino, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"Archivo guardado en {destino}")

def convertir_a_csv(ruta_excel, ruta_csv):
    try:
        df = pd.read_excel(ruta_excel, header=0)
        df = df.iloc[8:-3]
        df = df.dropna(how='all')
        df.to_csv(ruta_csv, index=False, sep=';')
        print(f"Archivo convertido y guardado como CSV en: {ruta_csv}")
    except Exception as e:
        print(f"Error al convertir el archivo a CSV: {e}")

def main():
    print(f"Buscando Excel en: {pagina_url}")
    enlace_excel = obtener_enlace_excel(pagina_url, base_url)

    if enlace_excel:
        print(f"Archivo Excel encontrado: {enlace_excel}")
        
        ruta_temporal = os.path.join(directorio_descargas, "temp.xlsx")
        descargar_archivo(enlace_excel, ruta_temporal)
        
        if archivo_actualizado(ruta_temporal):
            print("El archivo ha cambiado. Actualizando...")
            os.replace(ruta_temporal, ruta_archivo_local)
            with open(ruta_hash, 'w') as f:
                f.write(calcular_hash(ruta_archivo_local))
            print(f"Nuevo archivo guardado en: {ruta_archivo_local}")
            
            # Convertir a CSV
            convertir_a_csv(ruta_archivo_local, ruta_csv_local)
        else:
            print("No hay cambios en el archivo. No se actualiza.")
            os.remove(ruta_temporal)
    else:
        print("No se encontró un archivo Excel en la página.")

if __name__ == '__main__':
    main()
