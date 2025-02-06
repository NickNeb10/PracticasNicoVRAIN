#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import click
import pandas as pd
import glob
import os
import re
import pickle
import unicodedata
import hashlib

CACHE_FILE = "processed_excels.pkl"
CACHE_HASHES_FILE = "processed_hashes.pkl"

def normalize_text(text):
    if isinstance(text, str):
        text = text.strip()
        text = unicodedata.normalize("NFC", text)
        text = re.sub(r"\s+", " ", text)
    return text

def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

@click.command()
@click.option("-d", "--directory", default=".", type=click.Path(exists=True), help="Directorio que contiene los archivos Excel")
@click.option("-t", "--text", type=str, required=True, multiple=True, help="Expresiones regulares a buscar en los archivos Excel (pueden ser varias)")
@click.option("-o", "--output", default="result.csv", type=click.Path(), help="Archivo CSV donde se guardará la tabla encontrada")
@click.option("-c", "--choice", type=int, default=None, help="Número de la coincidencia deseada (si hay varias)")

def search_text_in_excels(directory, text, output, choice):
    try:
        print(f"Searching in directory: {directory}")
        
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "rb") as f:
                processed_excels = pickle.load(f)
        else:
            processed_excels = {}

        if os.path.exists(CACHE_HASHES_FILE):
            with open(CACHE_HASHES_FILE, "rb") as f:
                processed_hashes = pickle.load(f)
        else:
            processed_hashes = {}

        excel_files = glob.glob(os.path.join(directory, "*.xlsx"))
        matches = []
        normalized_texts = [normalize_text(t) for t in text]
        
        for file in excel_files:
            file_hash = get_file_hash(file)

            if file not in processed_hashes or processed_hashes[file] != file_hash:
                xls = pd.ExcelFile(file)
                sheet_names = xls.sheet_names
                df_dict = {}
                for sheet_name in sheet_names:
                    if re.search(r"graf|map", sheet_name, re.IGNORECASE):
                        continue
                    
                    df = pd.read_excel(file, sheet_name=sheet_name, header=None, dtype=str)
                    df = df.map(normalize_text)  
                    df_dict[sheet_name] = df

                processed_excels[file] = df_dict
                processed_hashes[file] = file_hash

                with open(CACHE_FILE, "wb") as f:
                    pickle.dump(processed_excels, f)
                with open(CACHE_HASHES_FILE, "wb") as f:
                    pickle.dump(processed_hashes, f)
            else:
                df_dict = processed_excels[file]
            
            for sheet_name, df in df_dict.items():
                for pattern in normalized_texts:
                    regex = re.compile(pattern, re.IGNORECASE)
                    mask = df.astype(str).apply(lambda x: x.str.contains(regex, na=False))
                    if mask.any().any():
                        row_idx, col_idx = mask.stack()[mask.stack()].index[0]
                        found_text = df.iloc[row_idx, col_idx]
                        print(f"[{len(matches)}] Archivo: {file}, Hoja: {sheet_name}, Texto encontrado: \"{found_text}\"")
                        matches.append((file, sheet_name, df))
        
        if not matches:
            print("Texto no encontrado en ningún archivo.")
            return
        
        if choice is None:
            if len(matches) > 1:
                print("Se encontraron varias coincidencias. Elija una con el parámetro -c:")
                return
            choice = 0  
        
        if choice < 0 or choice >= len(matches):
            print("Opción inválida. Use un número dentro del rango de coincidencias.")
            return
        
        file, sheet_name, df = matches[choice]
        print(f"Guardando tabla desde: {file}, Hoja: {sheet_name}")
        
        df.to_csv(output, index=False, sep=";", header=False, encoding="utf-8-sig")
        print(f"Datos guardados en {output}")
    
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    search_text_in_excels()

