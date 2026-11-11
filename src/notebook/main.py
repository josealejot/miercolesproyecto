import sys
import traceback
from pathlib import Path

BASE = Path(__file__).resolve().parent


def buscar_codigo():
    """Devuelve la carpeta que contiene todas las carpetas de código."""
    candidatas = [BASE, BASE / "notebook", BASE / "src" / "notebook", BASE / "src"]
    carpetas = ("simulacion", "exportacion", "limpieza", "consultas", "graficacion")
    for carpeta in candidatas:
        if all((carpeta / n).is_dir() for n in carpetas):
            return carpeta
    raise FileNotFoundError(
        "No encontré las carpetas simulacion/, exportacion/, limpieza/, consultas/ y graficacion/. Busqué en:\n  "
        + "\n  ".join(str(c) for c in candidatas)
    )


def buscar_raiz():
    """Sube desde este archivo hasta la carpeta del proyecto (.venv, .git o raíz de src/notebook)."""
    for carpeta in [BASE, *BASE.parents]:
        if (
            (carpeta / ".venv").exists()
            or (carpeta / ".git").exists()
            or (carpeta / "src" / "notebook").is_dir()
        ):
            return carpeta
    return BASE


CODIGO = buscar_codigo()
RAIZ = buscar_raiz()
CARPETA_CRUDO = RAIZ / "data" / "crudo"
CARPETA_LIMPIO = RAIZ / "data" / "limpio"
CARPETA_REPORTES = RAIZ / "reportes"

sys.path.insert(0, str(CODIGO))

from simulacion.simular import generar_categorias
from exportacion.exportar import exportar
from limpieza.limpiar_categorias import limpiar_categorias
from consultas.consultar_categorias import ejecutar_consultas
from graficacion.reporte_categorias import generar_reporte


def main():
    print("Python:", sys.executable)
    print("Código en:", CODIGO)
    print("Raíz del proyecto:", RAIZ)

    # 1. Simulación (HU F01)
    df = generar_categorias(250)
    print("\n=== 1. Simulación ===")
    print("Forma:", df.shape)
    print(df.head())
    print("\nNulos por columna:")
    print(df.isna().sum())
    print("\nFilas duplicadas exactas:", df.duplicated().sum())

    # 2. Exportación (HU X01)
    print("\n=== 2. Exportación ===")
    rutas = exportar(df, carpeta=str(CARPETA_CRUDO))
    for ruta in rutas:
        print(f"{ruta} | shape={df.shape} | creado={Path(ruta).exists()}")

    # 3. Limpieza (HU L01): lee el CSV recién exportado
    print("\n=== 3. Limpieza ===")
    entrada = CARPETA_CRUDO / "categorias_sucio.csv"
    salida = CARPETA_LIMPIO / "categorias_limpio.csv"
    catalogo = CARPETA_LIMPIO / "categorias_catalogo.csv"
    df_limpio = limpiar_categorias(entrada, salida, catalogo)
    print(f"\ncategorias_limpio.csv | shape={df_limpio.shape} | creado={salida.exists()}")
    print(f"categorias_catalogo.csv | creado={catalogo.exists()}")

    # 4. Consultas (HU Q01): lee el CSV limpio y guarda categorias_consulta_N.csv
    print("\n=== 4. Consultas ===")
    ejecutar_consultas(salida, CARPETA_LIMPIO)

    # 5. Gráficas y conclusiones (HU G01): lee el CSV limpio y guarda PNG en reportes/
    print("\n=== 5. Gráficas ===")
    generar_reporte(salida, CARPETA_REPORTES)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
