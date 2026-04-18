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

# ==========================================
# GRÁFICO 1: MAPA DE CALOR (Décadas vs Top 10 Países)
# ==========================================
# Crear columna de década
df_combined['Decade'] = (df_combined['Year'] // 10) * 10
top_10_countries = df_combined['Main_Country'].value_counts().head(10).index
df_heatmap = df_combined[df_combined['Main_Country'].isin(top_10_countries)]

# Crear matriz pivot
heatmap_data = df_heatmap.pivot_table(index='Main_Country', columns='Decade', aggfunc='size', fill_value=0)
heatmap_data.columns = [f"{int(c)}s" for c in heatmap_data.columns] # Formato '1980s'

fig3, ax3 = plt.subplots(figsize=(12, 6))
sns.heatmap(heatmap_data, cmap='YlGnBu', annot=True, fmt='d', linewidths=.5, ax=ax3, cbar_kws={'label': 'Nº de Estrenos'})

ax3.set_title('Concentración de Estrenos por País y Década', fontsize=16, fontweight='bold', pad=15)
ax3.set_xlabel('Década', fontsize=12)
ax3.set_ylabel('País', fontsize=12)
plt.yticks(rotation=0)

plt.tight_layout()
fig3.savefig('mapa_calor.png', dpi=300)
plt.close(fig3)

# ==========================================
# GRÁFICO 2: BUBBLE CHART (Canales de TV)
# ==========================================
# Usa el área de los círculos para representar la importancia del canal.
# CORRECCIÓN: Se cambió 'df_total' por 'df_combined'
channels = df_combined['Original Channel'].str.split(',').explode().str.strip()
ch_counts = channels[~channels.isin(['Unknown', 'TBA', 'None'])].value_counts().head(20).reset_index()

plt.figure(figsize=(12, 7))
scatter = sns.scatterplot(data=ch_counts, x='Original Channel', y='count', size='count', 
                        sizes=(100, 3000), hue='count', legend=False)
plt.xticks(rotation=45, ha='right')
plt.title('Impacto de Canales de TV (Bubble Chart)', fontsize=14)
plt.ylabel('Cantidad de Series')
plt.tight_layout()
plt.savefig('burbuja.png')

print("¡Proceso terminado con éxito!")
print("Se han generado 2 gráficos, separados y adaptados a tus datos de series animadas:")
print("3. 'mapa_calor.png'")
print("4. 'burbuja.png'")