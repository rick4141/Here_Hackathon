import os
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Point
from utils.logger import get_logger

logger = get_logger(__name__)

def interpolate_point_on_line(line: LineString, num: float, num_start: float, num_end: float) -> Point:
    if num_end == num_start:
        return line.interpolate(0.5, normalized=True)
    t = (num - num_start) / (num_end - num_start)
    t = np.clip(t, 0, 1)
    return line.interpolate(t, normalized=True)

def enrich_pois_geometry(pois_df: pd.DataFrame, naming_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    naming_gdf = naming_gdf.copy()
    naming_gdf.columns = naming_gdf.columns.str.lower().str.strip()
    pois_df = pois_df.copy()
    pois_df['geometry'] = None

    for idx, row in pois_df.iterrows():
        street = str(row.get('st_name') or '').strip().upper()
        num = row.get('st_num_ful')
        if pd.isna(street) or pd.isna(num):
            continue
        segs = naming_gdf[naming_gdf['st_name'].str.strip().str.upper() == street]
        if segs.empty:
            continue
        found = False
        for _, seg in segs.iterrows():
            for side, (n1, n2) in [('L', (seg.get('l_nrefaddr'), seg.get('l_refaddr'))),
                                   ('R', (seg.get('r_nrefaddr'), seg.get('r_refaddr')))]:
                if pd.isna(n1) or pd.isna(n2):
                    continue
                try:
                    n1, n2 = float(n1), float(n2)
                    num_f = float(num)
                except Exception:
                    continue
                min_addr, max_addr = sorted([n1, n2])
                if min_addr <= num_f <= max_addr:
                    geom = interpolate_point_on_line(seg.geometry, num_f, min_addr, max_addr)
                    pois_df.at[idx, 'geometry'] = geom
                    found = True
                    break
            if found:
                break
    gdf = gpd.GeoDataFrame(pois_df, geometry='geometry', crs=naming_gdf.crs or 'EPSG:4326')
    logger.info(f"POIs geocodificados: {gdf['geometry'].notnull().sum()} de {len(gdf)}")
    return gdf
