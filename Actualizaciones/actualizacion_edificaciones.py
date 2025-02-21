#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import requests
import hashlib
from bs4 import BeautifulSoup

pagina_url = "https://pegv.gva.es/auto/scpd/web/70403Construccion/aecv00186_v.html"
directorio_descargas = "/home/nnebsil/PracticasNicoVRAIN/Datos"
base_url = "https://pegv.gva.es/auto/scpd/web/70403Construccion/"
nombre_archivo_local = "nuevas_edificaciones.xlsx"
ruta_archivo_local = os.path.join(directorio_descargas, nombre_archivo_local)
ruta_hash = os.path.join(directorio_descargas, "hash_edificios.txt")

def obtener_enlace_excel(pagina_url, base_url):
    """Busca el enlace del archivo Excel en la página dada."""
    response = requests.get(pagina_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    enlace_excel = soup.find('a', href=True, string=lambda text: text and "Descàrrega" in text)

    if enlace_excel and enlace_excel['href'].endswith(".xlsx"):
        enlace_final = enlace_excel['href']
        if not enlace_final.startswith("http"):
            enlace_final = base_url + enlace_final  
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
    with open(destino, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

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
        else:
            print("No hay cambios en el archivo. No se actualiza.")
            os.remove(ruta_temporal)
    else:
        print("No se encontró un archivo Excel en la página.")

if __name__ == '__main__':
    main()

