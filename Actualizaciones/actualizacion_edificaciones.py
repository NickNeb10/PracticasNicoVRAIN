#!/usr/bin/env python
# coding: utf-8

# In[ ]:
"""
Descarga y procesamiento de un archivo Excel desde la página del PEGV (GVA), con verificación de cambios
por hash SHA-256 y conversión a CSV si hay una actualización.
"""

import os
import requests
import hashlib
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

PAGINA_URL = "https://pegv.gva.es/auto/scpd/web/70403Construccion/aecv00186_v.html"
BASE_URL = "https://pegv.gva.es/auto/scpd/web/70403Construccion/"

directorio_base = os.getcwd()
while not os.path.exists(os.path.join(directorio_base, "Datos")) and directorio_base != "/":
    directorio_base = os.path.dirname(directorio_base)

directorio_descargas = os.path.join(directorio_base, "Datos", "Nuevas_Edificaciones")
ruta_hash = os.path.join(directorio_descargas, "hash_edificios.txt")

def obtener_enlace_excel():
    """
    Extrae el enlace al archivo Excel desde la página del PEGV.

    Returns:
        str or None: URL completa del archivo Excel si se encuentra, o None si no.
    """
    print(f"{Fore.YELLOW}{Style.BRIGHT}🔍 Buscando el archivo Excel en la página...")

    response = requests.get(PAGINA_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    enlace_excel = soup.find('a', href=True, string=lambda text: text and "Descàrrega" in text)

    if enlace_excel and enlace_excel['href'].endswith(".xlsx"):
        enlace_final = enlace_excel['href']
        if not enlace_final.startswith("http"):
            enlace_final = BASE_URL + enlace_final
        print(f"{Fore.CYAN}🔗 Enlace del archivo Excel encontrado: {Style.BRIGHT}{enlace_final}")
        return enlace_final
    else:
        print(f"{Fore.RED}⚠️ No se encontró un archivo Excel en la página.")
        return None

def calcular_hash(archivo):
    """
    Calcula el hash SHA-256 de un archivo dado.

    Args:
        archivo (str): Ruta al archivo.

    Returns:
        str: Hash SHA-256 del contenido del archivo.
    """
    sha256 = hashlib.sha256()
    with open(archivo, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def archivo_actualizado(nuevo_archivo):
    """
    Verifica si el archivo descargado es diferente al último guardado, comparando hashes.

    Args:
        nuevo_archivo (str): Ruta del nuevo archivo descargado temporalmente.

    Returns:
        bool: True si el archivo es nuevo o actualizado, False si es el mismo.
    """
    if not os.path.exists(ruta_hash):
        return True

    with open(ruta_hash, 'r') as f:
        hash_anterior = f.read().strip()

    hash_nuevo = calcular_hash(nuevo_archivo)
    return hash_nuevo != hash_anterior

def descargar_archivo(url, destino):
    """
    Descarga el archivo desde la URL proporcionada y lo guarda en la ruta de destino.

    Args:
        url (str): Enlace al archivo.
        destino (str): Ruta local donde se guardará el archivo.

    Returns:
        bool: True si la descarga fue exitosa, False en caso de error o tipo inválido.
    """
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    print(f"{Fore.BLUE}📥 Descargando archivo desde: {Style.BRIGHT}{url}")

    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print(f"{Fore.RED}❌ Error al descargar el archivo: {response.status_code}")
        return False

    if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' not in response.headers.get('Content-Type', ''):
        print(f"{Fore.RED}⚠️ El archivo descargado no es un archivo Excel válido.")
        return False

    with open(destino, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print(f"{Fore.GREEN}✅ Archivo guardado en {Style.BRIGHT}{destino}")
    return True

def convertir_a_csv(ruta_excel, ruta_csv):
    """
    Convierte un archivo Excel en CSV, omitiendo filas vacías y cabeceras/pies no útiles.

    Args:
        ruta_excel (str): Ruta al archivo Excel.
        ruta_csv (str): Ruta donde se guardará el CSV generado.

    Returns:
        None
    """
    try:
        df = pd.read_excel(ruta_excel, header=0)
        df = df.iloc[8:-3]
        df = df.dropna(how='all')
        df.to_csv(ruta_csv, index=False, sep=';')
        print(f"{Fore.YELLOW}📄 Archivo convertido y guardado como CSV en: {Style.BRIGHT}{ruta_csv}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error al convertir el archivo a CSV: {e}")

def main():
    """
    Función principal que coordina la búsqueda, descarga, verificación y conversión del archivo Excel.

    Returns:
        None
    """
    print(f"{Fore.YELLOW}{Style.BRIGHT}✨ Iniciando el proceso de actualización de datos... ✨")

    enlace_excel = obtener_enlace_excel()

    if enlace_excel:
        ruta_temporal = os.path.join(directorio_descargas, "temp.xlsx")

        if descargar_archivo(enlace_excel, ruta_temporal):
            if archivo_actualizado(ruta_temporal):
                print(f"{Fore.GREEN}📌 El archivo ha cambiado. Actualizando...")

                fecha_actual = datetime.now().strftime("%d-%m-%Y")
                nombre_archivo_local = f"nuevas_edificaciones_{fecha_actual}.xlsx"
                ruta_archivo_local = os.path.join(directorio_descargas, nombre_archivo_local)

                os.replace(ruta_temporal, ruta_archivo_local)
                with open(ruta_hash, 'w') as f:
                    f.write(calcular_hash(ruta_archivo_local))

                print(f"{Fore.GREEN}✅ Nuevo archivo guardado en: {Style.BRIGHT}{ruta_archivo_local}")

                ruta_csv_local = os.path.join(directorio_descargas, f"nuevas_edificaciones_{fecha_actual}.csv")
                convertir_a_csv(ruta_archivo_local, ruta_csv_local)
            else:
                print(f"{Fore.YELLOW}🔄 No hay cambios en el archivo. No se actualiza.")
                os.remove(ruta_temporal)
    else:
        print(f"{Fore.RED}⚠️ No se encontró un archivo Excel para descargar.")

if __name__ == '__main__':
    main()

