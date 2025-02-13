#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import requests
from bs4 import BeautifulSoup
import os
import zipfile

catalogo_url = 'https://www.valencia.es/cas/estadistica/catalogo-de-publicaciones'
directorio_descargas = '/home/nnebot/PracticasNicoVRAIN/Datos'

def obtener_ultimo_anuario():
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
    print(f'Enlace donde se mete para buscar el archivo .zip: {enlace_descarga}')
    response = requests.get(enlace_descarga)
    soup = BeautifulSoup(response.content, 'html.parser')

    zip_link = None
    for enlace in soup.find_all('a', href=True):
        if enlace['href'].endswith('.zip'):
            zip_link = enlace['href']
            break

    if zip_link:
        print(f'Enlace para descargar el archivo .zip: {zip_link}')
        response = requests.get(zip_link)
        
        nombre_archivo = os.path.basename(zip_link)
        ruta_archivo = os.path.join(directorio_descargas, nombre_archivo)
        
        with open(ruta_archivo, 'wb') as file:
            file.write(response.content)
        
        print(f'Descargado: {nombre_archivo}')
        
        carpeta_anuario = os.path.join(directorio_descargas, f"Anuario{año}")
        os.makedirs(carpeta_anuario, exist_ok=True)

        with zipfile.ZipFile(ruta_archivo, 'r') as zip_ref:
            zip_ref.extractall(carpeta_anuario)
        print(f'Contenido extraído en: {carpeta_anuario}')
        
        os.remove(ruta_archivo)
        print(f'Archivo .zip eliminado: {nombre_archivo}')
    else:
        print('No se encontró un archivo .zip para descargar.')

def main():
    año, enlace_descarga = obtener_ultimo_anuario()
    if año and enlace_descarga:
        print(f'Último anuario encontrado: {año}')
        verificar_y_descargar_anuario(año, enlace_descarga)
    else:
        print('No se pudo obtener el último anuario.')

if __name__ == '__main__':
    main()