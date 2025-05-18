# src/preprocessing/normalizer.py

import geopandas as gpd
import pandas as pd
import logging

def normalize_pois(df: pd.DataFrame, logger: logging.Logger = None) -> gpd.GeoDataFrame:
    """
    Standardizes POI columns and prepares for geocoding.
    It doesn't create geometry here; it just normalizes names and cleans up nulls/duplicates.
    """
    # Standardize names to lowercase and remove spaces
    df = df.rename(columns={c: c.strip().lower().replace(" ", "_") for c in df.columns})
    if logger:
        logger.info(f"Standardized columns: {list(df.columns)}")

    # (Optional) Remove relevant duplicates or nulls
    df = df.drop_duplicates()
    df = df.dropna(subset=["st_name"]) 

    # Returns DataFrame for further geocoding
    return df

def normalize_streets(gdf: gpd.GeoDataFrame, logger: logging.Logger = None, target_crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """
    Normalize a GeoDataFrame of streets:
    - Standardize columns
    - Reproject to WGS84 (EPSG:4326) by default
    - Clean up invalid geometries
    """
    gdf = gdf.rename(columns={c: c.strip().lower().replace(" ", "_") for c in gdf.columns})
    if logger:
        logger.info(f"Standardized columns in streets: {list(gdf.columns)}")

    # Clean invalid geometries
    if not gdf.empty and (~gdf.is_valid).any():
        gdf = gdf[gdf.is_valid]
        if logger:
            logger.info(f"Invalid streets removed")

    # Reproject
    if gdf.crs is None or gdf.crs.to_string() != target_crs:
        gdf = gdf.to_crs(target_crs)
        if logger:
            logger.info(f"Streets reprojected to {target_crs}")

    return gdf
