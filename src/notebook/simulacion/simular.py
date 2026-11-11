import random
import uuid

import pandas as pd
from faker import Faker

# 1. Configuración del faker y semillas fijas (reproducibilidad)
fake = Faker("es_CO")
Faker.seed(42)
random.seed(42)

# 2. Constantes: 10 categorías reales y áreas responsables
CATEGORIAS = [
    "Logistica",
    "Tecnologia",
    "Innovacion",
    "Sostenibilidad",
    "Finanzas",
    "Talento Humano",
    "Marketing",
    "Operaciones",
    "Calidad",
    "Servicio Al Cliente",
]

AREAS = [
    "Direccion General",
    "TI y Sistemas",
    "Recursos Humanos",
    "Operaciones y Logistica",
    "Comercial y Ventas",
    "Finanzas y Contabilidad",
]

# Variantes con tilde para ensuciar nombres de categorías
CON_TILDE = {
    "Logistica": "logística",
    "Tecnologia": "tecnología",
    "Innovacion": "innovación",
}


def _muestra(df, porcentaje):
    """Índices de un porcentaje de filas tomadas al azar."""
    return df.sample(frac=porcentaje, random_state=random.randint(0, 999)).index


def _generar_limpios(n):
    filas = []
    for _ in range(n):
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": random.choice(CATEGORIAS),
            "descripcion": fake.sentence(nb_words=8),
            "area_responsable": random.choice(AREAS),
        })
    return pd.DataFrame(filas)


def _ensuciar(df):
    df = df.copy()

    # nombre: variantes de escritura ('Logistica', 'LOGISTICA', ' logistica ', 'logística', etc.)
    idx_mayus = _muestra(df, 0.15)
    df.loc[idx_mayus, "nombre"] = df.loc[idx_mayus, "nombre"].str.upper()

    idx_espacios = _muestra(df, 0.15)
    df.loc[idx_espacios, "nombre"] = " " + df.loc[idx_espacios, "nombre"].str.lower() + " "

    idx_tilde = _muestra(df, 0.15)
    df.loc[idx_tilde, "nombre"] = df.loc[idx_tilde, "nombre"].map(
        lambda x: CON_TILDE.get(x.strip().title(), x.lower())
    )

    # Garantizar explícitamente las variantes 'Logistica', 'LOGISTICA', ' logistica ', 'logística'
    variantes_logistica = ["Logistica", "LOGISTICA", " logistica ", "logística"]
    for i, var in enumerate(variantes_logistica):
        if i < len(df):
            df.loc[i, "nombre"] = var

    # descripcion: 15% en None (nulos)
    df.loc[_muestra(df, 0.15), "descripcion"] = None

    # area_responsable: 10% en None (nulos)
    df.loc[_muestra(df, 0.10), "area_responsable"] = None

    # 8% de las filas repetidas tal cual (duplicados exactos, total = n)
    n_dup = int(len(df) * 0.08)
    destinos = set(random.sample(range(len(df)), n_dup))
    origenes = [i for i in range(len(df)) if i not in destinos]
    for d in sorted(destinos):
        df.iloc[d] = df.iloc[random.choice(origenes)]

    return df.reset_index(drop=True)


def generar_categorias(n=250):
    """Genera n categorías ya ensuciadas y devuelve el DataFrame."""
    Faker.seed(42)
    random.seed(42)
    df = _ensuciar(_generar_limpios(n))
    return df


if __name__ == "__main__":
    df = generar_categorias()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())
