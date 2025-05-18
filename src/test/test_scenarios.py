# src/test/test_scenarios.py

import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from validation.validator import validate_pois
from validation.fixer import fix_pois

# Simulated small scenario dataset
pois_df = pd.DataFrame([
    # Scenario 1: Missing name (should be DELETE)
    {'poi_id': 1, 'poi_name': '', 'link_id': 1001, 'poi_st_sd': 'L', 'percfrref': 25},
    # Scenario 2: Wrong side (UPDATE_SIDE)
    {'poi_id': 2, 'poi_name': 'Valid POI', 'link_id': 999999, 'poi_st_sd': 'L', 'percfrref': 80},
    # Scenario 3: Multidigit Y but logic says should be N (FIX_MULTIDIGIT)
    {'poi_id': 3, 'poi_name': 'Multi POI', 'link_id': 2002, 'poi_st_sd': 'R', 'percfrref': 50},
    # Scenario 4: percfrref out of range (FIX_PERCFRREF)
    {'poi_id': 4, 'poi_name': 'OutOfRange', 'link_id': 2002, 'poi_st_sd': 'L', 'percfrref': 150},
    # Bonus: All correct
    {'poi_id': 5, 'poi_name': 'AllGood', 'link_id': 2002, 'poi_st_sd': 'L', 'percfrref': 25},
])

streets_df = pd.DataFrame([
    {'st_name': 'STREET A', 'link_id': 1001, 'multidigit': 'N'},
    {'st_name': 'STREET B', 'link_id': 2002, 'multidigit': 'Y'},
])

# VALIDATE
val = validate_pois(pois_df, streets_df)
print(val)

# FIX
fixed = fix_pois(val, pois_df, streets_df)
print(fixed[['poi_id', 'poi_name', 'link_id', 'poi_st_sd', 'percfrref']])
