#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import os
import click
import json
import pandas as pd
from scrapegraphai.graphs import SmartScraperGraph
from markitdown import MarkItDown

def is_valid_json(text):
    try:
        json.loads(text)
        return True
    except ValueError:
        return False

@click.command()
@click.option('--directory', required=True, help='Ruta de la carpeta con archivos Excel.')
@click.option('--prompt', required=True, help='Prompt para extraer información.')
@click.option('--output', required=True, help='Nombre del archivo CSV de salida.')
@click.option('--markdown', default="data.md", help='Archivo Markdown de salida')

def extract_info(directory, prompt, output, markdown):
    if not os.path.isdir(directory):
        click.echo(f'❌ Error: La carpeta {directory} no existe.')
        return

    if os.path.exists(markdown):
        click.echo(f"📑 Usando archivo Markdown existente: {markdown}")
        with open(markdown, "r", encoding="utf-8") as f:
            markdown_data = f.read().split('\n\n') 
    else:
        click.echo(f"📂 Procesando archivos Excel para generar {markdown}...")
        markdown_data = []
        excel_sheets = {}  
        md_converter = MarkItDown()  

        for filename in os.listdir(directory):
            if filename.endswith('.xlsx') or filename.endswith('.xls'):
                file_path = os.path.join(directory, filename)
                click.echo(f'📂 Procesando archivo: {file_path}')

                try:
                    with pd.ExcelFile(file_path) as xls:  
                        for sheet_name in xls.sheet_names:
                            if "graf" in sheet_name.lower() or "map" in sheet_name.lower():
                                click.echo(f'⏩ Ignorando hoja: {sheet_name}')
                                continue

                            md_table = md_converter.convert(file_path)
                            markdown_data.append(f"### {filename} - {sheet_name}\n\n{md_table}\n\n")
                            excel_sheets[f"{filename} - {sheet_name}"] = (file_path, sheet_name)

                except Exception as e:
                    click.echo(f'⚠️ Error al procesar {file_path}: {e}')

        if not markdown_data:
            click.echo("❌ No se encontraron datos útiles en los archivos.")
            return

        with open(markdown, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_data))

        click.echo(f'📑 Archivo Markdown generado: {markdown}')

    graph_config = {"llm": {"model": "ollama/llama3.2"}, "verbose": True}
    
    scraper = SmartScraperGraph(
        prompt=f"Identifica qué tablas contienen información sobre {prompt}. Devuelve solo los nombres de los archivos y hojas relevantes.",
        source="\n".join(markdown_data),
        config=graph_config
    )

    result = scraper.run()

    if not is_valid_json(result):
        click.echo(f"⚠️ El resultado no es un JSON válido. La salida del LLM fue:\n{result}")
    else:
        json_data = json.loads(result)
        excel_sheets = {}  

        relevant_data = []
        for key in json_data:
            file_path, sheet_name = excel_sheets.get(key, (None, None))
            if file_path and sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                df["Archivo"] = file_path
                df["Hoja"] = sheet_name
                relevant_data.append(df)

        if relevant_data:
            final_df = pd.concat(relevant_data, ignore_index=True)
            final_df.to_csv(output, index=False, encoding="utf-8-sig")
            click.echo(f'✅ Se guardaron los resultados en "{output}".')
        else:
            click.echo("❌ No se encontró información relevante en las hojas detectadas.")

if __name__ == '__main__':
    extract_info()




