"""HU Q01 - Consultas sobre la tabla categorias con pandas.

Lee data/limpio/categorias_limpio.csv (el archivo LIMPIO, no el sucio), responde
cinco consultas (cada una en su propia función), imprime el título y el
resultado de cada una en orden y guarda data/limpio/categorias_consulta_N.csv.

Se puede ejecutar solo (python src/notebook/consultas/consultar_categorias.py) o
importarse desde main.py con: from consultas.consultar_categorias import ejecutar_consultas
"""

from pathlib import Path

import pandas as pd

# src/notebook/consultas/consultar_categorias.py -> sube 3 niveles hasta la raíz del proyecto
RAIZ = Path(__file__).resolve().parents[3]
CARPETA_LIMPIO = RAIZ / "data" / "limpio"
RUTA_ENTRADA = CARPETA_LIMPIO / "categorias_limpio.csv"


def cargar_datos(ruta):
    """Lee el CSV limpio de categorías."""
    df = pd.read_csv(ruta)
    return df


def guardar(resultado, carpeta, numero):
    """Guarda el resultado de la consulta N como categorias_consulta_N.csv."""
    ruta = Path(carpeta) / f"categorias_consulta_{numero}.csv"
    resultado.to_csv(ruta, index=True if resultado.index.name else False, encoding="utf-8")
    return ruta


def consulta_1(df, carpeta):
    """Consulta 1: cuántas veces aparece cada categoría."""
    print("\n=== Consulta 1: ¿Cuántas veces aparece cada categoría? ===")
    conteo = df["nombre"].value_counts().rename("cantidad")
    conteo.index.name = "nombre"
    print(conteo.to_string())
    guardar(conteo, carpeta, 1)
    return conteo


def consulta_2(df, carpeta):
    """Consulta 2: categorías sin descripción."""
    print("\n=== Consulta 2: ¿Qué registros de categorías no tenían descripción? ===")
    sin_desc = df[df["descripcion"] == "Sin descripcion"]
    print(sin_desc.to_string(index=False))
    guardar(sin_desc, carpeta, 2)
    return sin_desc


def consulta_3(df, carpeta):
    """Consulta 3 (groupby): largo promedio de la descripción por categoría."""
    print("\n=== Consulta 3: ¿Cuál es el largo promedio de la descripción por categoría? ===")
    largos = df.groupby("nombre")["largo_desc"].mean().round(1).sort_values(ascending=False)
    largos = largos.rename("largo_promedio")
    largos.index.name = "nombre"
    print(largos.to_string())
    guardar(largos, carpeta, 3)
    return largos


def consulta_4(df, carpeta):
    """Consulta 4 (groupby): cuántas categorías maneja cada área."""
    print("\n=== Consulta 4: ¿Cuántas categorías maneja cada área responsable? ===")
    por_area = df.groupby("area_responsable")["id"].count().sort_values(ascending=False)
    por_area = por_area.rename("cantidad")
    por_area.index.name = "area_responsable"
    print(por_area.to_string())
    guardar(por_area, carpeta, 4)
    return por_area


def consulta_5(df, carpeta):
    """Consulta 5 (groupby doble): categorías por área responsable (tabla cruzada)."""
    print("\n=== Consulta 5: ¿Cómo se distribuyen las categorías por área responsable (tabla cruzada)? ===")
    tabla = df.groupby(["area_responsable", "nombre"])["id"].count().unstack(fill_value=0)
    print(tabla.to_string())
    guardar(tabla, carpeta, 5)
    return tabla


def ejecutar_consultas(ruta_entrada=RUTA_ENTRADA, carpeta_salida=CARPETA_LIMPIO):
    """Carga los datos limpios y corre las cinco consultas en orden."""
    ruta_entrada = Path(ruta_entrada)
    if not ruta_entrada.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta_entrada}. Ejecuta primero la limpieza (HU L01)."
        )
    carpeta_salida = Path(carpeta_salida)
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    df = cargar_datos(ruta_entrada)

    consulta_1(df, carpeta_salida)
    consulta_2(df, carpeta_salida)
    consulta_3(df, carpeta_salida)
    consulta_4(df, carpeta_salida)
    consulta_5(df, carpeta_salida)

    print(f"\nListo: se guardaron categorias_consulta_1.csv ... categorias_consulta_5.csv en {carpeta_salida}")


if __name__ == "__main__":
    ejecutar_consultas()

