#!/usr/bin/env python
# coding: utf-8

# In[ ]:
#!/usr/bin/env python
# coding: utf-8
import os
import re
from datetime import datetime
from markitdown import MarkItDown

directorio_descargas = "/home/nnebot/PracticasNicoVRAIN/Datos/Emisiones_Invernadero"

def obtener_pdf_mas_reciente(directorio_descargas):
    """
    Busca el archivo PDF más reciente en un directorio, según una fecha en el nombre del archivo con formato dd-mm-aaaa.

    Args:
        directorio_descargas (str): Ruta al directorio donde buscar los archivos PDF.

    Returns:
        str | None: Ruta al archivo PDF más reciente, o None si no se encuentra.
    """
    archivos_pdf = [f for f in os.listdir(directorio_descargas) if f.endswith(".pdf")]

    if not archivos_pdf:
        print("No se encontraron archivos PDF en la carpeta.")
        return None

    archivos_con_fecha = []
    patron_fecha = r"(\d{2}-\d{2}-\d{4})\.pdf$"

    for archivo in archivos_pdf:
        coincidencia = re.search(patron_fecha, archivo)
        if coincidencia:
            fecha_str = coincidencia.group(1)
            fecha_objeto = datetime.strptime(fecha_str, "%d-%m-%Y")
            archivos_con_fecha.append((archivo, fecha_objeto))

    if not archivos_con_fecha:
        print("No se encontraron archivos con fechas válidas.")
        return None

    archivo_mas_reciente = max(archivos_con_fecha, key=lambda x: x[1])
    return os.path.join(directorio_descargas, archivo_mas_reciente[0])

def convertir_pdf_a_markdown(pdf_path):
    """
    Convierte un archivo PDF a texto en formato Markdown usando MarkItDown.

    Args:
        pdf_path (str): Ruta del archivo PDF a convertir.

    Returns:
        str | None: Texto en formato Markdown si tiene éxito, o None si ocurre un error.
    """
    try:
        md = MarkItDown()
        result = md.convert(pdf_path)
        return result.text_content
    except Exception as e:
        print(f"Error al convertir el PDF a Markdown: {e}")
        return None

def extraer_subsector_emisiones(markdown_text):
    """
    Busca en el texto Markdown el subsector con más peso en las emisiones de GEI.

    Args:
        markdown_text (str): Texto en formato Markdown.

    Returns:
        list[str]: Lista de coincidencias encontradas o un mensaje si no se encontró nada.
    """
    patron = r"subsector.*más.*peso.*emisiones.*\s*(\w+.*?[\d,]+%)"
    resultados = re.findall(patron, markdown_text, re.IGNORECASE)
    if resultados:
        return resultados
    else:
        return ["No se encontró información sobre el subsector con más peso."]

def guardar_markdown(markdown_text, pdf_filename):
    """
    Guarda el texto Markdown extraído de un PDF con un nombre basado en la fecha del archivo.

    Args:
        markdown_text (str): Texto Markdown a guardar.
        pdf_filename (str): Nombre del archivo PDF original, que contiene la fecha.
    """
    patron_fecha = r"(\d{2}-\d{2}-\d{4})\.pdf$"
    coincidencia = re.search(patron_fecha, pdf_filename)
    if coincidencia:
        fecha_str = coincidencia.group(1)
        archivo_salida = os.path.join(directorio_descargas, f"markdownEmisiones{fecha_str}.md")
        with open(archivo_salida, 'w') as f:
            f.write(markdown_text)
        print(f"Contenido Markdown guardado en {archivo_salida}")
    else:
        print("No se pudo extraer la fecha del archivo PDF.")

def main():
    """
    Función principal: busca el PDF más reciente, lo convierte a Markdown, guarda el resultado
    y extrae el subsector con mayor peso en las emisiones de GEI.
    """
    pdf_path = obtener_pdf_mas_reciente(directorio_descargas)

    if pdf_path:
        print(f"Archivo PDF encontrado: {pdf_path}")

        markdown_text = convertir_pdf_a_markdown(pdf_path)

        if markdown_text:
            print("Markdown convertido desde PDF.")
            print("Contenido del Markdown:")

            guardar_markdown(markdown_text, os.path.basename(pdf_path))

            subsector_emisiones = extraer_subsector_emisiones(markdown_text)
            print("Subsector con más peso en las emisiones de GEI:")
            for subsector in subsector_emisiones:
                print(subsector)
        else:
            print("No se pudo convertir el PDF a Markdown.")
    else:
        print("No se encontraron archivos PDF en la carpeta para procesar.")

if __name__ == '__main__':
    main()