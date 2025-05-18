import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from .interpolator import interpolate_point_on_line

def geocode_pois(pois_df: pd.DataFrame, streets_gdf: gpd.GeoDataFrame, logger=None) -> gpd.GeoDataFrame:
    """
    Geocodes POIs by interpolating over street segments.
    """
    geocoded = []
    for idx, poi in pois_df.iterrows():
        street_name = str(poi['st_name']).strip().upper()
        num_str = str(poi['st_num_ful']).replace('.0','').strip()
        try:
            poi_num = int(num_str)
        except:
            poi_num = np.nan

        # Search street segment
        segments = streets_gdf[streets_gdf['st_name'].str.upper().str.strip() == street_name]
        if segments.empty:
            geom = None
        else:
            # Search all segments and choose the first one that contains the number in its range
            geom = None
            for _, seg in segments.iterrows():
                min_num = seg['l_nrefaddr'] if seg['l_nrefaddr'] else seg['r_nrefaddr']
                max_num = seg['l_refaddr']  if seg['l_refaddr']  else seg['r_refaddr']
                # Treat fields as numbers
                try:
                    min_num, max_num = int(min_num), int(max_num)
                except:
                    continue
                if np.isnan(poi_num) or poi_num < min_num or poi_num > max_num:
                    continue
                geom = interpolate_point_on_line(seg.geometry, poi_num, min_num, max_num)
                if geom:
                    break
        row = poi.copy()
        row['geometry'] = geom if geom else None
        geocoded.append(row)
        if logger and idx % 1000 == 0:
            logger.info(f"{idx+1} POIs processed")
    return gpd.GeoDataFrame(geocoded, geometry='geometry', crs=streets_gdf.crs)
