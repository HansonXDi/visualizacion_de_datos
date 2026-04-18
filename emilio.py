import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --- 1. Carga y Procesamiento de Datos ---

# Cargar archivos y unificar el nombre de la columna del año de estreno
try:
    df1 = pd.read_csv('1948 - 1986.csv').rename(columns={'Premiere Year': 'Year'})
    df2 = pd.read_csv('1987 - 2022.csv').rename(columns={'Premiere Year': 'Year'})
    df3 = pd.read_csv('2023.csv').rename(columns={'Original channel': 'Original Channel'})
    
    # Concatenar todos los datos
    df_combined = pd.concat([df1, df2, df3], ignore_index=True)
except FileNotFoundError as e:
    print(f"Error al cargar archivos: {e}. Asegúrate de que estén en la misma carpeta.")
    exit()

# Limpieza básica de Años
df_combined['Year'] = pd.to_numeric(df_combined['Year'], errors='coerce')
df_combined = df_combined.dropna(subset=['Year'])
df_combined['Year'] = df_combined['Year'].astype(int)

# Limpieza de Países (Unificar nombres como US y United States)
df_combined['Country'] = df_combined['Country'].astype(str)
# Tomar solo el primer país si hay coproducciones (separadas por coma) para simplificar
df_combined['Main_Country'] = df_combined['Country'].apply(lambda x: x.split(',')[0].strip().replace('"', ''))
# Estandarizar nombres
df_combined['Main_Country'] = df_combined['Main_Country'].replace({
    'US': 'United States', 
    'UK': 'United Kingdom', 
    'Britain': 'United Kingdom'
})

# Filtrar valores nulos de texto
df_combined = df_combined[df_combined['Main_Country'] != 'nan']

# Configuración visual global
sns.set_theme(style="whitegrid")
colores = sns.color_palette("husl", 10)

# --- 2. Generación de Gráficos ---

# ==========================================
# GRÁFICO 1: ÁREA APILADA (Evolución Top 5 Países)
# ==========================================
top_5_countries = df_combined['Main_Country'].value_counts().head(5).index
df_top5 = df_combined[df_combined['Main_Country'].isin(top_5_countries)]

# Agrupar por año y país
data_area = df_top5.groupby(['Year', 'Main_Country']).size().unstack(fill_value=0)
# Suavizar un poco los datos agrupando por cada 2 años para que el gráfico no sea tan ruidoso
data_area = data_area.groupby(data_area.index // 2 * 2).sum()

fig1, ax1 = plt.subplots(figsize=(12, 7))
data_area.plot(kind='area', stacked=True, ax=ax1, alpha=0.8, color=colores[:5])

ax1.set_title('Evolución de Estrenos de Series Animadas (Top 5 Países)', fontsize=16, fontweight='bold', pad=15)
ax1.set_xlabel('Año de Estreno', fontsize=12)
ax1.set_ylabel('Cantidad de Series', fontsize=12)
ax1.set_xlim(data_area.index.min(), 2023)
ax1.legend(title='País', loc='upper left')

plt.tight_layout()
fig1.savefig('area_apilada.png', dpi=300)
plt.close(fig1)

# ==========================================
# GRÁFICO 2: GRÁFICO DE COYAC VIVA CHILE (Top 15 Países Histórico)
# ==========================================
top_15_counts = df_combined['Main_Country'].value_counts().head(15)

fig2, ax2 = plt.subplots(figsize=(12, 8))
# Ordenar de menor a mayor para que el más grande quede arriba
top_15_counts = top_15_counts.sort_values() 

# Dibujar las líneas (palitos)
ax2.hlines(y=top_15_counts.index, xmin=0, xmax=top_15_counts.values, color='skyblue', alpha=0.8, linewidth=3)
# Dibujar los puntos (caramelos)
ax2.scatter(top_15_counts.values, top_15_counts.index, color='navy', s=100, alpha=0.9, zorder=2)

ax2.set_title('Top 15 Países Productores de Series Animadas Históricos', fontsize=16, fontweight='bold', pad=15)
ax2.set_xlabel('Total de Series Producidas', fontsize=12)
ax2.set_ylabel('País', fontsize=12)

# Añadir las etiquetas de datos al lado de las burbujas
for i, v in enumerate(top_15_counts.values):
    ax2.text(v + 15, i, str(v), color='black', va='center', fontweight='bold', fontsize=10)

plt.tight_layout()
fig2.savefig('coyac.png', dpi=300)
plt.close(fig2)


print("¡Proceso terminado con éxito!")
print("Se han generado 2 gráficos, separados y adaptados a tus datos de series animadas:")
print("1. 'area_apilada.png'")
print("2. 'coyac.png'")