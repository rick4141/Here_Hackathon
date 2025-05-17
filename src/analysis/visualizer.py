# src/analysis/visualizer.py
import geopandas as gpd
import matplotlib.pyplot as plt
import os

def plot_pois_map(pois_gdf: gpd.GeoDataFrame, output_dir="output", filename="pois_map.png"):
    os.makedirs(output_dir, exist_ok=True)
    ax = pois_gdf.plot(figsize=(12, 8), marker='o', color='red', alpha=0.5)
    plt.title("POIs Geocodificados")
    plt.savefig(os.path.join(output_dir, filename))
    plt.close()
