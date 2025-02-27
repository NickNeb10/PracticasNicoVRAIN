#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import pandas as pd
import argparse
import re

def limpiar_texto(texto):
    if isinstance(texto, str):
        texto = texto.strip()
        texto = re.sub(r'\s+', ' ', texto)
        texto = texto.replace("\n", " ").replace("\r", " ")
        return texto.lower()
    return ""

def buscar_titulo_en_hoja(archivo, carpeta, nombre_hoja, titulo_buscado, resultados):
    archivo_path = os.path.join(carpeta, archivo)
    try:
        excel_data = pd.ExcelFile(archivo_path)
        if nombre_hoja in excel_data.sheet_names:
            df = excel_data.parse(nombre_hoja)
            print(f"Buscando '{titulo_buscado}' en el archivo '{archivo}', hoja '{nombre_hoja}'...")
            titulo_buscado_cleaned = limpiar_texto(titulo_buscado)
            for i, row in df.iterrows():
                for cell in row:
                    if isinstance(cell, str):
                        cell_cleaned = limpiar_texto(cell)
                        if titulo_buscado_cleaned in cell_cleaned:
                            print(f"¡Encontrado '{titulo_buscado}' en la fila {i + 1} de la hoja '{nombre_hoja}'!")
                            resultados.append({
                                'Archivo': archivo,
                                'Hoja': nombre_hoja,
                                'Fila': i + 1,
                                'Contenido': row.to_dict()
                            })
                            return
            print(f"No se encontró '{titulo_buscado}' en la hoja '{nombre_hoja}' del archivo '{archivo}'.")
        else:
            print(f"La hoja '{nombre_hoja}' no se encuentra en el archivo '{archivo}'.")
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

def buscar_en_toda_carpeta(carpeta, titulo_buscado):
    archivos_encontrados = []
    resultados = []
    
    for archivo in os.listdir(carpeta):
        if archivo.endswith('.xlsx'):
            print(f"Procesando archivo: {archivo}")
            archivo_path = os.path.join(carpeta, archivo)
            excel_data = pd.ExcelFile(archivo_path)

            for nombre_hoja in excel_data.sheet_names:
                if 'map' in nombre_hoja.lower() or 'graf' in nombre_hoja.lower():
                    print(f"Saltando la hoja '{nombre_hoja}' en el archivo '{archivo}' (contiene 'map' o 'graf').")
                    continue
                buscar_titulo_en_hoja(archivo, carpeta, nombre_hoja, titulo_buscado, resultados)

            if resultados:  
                archivos_encontrados.append(archivo)

    if archivos_encontrados:
        print("\nArchivos que contienen el término de búsqueda:")
        for i, archivo in enumerate(archivos_encontrados, 1):
            print(f"{i}. {archivo}")

        seleccion = int(input("\nSelecciona el número del archivo que deseas procesar: ")) - 1
        archivo_seleccionado = archivos_encontrados[seleccion]
        print(f"\nProcesando el archivo '{archivo_seleccionado}'...")

        if resultados:
            df_resultados = pd.DataFrame(resultados)
            csv_path = os.path.join(carpeta, f"resultados_{archivo_seleccionado}.csv")
            df_resultados.to_csv(csv_path, index=False)
            print(f"\nLos resultados se han guardado en '{csv_path}'.")

def main():
    parser = argparse.ArgumentParser(description="Buscar un título en tablas dentro de archivos Excel en una carpeta y guardar los resultados en un CSV.")
    parser.add_argument('carpeta', help="Ruta de la carpeta donde están los archivos Excel")
    parser.add_argument('titulo', help="Título que buscas dentro de las hojas de los archivos")
    args = parser.parse_args()
    buscar_en_toda_carpeta(args.carpeta, args.titulo)

if __name__ == '__main__':
    main()

