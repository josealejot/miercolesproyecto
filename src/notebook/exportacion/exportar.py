import os
import sys
from pathlib import Path

# Permite ejecutar este archivo directamente o importarlo desde main.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulacion.simular import generar_categorias

CARPETA = "data/crudo"


def exportar(df, carpeta=CARPETA):
    os.makedirs(carpeta, exist_ok=True)
    ruta_csv = os.path.join(carpeta, "categorias_sucio.csv")
    ruta_xlsx = os.path.join(carpeta, "categorias_sucio.xlsx")
    ruta_json = os.path.join(carpeta, "categorias_sucio.json")

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="categorias")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)
    return [ruta_csv, ruta_xlsx, ruta_json]


if __name__ == "__main__":
    df = generar_categorias()
    for ruta in exportar(df):
        print(ruta, df.shape)

