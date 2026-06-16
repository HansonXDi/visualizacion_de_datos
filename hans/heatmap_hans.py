import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LogNorm
import matplotlib.ticker as ticker
import urllib.request
import os

CSV_PATH = "animated_series_seasons_by_country.csv"
GEO_PATH = "countries.geojson"
GEO_URL  = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"

if not os.path.exists(GEO_PATH):
    print("Downloading world GeoJSON…")
    urllib.request.urlretrieve(GEO_URL, GEO_PATH)

df    = pd.read_csv(CSV_PATH)
world = gpd.read_file(GEO_PATH)

name_map = {
    "United States of America": "United States of America",
    "French Guiana": None,
    "Hong Kong":     None,
}
df["Country"] = df["Country"].replace({k: v for k, v in name_map.items() if v})
df = df[df["Country"].notna()]

merged = world.merge(df, left_on="name", right_on="Country", how="left")
merged["Total_Seasons"] = merged["Total_Seasons"].fillna(0)

fig, ax = plt.subplots(1, 1, figsize=(20, 10))
fig.patch.set_facecolor("#0f1117")
ax.set_facecolor("#0f1117")

no_data  = merged[merged["Total_Seasons"] == 0]
has_data = merged[merged["Total_Seasons"]  > 0]

no_data.plot(ax=ax, color="#2a2d3a", edgecolor="#1e2130", linewidth=0.3)

vmin, vmax = 1, merged["Total_Seasons"].max()
norm  = LogNorm(vmin=vmin, vmax=vmax)
cmap  = plt.cm.YlOrRd

has_data.plot(
    ax=ax,
    column="Total_Seasons",
    cmap=cmap,
    norm=norm,
    edgecolor="#1e2130",
    linewidth=0.3,
    missing_kwds={"color": "#2a2d3a"},
)

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(
    sm, ax=ax,
    orientation="horizontal",
    fraction=0.03, pad=0.02, aspect=40,
    shrink=0.5,
)
cbar.set_label("Series totales (escala logarítmica)", color="white", fontsize=11, labelpad=8)
cbar.ax.xaxis.set_tick_params(color="white")
plt.setp(cbar.ax.xaxis.get_ticklabels(), color="white", fontsize=9)
cbar.outline.set_edgecolor("white")

cbar.ax.xaxis.set_major_formatter(
    ticker.FuncFormatter(lambda x, _: f"{int(x):,}" if x >= 1 else "")
)

ax.set_title(
    "Total de temporadas por país",
    color="white", fontsize=18, fontweight="bold", pad=16,
)
ax.text(
    0.5, -0.04,
    "Fuentes: Animated series dataset (1948–2023)  •  Paises sin series se ven en gris",
    transform=ax.transAxes,
    ha="center", va="top", color="#8888aa", fontsize=8,
)
ax.axis("off")

plt.tight_layout()
out = "temporadas_por_pais.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved → {out}")
plt.show()
