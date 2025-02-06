#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import click
import pandas as pd
import glob
from scrapegraphai.graphs import SmartScraperGraph

@click.command()
@click.option("--directory", default=".", help="Directorio que contiene los archivos Excel")
@click.option("--prompt", prompt="Describe qué información deseas extraer", help="Prompt para buscar en los archivos Excel")
@click.option("--output", default="output.csv", help="Archivo de salida donde se guardará la información extraída")
def extract_from_excel(directory, prompt, output):
    files = glob.glob(f"{directory}/*.xlsx")  # Buscar todos los archivos Excel en la carpeta
    extracted_data = []

    for file in files:
        xls = pd.ExcelFile(file)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # Convertimos el DataFrame a texto para procesarlo con ScrapeGraphAI
            text_data = df.to_csv(index=False, sep='|')
            
            # Configurar ScrapeGraphAI
            graph_config = {"llm": {"model": "ollama/llama3.2"}, "verbose": True}
            scraper = SmartScraperGraph(
                prompt=prompt,
                source=text_data,
                config=graph_config
            )
            
            result = scraper.run()
            if result:
                print(result)
                extracted_data.append(pd.DataFrame(result))

    if extracted_data:
        final_df = pd.concat(extracted_data, ignore_index=True)
        final_df.to_csv(output, index=False)
        print(f"Información extraída guardada en {output}")
    else:
        print("No se encontró información relevante.")

if __name__ == "__main__":
    extract_from_excel()

