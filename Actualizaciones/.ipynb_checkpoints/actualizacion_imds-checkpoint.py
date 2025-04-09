#!/usr/bin/env python
# coding: utf-8

# In[3]:


import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import hashlib
import pandas as pd
from colorama import Fore, Style, init
import unicodedata

init(autoreset=True)
URL = "https://www.valencia.es/cas/movilidad/otras-descargas"

now = datetime.now()
if now.month == 1:
    target_date = now.replace(year=now.year - 1, month=12)
else:
    target_date = now

CURRENT_YEAR = target_date.year
CURRENT_MONTH = target_date.strftime("%B").upper()

directorio_base = os.getcwd()
while not os.path.exists(os.path.join(directorio_base, "Datos")) and directorio_base != "/":
    directorio_base = os.path.dirname(directorio_base)

directorio_descargas = os.path.join(directorio_base, "Datos", "IMDS_Trafico")
os.makedirs(directorio_descargas, exist_ok=True)

ruta_hash = os.path.join(directorio_descargas, "hash_imds.txt")

def hash_dataframe(df):
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    return hashlib.md5(csv_bytes).hexdigest()

def clean_imd_column(df):
    imd_col = [col for col in df.columns if "IMD" in col.upper()][0]
    df[imd_col] = df[imd_col].astype(str).str.replace('.', '', regex=False).astype(int)
    return df

def normalizar(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def get_download_link(html, year):
    soup = BeautifulSoup(html, "html.parser")
    panels = soup.find_all("div", class_="panel panel-default")

    for panel in panels:
        body = panel.find("div", class_="panel-body")
        if body:
            links = body.find_all("a", href=True)
            for link in links:
                href = link['href']
                text = link.get_text(strip=True)
                text_normal = normalizar(text)
                
                if str(year) in text_normal and "imds vehiculos motorizados" in text_normal and ".ods" in href.lower():
                    if href.startswith("/"):
                        href = "https://www.valencia.es" + href
                    return href
    return None

def archivo_actualizado(df_nuevo):
    nuevo_hash = hash_dataframe(df_nuevo)

    if not os.path.exists(ruta_hash):
        return True, nuevo_hash

    with open(ruta_hash, "r") as f:
        hash_anterior = f.read().strip()

    return nuevo_hash != hash_anterior, nuevo_hash

def main():
    print(f"{Fore.YELLOW}🔍 Buscando archivo en la web...")
    response = requests.get(URL)
    response.raise_for_status()

    ods_link = get_download_link(response.text, CURRENT_YEAR)
    if not ods_link:
        print(f"{Fore.RED}❌ No se encontró el archivo del año actual.")
        return

    if ods_link.startswith("/"):
        ods_link = "https://www.valencia.es" + ods_link

    print(f"{Fore.BLUE}📥 Descargando archivo: {Style.BRIGHT}{ods_link}")
    file_data = requests.get(ods_link).content

    temp_path = os.path.join(directorio_descargas, "temp.ods")
    with open(temp_path, "wb") as f:
        f.write(file_data)

    try:
        xls = pd.read_excel(temp_path, sheet_name=None, engine="odf")
    except Exception as e:
        print(f"{Fore.RED}⚠️ Error leyendo el archivo: {e}")
        os.remove(temp_path)
        return

    if not xls:
        print(f"{Fore.RED}❌ El archivo no contiene hojas.")
        os.remove(temp_path)
        return

    hojas_actuales = sorted(xls.keys())

    nombre_total_csv = f"imds_total_{CURRENT_YEAR}.csv"
    ruta_csv_total = os.path.join(directorio_descargas, nombre_total_csv)

    hojas_existentes = []
    if os.path.exists(ruta_csv_total):
        df_existente = pd.read_csv(ruta_csv_total)
        hojas_existentes = list(df_existente["MES"].unique()) if "MES" in df_existente.columns else []

    hojas_nuevas = [h for h in hojas_actuales if h.strip() not in hojas_existentes]

    if not hojas_nuevas:
        print(f"{Fore.YELLOW}🟡 No hay hojas nuevas respecto al CSV actual. Nada que hacer.")
        os.remove(temp_path)
        return

    print(f"{Fore.GREEN}➕ Nuevas hojas detectadas: {', '.join(hojas_nuevas)}")

    datos_completos = []

    for nombre_hoja in hojas_actuales:
        df = xls[nombre_hoja]
        df = clean_imd_column(df)
        df["MES"] = nombre_hoja.strip()
        datos_completos.append(df)

    df_total = pd.concat(datos_completos, ignore_index=True)
    nuevo_hash = hash_dataframe(df_total)

    if os.path.exists(ruta_hash):
        with open(ruta_hash, "r") as f:
            hash_anterior = f.read().strip()
        if nuevo_hash == hash_anterior:
            print(f"{Fore.YELLOW}🔄 El contenido no ha cambiado respecto al hash anterior. No se guarda.")
            os.remove(temp_path)
            return

    # Eliminar archivo anterior solo si es del mismo año
    for archivo in os.listdir(directorio_descargas):
        if archivo.startswith("imds_total_") and archivo.endswith(".csv") and archivo != nombre_total_csv:
            if f"_{CURRENT_YEAR}" in archivo:
                os.remove(os.path.join(directorio_descargas, archivo))
                print(f"{Fore.MAGENTA}🧹 Eliminado archivo anterior del mismo año: {archivo}")

    df_total.to_csv(ruta_csv_total, index=False)
    with open(ruta_hash, "w") as f:
        f.write(nuevo_hash)

    os.remove(temp_path)
    print(f"{Fore.GREEN}✅ Nuevo archivo total guardado en: {Style.BRIGHT}{ruta_csv_total}")


if __name__ == "__main__":
    main()

