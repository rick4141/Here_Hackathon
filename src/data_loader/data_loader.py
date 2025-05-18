import os
import glob
import pandas as pd
import geopandas as gpd

def find_coord_columns(df: pd.DataFrame):
    """
    Detects possible latitude/longitude columns (Spanish and English).
    """
    lat_candidates = [c for c in df.columns if c.lower() in ("latitud", "latitude", "lat", "y")]
    lon_candidates = [c for c in df.columns if c.lower() in ("longitud", "longitude", "lon", "lng", "x")]
    return lat_candidates[0] if lat_candidates else None, lon_candidates[0] if lon_candidates else None

def load_pois(poi_dir, logger=None):
    """
    Loads all POI CSVs and concatenates them into a DataFrame.
    If there is a lat/lon, it creates a GeoDataFrame; if not, it returns a regular DataFrame.
    """
    files = glob.glob(os.path.join(poi_dir, "*.csv"))
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            if logger:
                logger.info(f"POI CSV loadind: {f}, filas: {len(df)}")
            df['source_file'] = os.path.basename(f)
            dfs.append(df)
        except Exception as e:
            if logger:
                logger.error(f"Error cargando {f}: {e}")
    if not dfs:
        return pd.DataFrame()
    result = pd.concat(dfs, ignore_index=True)
    lat, lon = find_coord_columns(result)
    if lat and lon:
        result = gpd.GeoDataFrame(result, geometry=gpd.points_from_xy(result[lon], result[lat]), crs="EPSG:4326")
        if logger:
            logger.info("POIs loaded as GeoDataFrame")
    return result

def load_streets(streets_dir, logger=None):
    """
    Loads all street GeoJSONs and concatenates them into a GeoDataFrame.
    """
    files = glob.glob(os.path.join(streets_dir, "*.geojson"))
    gdfs = []
    for f in files:
        try:
            gdf = gpd.read_file(f)
            if logger:
                logger.info(f"GeoJSON loaded from {f}: {len(gdf)} geometries")
            gdfs.append(gdf)
        except Exception as e:
            if logger:
                logger.error(f"Error loading {f}: {e}")
    if not gdfs:
        return gpd.GeoDataFrame()
    result = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    if logger:
        logger.info(f"Total geometries loaded with {streets_dir}: {len(result)}")
    return result

def load_any_csv(csv_file, logger=None):
    """
    Utility to load any flat CSV (for catalogs, lookups, etc.).
    """
    try:
        df = pd.read_csv(csv_file)
        if logger:
            logger.info(f"CSV cargado: {csv_file}, filas: {len(df)}")
        return df
    except Exception as e:
        if logger:
            logger.error(f"Error cargando CSV {csv_file}: {e}")
        return pd.DataFrame()
