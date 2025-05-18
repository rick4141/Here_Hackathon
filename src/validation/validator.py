# src/validation/validator.py

import pandas as pd

def validate_pois(pois_gdf, streets_gdf, logger=None):
    """
    Validates each POI for rule violations based on scenarios.
    Returns a DataFrame listing POI IDs, violation codes, and detailed descriptions.
    """
    results = []
    for idx, poi in pois_gdf.iterrows():
        # 1. POI does not exist in reality (e.g., name missing/invalid)
        if pd.isna(poi.get('poi_name')) or (str(poi.get('poi_name')).strip() == ""):
            results.append({
                "poi_id": poi['poi_id'],
                "violation_code": "DELETE",
                "violation_detail": "POI missing or invalid (empty name)"
            })
            continue

        # 2. POI is on the wrong side of the street (link_id not found)
        street_row = streets_gdf[streets_gdf['link_id'] == poi['link_id']]
        if street_row.empty:
            results.append({
                "poi_id": poi['poi_id'],
                "violation_code": "UPDATE_SIDE",
                "violation_detail": "Street segment not found – possibly wrong side"
            })
            continue

        # 3. Multiply Digitised attribute is incorrect
        if 'multidigit' in street_row.columns:
            if str(street_row.iloc[0]['multidigit']).upper() == "Y":
                if not should_be_multidigit(poi, street_row.iloc[0]):
                    results.append({
                        "poi_id": poi['poi_id'],
                        "violation_code": "FIX_MULTIDIGIT",
                        "violation_detail": "Multiply Digitised should be N"
                    })
                    continue

        # 4. percfrref out of range (bonus critical attribute)
        if 'percfrref' in poi and (pd.notna(poi['percfrref'])):
            try:
                perc = float(poi['percfrref'])
                if perc < 0 or perc > 100:
                    results.append({
                        "poi_id": poi['poi_id'],
                        "violation_code": "FIX_PERCFRREF",
                        "violation_detail": "percfrref out of range, should be 0-100"
                    })
                    continue
            except Exception:
                results.append({
                    "poi_id": poi['poi_id'],
                    "violation_code": "FIX_PERCFRREF",
                    "violation_detail": "percfrref not a number"
                })
                continue


        # 5. Legitimate Exception (all correct)
        results.append({
            "poi_id": poi['poi_id'],
            "violation_code": "LEGIT_EXCEPTION",
            "violation_detail": "POI passes all validation rules"
        })

    validation_results = pd.DataFrame(results)
    if logger:
        logger.info(f"Validated {len(validation_results)} POIs.")
    return validation_results

def should_be_multidigit(poi, street_row):
    """
    For demo purposes: you can implement your rule.
    Here we return False always (to trigger fix), but in a real scenario,
    you should check your POI/street data logic.
    """
    return False
