import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from validation.validator import validate_pois
from validation.fixer import fix_pois

pois_df = pd.DataFrame([
    {'poi_id': 1, 'st_name': 'CALLE INEXISTENTE', 'link_id': 111, 'poi_name': 'POI A'},
    {'poi_id': 2, 'st_name': 'AVENIDA SOLIDARIDAD LAS TORRES', 'link_id': 999999, 'poi_name': 'POI B'},
    {'poi_id': 3, 'st_name': 'AVENIDA SOLIDARIDAD LAS TORRES', 'link_id': 939199332, 'poi_name': 'POI C'},
    {'poi_id': 4, 'st_name': 'CALLE INEXISTENTE', 'link_id': 222, 'poi_name': 'HOSPITAL Z'},
    {'poi_id': 5, 'st_name': 'AVENIDA SOLIDARIDAD LAS TORRES', 'link_id': 1296526969, 'poi_name': 'POI D'},
])
pois_df['poi_st_sd'] = None

streets_df = pd.DataFrame([
    {'st_name': 'AVENIDA SOLIDARIDAD LAS TORRES', 'link_id': 939199332, 'multiplydigit': 'N'},
    {'st_name': 'AVENIDA SOLIDARIDAD LAS TORRES', 'link_id': 1296526969, 'multiplydigit': 'Y'},
])

from validation.validator import validate_pois
from validation.fixer import fix_pois

val = validate_pois(pois_df, streets_df)
print(val[['poi_id', 'violation_code', 'violation_detail']])

fixed = fix_pois(val, pois_df, streets_df)
print(fixed)
