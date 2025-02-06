#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import click
import pandas as pd
import glob
import os

@click.command()
@click.option(
    "-d", "--directory",
    default=".",
    type=click.Path(exists=True),
    help="Directorio que contiene los archivos Excel",
)
@click.option(
    "-t", "--text",
    type=str,
    required=True,
    help="Texto a buscar en los archivos Excel",
)
@click.option(
    "-o", "--output",
    default="result.csv",
    type=click.Path(),
    help="Archivo CSV donde se guardará la tabla encontrada",
)
def search_text_in_excels(directory, text, output):
    """
    Busca un texto en archivos Excel dentro de un directorio y guarda la tabla correspondiente.
    """
    excel_files = glob.glob(os.path.join(directory, "*.xlsx"))
    matches = []
    
    for file in excel_files:
        xls = pd.ExcelFile(file)
        for sheet_name in xls.sheet_names:
            df = xls.parse(sheet_name)
            
            mask = df.astype(str).apply(lambda x: x.str.contains(text, case=False, na=False))
            if mask.any().any():
                row_idx, col_idx = mask.stack()[mask.stack()].index[0]  # Primera coincidencia
                matches.append((file, sheet_name, row_idx, col_idx, df))
    
    if not matches:
        print("Texto no encontrado en ningún archivo.")
        return
    
    if len(matches) > 1:
        print("Se encontraron varias coincidencias. Elija una:")
        for i, (file, sheet, row, col, _) in enumerate(matches):
            print(f"[{i}] Archivo: {file}, Hoja: {sheet}, Celda: ({row+1}, {col+1})")
        choice = int(input("Ingrese el número de la opción deseada: "))
    else:
        choice = 0
    
    file, sheet_name, row_idx, col_idx, df = matches[choice]
    print(f"Guardando tabla desde: {file}, Hoja: {sheet_name}")
    
    table = df.iloc[row_idx:]
    table.to_csv(output, index=False)
    print(f"Tabla guardada en {output}")

if __name__ == "__main__":
    search_text_in_excels()

