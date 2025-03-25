#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import requests
from bs4 import BeautifulSoup
import os
import zipfile
import subprocess
from colorama import Fore, Style, init

# Inicializamos colorama
init(autoreset=True)

# URL del catálogo de publicaciones
catalogo_url = 'https://www.valencia.es/cas/estadistica/catalogo-de-publicaciones'
directorio_descargas = '/home/nnebot/PracticasNicoVRAIN/Datos'

def obtener_ultimo_anuario():
    """
    Obtiene el último anuario estadístico disponible en la página del Ayuntamiento de València.

    Returns:
        tuple: Año más reciente (str) y enlace a la página del anuario (str).
    """
    print(f"{Fore.YELLOW}{Style.BRIGHT}✨ Obteniendo el último anuario disponible... ✨\n")
    response = requests.get(catalogo_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    anuario_section = soup.find_all('tr')
    años = []
    anuario_enlaces = {}
    
    for row in anuario_section:
        titulo = row.find('strong', string=lambda x: x and 'Anuario Estadístico' in x)
        if titulo:
            texto_titulo = titulo.string.strip()
            año = ''.join(filter(str.isdigit, texto_titulo))
            if len(año) == 4:
                enlace_td = row.find('td', class_='text-left padding-left-50px')
                if enlace_td:
                    enlace = enlace_td.find('a', href=True)
                    if enlace:
                        anuario_enlaces[año] = enlace['href']
                        años.append(int(año))

    if años:
        ultimo_año = str(max(años))
        return ultimo_año, anuario_enlaces[ultimo_año]

    return None, None

def verificar_y_descargar_anuario(año, enlace_descarga):
    """
    Verifica y descarga el anuario estadístico para el año especificado, lo descomprime y elimina el ZIP.

    Args:
        año (str): Año del anuario.
        enlace_descarga (str): Enlace a la página de descarga del anuario.
    """
    response = requests.get(enlace_descarga)
    soup = BeautifulSoup(response.content, 'html.parser')

    zip_link = None
    for enlace in soup.find_all('a', href=True):
        if enlace['href'].endswith('.zip'):
            zip_link = enlace['href']
            break

    if zip_link:
        print(f"{Fore.CYAN}🔗 Enlace de descarga del archivo .zip: {Style.BRIGHT}{zip_link}")
        response = requests.get(zip_link)
        
        nombre_archivo = os.path.basename(zip_link)
        ruta_archivo = os.path.join(directorio_descargas, nombre_archivo)
        
        with open(ruta_archivo, 'wb') as file:
            file.write(response.content)
        
        print(f"{Fore.GREEN}✅ {nombre_archivo} descargado correctamente.\n")
        
        carpeta_anuario = os.path.join(directorio_descargas, f"Anuario{año}")
        os.makedirs(carpeta_anuario, exist_ok=True)

        with zipfile.ZipFile(ruta_archivo, 'r') as zip_ref:
            zip_ref.extractall(carpeta_anuario)
        print(f"{Fore.YELLOW}📂 Contenido extraído en: {carpeta_anuario}")
        
        os.remove(ruta_archivo)
        print(f"{Fore.RED}🗑️ Archivo .zip eliminado: {nombre_archivo}\n")
    else:
        print(f"{Fore.RED}⚠️ No se encontró un archivo .zip para descargar.\n")

PARSER_SCRIPT = "/home/nnebot/PracticasNicoVRAIN/Parser_LLM/parser_excel2.py"

TABLAS_A_BUSCAR = {
    "facturación_electrica{}.csv": "Número de contratos y facturación por código postal y sector económico",
    "bienes_inmueblesbarrio{}.csv": "Bienes Inmuebles según uso por barrio",
    "bienes_inmueblesdistrito{}.csv": "Bienes Inmuebles según uso por distrito",
    "facturacion_gas{}.csv": "Abonados y facturación de gas natural por mes según tipo de instalación",
    "parque_vehiculos{}.csv": "Parque de vehículos según tipo de vehículo y carburante",
    "renta_mediana{}.csv": "Renta disponible media por declaración de residentes en la ciudad por código postal",
    "residuos_urbanos{}.csv": "Residuos sólidos urbanos procedentes de València tratados según mes",
    "subproductos_residuos{}.csv": "Subproductos obtenidos del tratamiento de residuos sólidos",
    "turismos_titular{}.csv": "Turismos según tipo de titular por distrito",
    "zonasverdes_numero{}.csv": "Número y superficie de las zonas verdes de gestión municipal",
    "zonasverdes_superficie{}.csv": "Superficie de las zonas verdes urbanas en la ciudad según tipo"
}

def ejecutar_parser(directorio_anuario, año):
    """
    Ejecuta un script parser para extraer tablas específicas desde los archivos del anuario descomprimido.

    Args:
        directorio_anuario (str): Ruta al directorio donde se extrajo el anuario.
        año (str): Año del anuario, usado para nombrar los archivos de salida.
    """
    cache_dir = '/home/nnebot/PracticasNicoVRAIN/Datos/DatosAnuario'
    os.makedirs(cache_dir, exist_ok=True) 

    print(f"\n{Fore.YELLOW}🔍 Iniciando búsqueda de tablas para el año {año}...\n")
    for nombre_base, texto_a_buscar in TABLAS_A_BUSCAR.items():
        nombre_fichero = nombre_base.format(año) 
        ruta_salida = os.path.join(cache_dir, nombre_fichero)

        print(f"{Fore.CYAN}🔎 Buscando '{texto_a_buscar}'")
        comando = [
            "python3",
            PARSER_SCRIPT,
            "--directory", directorio_anuario,
            "--text", texto_a_buscar,
            "--output", ruta_salida,
            "--cache-dir", cache_dir  
        ]
        try:
            subprocess.run(comando, check=True)
            print(f"{Fore.GREEN}✅ Tabla guardada exitosamente en {ruta_salida}\n")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}⚠️ Error ejecutando el parser para {texto_a_buscar}: {e}\n")

def main():
    """
    Función principal que coordina la obtención del anuario, su descarga y extracción de tablas.
    """
    año, enlace_descarga = obtener_ultimo_anuario()
    if año and enlace_descarga:
        print(f"{Fore.YELLOW}📅 Último anuario encontrado: {año}\n")
        verificar_y_descargar_anuario(año, enlace_descarga)
        directorio_anuario = os.path.join(directorio_descargas, f"Anuario{año}")
        ejecutar_parser(directorio_anuario, año)
    else:
        print(f"{Fore.RED}⚠️ No se pudo obtener el último anuario.\n")

if __name__ == '__main__':
    main()
