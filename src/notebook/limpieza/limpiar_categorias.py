"""Limpieza de la tabla categorias (HU L01 de Kaizen).

Lee data/crudo/categorias_sucio.csv, imprime el diagnóstico, corrige los errores,
imprime el diagnóstico otra vez, exporta el catálogo real (categorias_catalogo.csv)
y guarda data/limpio/categorias_limpio.csv.

Se puede ejecutar solo (python src/notebook/limpieza/limpiar_categorias.py) o importarse
desde main.py con: from limpieza.limpiar_categorias import limpiar_categorias
"""

from pathlib import Path

import pandas as pd

# src/notebook/limpieza/limpiar_categorias.py -> sube 3 niveles hasta la raíz del proyecto
RAIZ = Path(__file__).resolve().parents[3]
RUTA_ENTRADA = RAIZ / "data" / "crudo" / "categorias_sucio.csv"
RUTA_SALIDA = RAIZ / "data" / "limpio" / "categorias_limpio.csv"
RUTA_CATALOGO = RAIZ / "data" / "limpio" / "categorias_catalogo.csv"

# Columnas que no pueden quedar con nulos después de limpiar.
COLUMNAS_OBLIGATORIAS = ["id", "nombre", "descripcion", "area_responsable"]


def leer_csv(ruta):
    """Lee el CSV sucio con pandas y devuelve el DataFrame."""
    return pd.read_csv(ruta)


def imprimir_diagnostico(df, titulo):
    """Imprime shape, info, nulos por columna y cantidad de duplicados exactos."""
    print("=" * 60)
    print(titulo)
    print("=" * 60)
    print(f"df.shape: {df.shape}")
    print("\ndf.info():")
    df.info()
    print("\ndf.isna().sum():")
    print(df.isna().sum())
    print(f"\ndf.duplicated().sum(): {df.duplicated().sum()}\n")


def quitar_duplicados(df):
    """Elimina las filas duplicadas exactas."""
    return df.drop_duplicates()


def unificar_nombre(df):
    """Quita espacios, pasa a formato título y elimina tildes para unificar nombres."""
    df["nombre"] = df["nombre"].str.strip().str.title()
    df["nombre"] = (
        df["nombre"]
        .str.normalize("NFKD")
        .str.encode("ascii", "ignore")
        .str.decode("utf-8")
    )
    return df


def rellenar_nulos(df):
    """Rellena los valores nulos en descripcion y area_responsable."""
    df["descripcion"] = df["descripcion"].fillna("Sin descripcion")
    df["area_responsable"] = df["area_responsable"].fillna("Sin asignar")
    return df


def crear_largo_desc(df):
    """Crea la columna largo_desc con la longitud del texto de descripcion."""
    df["largo_desc"] = df["descripcion"].str.len()
    return df


def extraer_catalogo(df, ruta_catalogo=RUTA_CATALOGO):
    """Saca el catálogo real (una fila por categoría) y lo exporta como categorias_catalogo.csv."""
    catalogo = df.drop_duplicates(subset=["nombre"]).reset_index(drop=True)
    guardar_csv(catalogo, ruta_catalogo)
    print(f"Catálogo real de categorías: antes había {len(df)} filas y quedaron {len(catalogo)} categorías únicas.\n")
    return catalogo


def guardar_csv(df, ruta):
    """Crea la carpeta si hace falta y guarda el CSV en UTF-8 sin índice."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8")
    print(f"Archivo guardado en: {ruta}")


def limpiar_categorias(
    ruta_entrada=RUTA_ENTRADA,
    ruta_salida=RUTA_SALIDA,
    ruta_catalogo=None,
):
    """Ejecuta todo el proceso de limpieza y devuelve el DataFrame limpio."""
    ruta_entrada = Path(ruta_entrada)
    ruta_salida = Path(ruta_salida)
    if ruta_catalogo is None:
        ruta_catalogo = ruta_salida.parent / "categorias_catalogo.csv"
    else:
        ruta_catalogo = Path(ruta_catalogo)

    df = leer_csv(ruta_entrada)
    filas_iniciales = len(df)
    nulos_antes = df.isna().sum()
    imprimir_diagnostico(df, "DIAGNÓSTICO ANTES DE LIMPIAR")

    df = quitar_duplicados(df)
    df = unificar_nombre(df)
    df = rellenar_nulos(df)
    df = crear_largo_desc(df)
    # Unificar el nombre o rellenar nulos puede crear duplicados nuevos; se quitan para que no quede ninguno.
    df = quitar_duplicados(df)

    imprimir_diagnostico(df, "DIAGNÓSTICO DESPUÉS DE LIMPIAR")

    print("Nulos corregidos por columna (antes - después):")
    print((nulos_antes - df.isna().sum().reindex(nulos_antes.index)).to_string())
    print(f"\nFilas antes de limpiar: {filas_iniciales} | Filas después de limpiar: {len(df)}")
    print(f"Filas eliminadas: {filas_iniciales - len(df)} (de {filas_iniciales} a {len(df)})")

    obligatorias = [c for c in COLUMNAS_OBLIGATORIAS if c in df.columns]
    nulos_obl = df[obligatorias].isna().sum()
    if nulos_obl.sum() > 0:
        print("\nAVISO: quedan nulos en columnas obligatorias:")
        print(nulos_obl[nulos_obl > 0].to_string())
    else:
        print("\nOK: no quedan nulos en las columnas obligatorias ni duplicados exactos.")

    guardar_csv(df, ruta_salida)
    extraer_catalogo(df, ruta_catalogo)
    return df


if __name__ == "__main__":
    limpiar_categorias()

