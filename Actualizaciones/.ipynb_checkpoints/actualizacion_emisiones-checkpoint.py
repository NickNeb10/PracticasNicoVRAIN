#!/usr/bin/env python
# coding: utf-8

# In[ ]:
#!/usr/bin/env python
# coding: utf-8
"""
Este script automatiza la descarga del PDF del "Documento resumen" del inventario de gases
de efecto invernadero desde el sitio del MITECO. Verifica si ya existe una copia previa usando
hashes SHA-256 para evitar duplicados. Si el archivo es nuevo, lo guarda con fecha.
"""

import os
import requests
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

init(autoreset=True)

pagina_url = "https://www.miteco.gob.es/es/calidad-y-evaluacion-ambiental/temas/sistema-espanol-de-inventario-sei-/inventario-gases-efecto-invernadero.html"
base_url = "https://www.miteco.gob.es"
directorio_descargas = os.path.join("Datos", "Emisiones_Invernadero")
os.makedirs(directorio_descargas, exist_ok=True)

def obtener_enlace_pdf():
    """
    Busca en la página del MITECO el enlace al PDF con el Documento resumen.

    Returns:
        str or None: URL completa al PDF si se encuentra, o None si falla.
    """
    print(f"{Fore.YELLOW}{Style.BRIGHT}✨ Obteniendo el enlace al PDF... ✨")
    response = requests.get(pagina_url)
    if response.status_code != 200:
        print(f"{Fore.RED}⚠️ Error al acceder a la página: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    enlace_pdf = soup.find('a', href=True, string=lambda text: text and "Documento resumen" in text)
    if enlace_pdf:
        enlace_final = enlace_pdf['href']
        if not enlace_final.startswith("http"):
            enlace_final = base_url + enlace_final
        return enlace_final

    print(f"{Fore.RED}⚠️ No se encontró el PDF en la página.")
    return None

def calcular_hash(archivo):
    """
    Calcula el hash SHA-256 de un archivo.

    Args:
        archivo (str): Ruta al archivo local.

    Returns:
        str: Hash SHA-256 del archivo.
    """
    sha256 = hashlib.sha256()
    with open(archivo, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def es_archivo_nuevo(nuevo_archivo):
    """
    Compara el hash del nuevo archivo con los ya existentes en el directorio.

    Args:
        nuevo_archivo (str): Ruta al archivo recién descargado (temporal).

    Returns:
        bool: True si no hay duplicados, False si ya existe uno igual.
    """
    hash_nuevo = calcular_hash(nuevo_archivo)
    archivos_pdf = [f for f in os.listdir(directorio_descargas) if f.endswith(".pdf") and f != "temp.pdf"]
    if not archivos_pdf:
        return True

    for archivo in archivos_pdf:
        ruta_archivo = os.path.join(directorio_descargas, archivo)
        hash_existente = calcular_hash(ruta_archivo)
        print(f"{Fore.CYAN}🔍 Comparando con {archivo} - Hash existente: {hash_existente}")
        if hash_nuevo == hash_existente:
            return False
    return True

def descargar_pdf(url):
    """
    Descarga un archivo PDF desde la URL y lo guarda si no es duplicado.

    Args:
        url (str): Enlace al archivo PDF.

    Returns:
        None
    """
    print(f"{Fore.YELLOW}🔽 Iniciando la descarga del PDF...")
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print(f"{Fore.RED}⚠️ Error al descargar el archivo: {response.status_code}")
        return None

    content_type = response.headers.get('Content-Type', '')
    if 'application/pdf' not in content_type:
        print(f"{Fore.RED}⚠️ El archivo descargado no es un PDF válido.")
        return None

    fecha_actual = datetime.now().strftime("%d-%m-%Y")
    nombre_archivo = f"Documento_resumen_Inventario_GEI_{fecha_actual}.pdf"
    ruta_temporal = os.path.join(directorio_descargas, "temp.pdf")
    ruta_final = os.path.join(directorio_descargas, nombre_archivo)

    with open(ruta_temporal, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    if es_archivo_nuevo(ruta_temporal):
        os.rename(ruta_temporal, ruta_final)
        print(f"{Fore.GREEN}✅ Nuevo archivo guardado en: {ruta_final}")
    else:
        print(f"{Fore.YELLOW}⚠️ El archivo ya existe en la carpeta. No se guardará una copia nueva.")
        os.remove(ruta_temporal)

def main():
    """
    Función principal que orquesta la descarga del PDF si hay uno nuevo disponible.

    Returns:
        None
    """
    print(f"{Fore.YELLOW}✨ Comenzando el proceso de descarga... ✨")
    enlace_pdf = obtener_enlace_pdf()
    if enlace_pdf:
        print(f"{Fore.CYAN}🔗 Enlace del PDF encontrado: {enlace_pdf}")
        descargar_pdf(enlace_pdf)
    else:
        print(f"{Fore.RED}⚠️ No se pudo obtener el enlace al PDF.")

if __name__ == '__main__':
    main()

