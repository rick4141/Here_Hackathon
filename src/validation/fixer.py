# src/validation/fixer.py

def fix_pois(validation_results, pois_gdf, streets_gdf, logger=None):
    """
    Automatically applies corrections to POIs and street segments, based on validation codes.
    Returns the updated POIs dataframe.
    """
    pois_fixed = pois_gdf.copy()

    for _, row in validation_results.iterrows():
        idx = pois_fixed.index[pois_fixed['poi_id'] == row['poi_id']]
        if row['violation_code'] == "DELETE":
            pois_fixed = pois_fixed.drop(idx)
        elif row['violation_code'] == "UPDATE_SIDE":
            if not idx.empty and 'poi_st_sd' in pois_fixed.columns:
                old_val = pois_fixed.at[idx[0], 'poi_st_sd']
                pois_fixed.at[idx[0], 'poi_st_sd'] = 'R' if old_val == 'L' else 'L'
        elif row['violation_code'] == "FIX_MULTIDIGIT":
            if not idx.empty and 'percfrref' in pois_fixed.columns:
                value = pois_fixed.at[idx[0], 'percfrref']
                try:
                    value = float(value)
                    if value < 0 or value > 100:
                        pois_fixed.at[idx[0], 'percfrref'] = 50
                except Exception:
                    pois_fixed.at[idx[0], 'percfrref'] = 50
            link_id = pois_fixed.at[idx[0], 'link_id']
            street_idx = streets_gdf.index[streets_gdf['link_id'] == link_id]
            if not street_idx.empty and 'multiplydigit' in streets_gdf.columns:
                streets_gdf.at[street_idx[0], 'multiplydigit'] = 'N'
        # LEGIT_EXCEPTION means no change needed

    if logger:
        logger.info(f"Automatic corrections applied. Final POIs: {len(pois_fixed)}")
    return pois_fixed

