# src/preprocessing/normalizer.py

import geopandas as gpd
import pandas as pd
import logging

def normalize_pois(df: pd.DataFrame, logger: logging.Logger = None) -> gpd.GeoDataFrame:
    """
    Estandariza columnas de POIs y prepara para geocodificación.
    No crea geometría aquí, solo normaliza nombres y limpia nulos/duplicados.
    """
    # Estandarizar nombres a minúsculas y quitar espacios
    df = df.rename(columns={c: c.strip().lower().replace(" ", "_") for c in df.columns})
    if logger:
        logger.info(f"Columnas estandarizadas: {list(df.columns)}")

    # (Opcional) Eliminar duplicados o nulos relevantes
    df = df.drop_duplicates()
    df = df.dropna(subset=["st_name"])  # Solo si lo requieres para la geocodificación

    # Regresa DataFrame para geocodificación posterior
    return df

def normalize_streets(gdf: gpd.GeoDataFrame, logger: logging.Logger = None, target_crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """
    Normaliza un GeoDataFrame de calles:
    - Estandariza columnas
    - Reproyecta a WGS84 (EPSG:4326) por defecto
    - Limpia geometrías inválidas
    """
    gdf = gdf.rename(columns={c: c.strip().lower().replace(" ", "_") for c in gdf.columns})
    if logger:
        logger.info(f"Columnas estandarizadas en calles: {list(gdf.columns)}")

    # Limpia geometrías inválidas
    if not gdf.empty and (~gdf.is_valid).any():
        gdf = gdf[gdf.is_valid]
        if logger:
            logger.info(f"Calles inválidas eliminadas")

    # Reproyecta
    if gdf.crs is None or gdf.crs.to_string() != target_crs:
        gdf = gdf.to_crs(target_crs)
        if logger:
            logger.info(f"Calles reproyectadas a {target_crs}")

    return gdf
