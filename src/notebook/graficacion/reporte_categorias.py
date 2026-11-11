"""Reporte de la tabla categorias (HU G01): tres gráficas con matplotlib y conclusiones.

Lee data/limpio/categorias_limpio.csv, guarda las tres gráficas en reportes/ e
imprime las conclusiones.

Se puede ejecutar solo (python src/notebook/graficacion/reporte_categorias.py) o
importarse desde main.py con: from graficacion.reporte_categorias import generar_reporte
"""

import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Sin ventana: el script guarda las imágenes y no se queda esperando
import matplotlib.pyplot as plt
import pandas as pd

# src/notebook/graficacion/reporte_categorias.py -> sube 3 niveles hasta la raíz del proyecto
RAIZ = Path(__file__).resolve().parents[3]
RUTA_ENTRADA = RAIZ / "data" / "limpio" / "categorias_limpio.csv"
RUTA_CRUDO = RAIZ / "data" / "crudo" / "categorias_sucio.csv"
CARPETA_REPORTES = RAIZ / "reportes"


def cargar_datos(ruta):
    """Lee categorias_limpio.csv con pandas y calcula largo_desc si falta."""
    df = pd.read_csv(ruta)
    df.columns = [c.strip().lower() for c in df.columns]

    faltan = [c for c in ("id", "nombre", "descripcion", "area_responsable") if c not in df.columns]
    if faltan:
        sys.exit(f"Error: al archivo le faltan las columnas {faltan}. Columnas: {list(df.columns)}")

    if "largo_desc" not in df.columns:
        df["largo_desc"] = df["descripcion"].astype(str).str.len()
    df["largo_desc"] = pd.to_numeric(df["largo_desc"], errors="coerce")
    return df


def guardar_grafica(ruta):
    """Ajusta el diseño, guarda la figura actual con dpi=120 y la cierra."""
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()
    print(f"Gráfica guardada: {ruta}")


def grafica_conteo_categorias(df, carpeta):
    """Gráfica 1 (barras horizontales): cuántas veces aparece cada categoría."""
    conteo = df["nombre"].value_counts()
    plt.figure(figsize=(9, 5))
    conteo.plot(kind="barh")
    plt.title("Frecuencia de aparición por categoría")
    plt.xlabel("Cantidad de registros")
    plt.ylabel("Categoría")
    guardar_grafica(os.path.join(carpeta, "categorias_grafica_1.png"))
    return conteo


def grafica_por_area(df, carpeta):
    """Gráfica 2 (torta): reparto de categorías por área responsable."""
    por_area = df.groupby("area_responsable")["id"].count().sort_values(ascending=False)
    plt.figure(figsize=(8, 6))
    por_area.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Reparto de categorías por área responsable")
    plt.xlabel("Área responsable")
    plt.ylabel("Proporción")
    guardar_grafica(os.path.join(carpeta, "categorias_grafica_2.png"))
    return por_area


def grafica_largo_descripcion(df, carpeta):
    """Gráfica 3 (barras): largo promedio de la descripción por categoría."""
    largos = df.groupby("nombre")["largo_desc"].mean().round(1).sort_values(ascending=False)
    plt.figure(figsize=(9, 5))
    largos.plot(kind="bar")
    plt.title("Largo promedio de la descripción por categoría")
    plt.xlabel("Categoría")
    plt.ylabel("Largo promedio (caracteres)")
    plt.xticks(rotation=45)
    guardar_grafica(os.path.join(carpeta, "categorias_grafica_3.png"))
    return largos


def imprimir_conclusiones(df, ruta_crudo=RUTA_CRUDO):
    """Imprime las conclusiones finales del análisis de categorías."""
    print("\n=== CONCLUSIONES ===")

    filas_iniciales = 250
    if Path(ruta_crudo).exists():
        filas_iniciales = len(pd.read_csv(ruta_crudo))

    filas_limpias = len(df)
    eliminadas_duplicadas = filas_iniciales - filas_limpias
    categorias_reales = df["nombre"].nunique()
    eliminadas_catalogo = filas_iniciales - categorias_reales

    print(
        f"1. Filas eliminadas al quitar duplicados y variantes de escritura: "
        f"se eliminaron {eliminadas_duplicadas} filas duplicadas exactas (de {filas_iniciales} a {filas_limpias} filas), "
        f"y al consolidar las variantes de escritura en el catálogo único se redujeron {eliminadas_catalogo} filas repetidas "
        f"(de {filas_iniciales} registros a {categorias_reales} categorías únicas)."
    )
    print(
        f"2. Categorías REALES que quedaron al final: {categorias_reales} categorías únicas "
        f"({', '.join(sorted(df['nombre'].unique()))})."
    )
    print(
        "3. ¿Por qué el back debe declarar 'nombre' como ÚNICO (UNIQUE) y normalizarlo antes de guardar?: "
        "porque sin una restricción UNIQUE (y validación de mayúsculas/tildes/espacios en el backend), "
        "una misma categoría como 'Logistica' se inserta múltiples veces como 'LOGISTICA', ' logistica ' o 'logística', "
        "contaminando el catálogo, duplicando llaves foráneas y distorsionando los reportes y métricas por categoría."
    )


def generar_reporte(ruta_entrada=RUTA_ENTRADA, carpeta_reportes=CARPETA_REPORTES):
    """Crea las tres gráficas en reportes/ e imprime las conclusiones."""
    ruta_entrada = Path(ruta_entrada)
    if not ruta_entrada.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta_entrada}. Ejecuta primero la limpieza (HU L01)."
        )
    os.makedirs("reportes", exist_ok=True)
    carpeta_reportes = str(carpeta_reportes)
    os.makedirs(carpeta_reportes, exist_ok=True)

    df = cargar_datos(ruta_entrada)
    print(f"Filas leídas: {len(df)}")
    grafica_conteo_categorias(df, carpeta_reportes)
    grafica_por_area(df, carpeta_reportes)
    grafica_largo_descripcion(df, carpeta_reportes)
    imprimir_conclusiones(df)


if __name__ == "__main__":
    generar_reporte()

