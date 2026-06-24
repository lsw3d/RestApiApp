# DEM data

GeoTIFF files in `dem/` are not committed to git (see `.gitignore`).

Download elevation data for the Crimea south coast region:

```bash
python scripts/download_dem.py
```

Output: `data/dem/crimea_south.tif` (Copernicus DEM GLO-30, clipped to bbox).

Coverage: `44.30°N–44.55°N`, `33.90°E–34.20°E` (Yalta — Ai-Petri — Foros).
