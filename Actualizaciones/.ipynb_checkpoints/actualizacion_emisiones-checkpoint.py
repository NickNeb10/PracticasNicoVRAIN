#!/usr/bin/env python
# coding: utf-8

# In[ ]:
#!/usr/bin/env python
# coding: utf-8
import os
import requests
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup

pagina_url = "https://www.miteco.gob.es/es/calidad-y-evaluacion-ambiental/temas/sistema-espanol-de-inventario-sei-/inventario-gases-efecto-invernadero.html"
base_url = "https://www.miteco.gob.es"

directorio_descargas = "/home/nnebot/PracticasNicoVRAIN/Datos/Emisiones_Invernadero"
os.makedirs(directorio_descargas, exist_ok=True)

if not os.path.exists(directorio_descargas):
    print(f"La carpeta {directorio_descargas} no existe. Se creará ahora.")
    os.makedirs(directorio_descargas, exist_ok=True)
else:
    print(f"La carpeta {directorio_descargas} ya existe.")

def obtener_enlace_pdf():
    response = requests.get(pagina_url)
    if response.status_code != 200:
        print(f"Error al acceder a la página: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    enlace_pdf = soup.find('a', href=True, string=lambda text: text and "Documento resumen" in text)
    if enlace_pdf:
        enlace_final = enlace_pdf['href']
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

def es_archivo_nuevo(nuevo_archivo):
    hash_nuevo = calcular_hash(nuevo_archivo)
    archivos_pdf = [f for f in os.listdir(directorio_descargas) if f.endswith(".pdf") and f != "temp.pdf"]
    if not archivos_pdf: 
        return True  

    for archivo in archivos_pdf:
        ruta_archivo = os.path.join(directorio_descargas, archivo)
        hash_existente = calcular_hash(ruta_archivo)
        print(f"Comparando con {archivo} - Hash existente: {hash_existente}")
        if hash_nuevo == hash_existente:
            return False  
    return True  

def descargar_pdf(url):
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print(f"Error al descargar el archivo: {response.status_code}")
        return None
    
    content_type = response.headers.get('Content-Type', '')
    if 'application/pdf' not in content_type:
        print("El archivo descargado no es un PDF válido.")
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
        print(f"Nuevo archivo guardado en: {ruta_final}")
    else:
        print("El archivo ya existe en la carpeta. No se guardará una copia nueva.")
        os.remove(ruta_temporal)

def main():
    enlace_pdf = obtener_enlace_pdf()
    if enlace_pdf:
        print(f"Enlace del PDF encontrado: {enlace_pdf}")
        descargar_pdf(enlace_pdf)
    else:
        print("No se encontró el PDF en la página.")

if __name__ == '__main__':
    main()