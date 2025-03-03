#!/usr/bin/env python
# coding: utf-8

# In[ ]:
#!/usr/bin/env python
# coding: utf-8
import requests
import json
import os
from datetime import datetime

carpeta_guardado = "Datos/EspirasTrafico"
os.makedirs(carpeta_guardado, exist_ok=True)  
fecha_actual = datetime.now().strftime("%d-%m-%Y")

url = "https://valencia.opendatasoft.com/api/records/1.0/search/"

params = {
    "dataset": "punts-mesura-trafic-espires-electromagnetiques-puntos-medida-trafico-espiras-ele",
    "rows": 100,  
    "start": 0  
}

todos_los_datos = []
while True:
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        records = data.get("records", [])
        
        if not records:
            break  

        todos_los_datos.extend(records)  
        params["start"] += params["rows"]  

        print(f"Descargados {len(todos_los_datos)} registros...")

    else:
        print(f"❌ Error al obtener los datos. Código: {response.status_code}")
        print(response.text)
        break

nombre_archivo = f"espiras_trafico_{fecha_actual}.json"
ruta_archivo = os.path.join(carpeta_guardado, nombre_archivo)
archivo_anterior = sorted([f for f in os.listdir(carpeta_guardado) if f.startswith("espiras_trafico_")], reverse=True)

if archivo_anterior:
    ruta_anterior = os.path.join(carpeta_guardado, archivo_anterior[0])
    with open(ruta_anterior, "r", encoding="utf-8") as f:
        datos_anteriores = json.load(f)
    
    if datos_anteriores == todos_los_datos:
        print("🔄 Los datos no han cambiado. No se guardará un nuevo archivo.")
    else:
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(todos_los_datos, f, indent=4, ensure_ascii=False)
        print(f"✅ Datos actualizados y guardados en '{ruta_archivo}'")
else:
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        json.dump(todos_los_datos, f, indent=4, ensure_ascii=False)
    print(f"✅ Datos descargados y guardados en '{ruta_archivo}'")