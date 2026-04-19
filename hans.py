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
 # Carga y limpieza (igual que en tus códigos anteriores)

df_combined['Year'] = pd.to_numeric(df_combined['Year'], errors='coerce')
df_combined['Final Year'] = pd.to_numeric(df_combined['Final Year'], errors='coerce')
df_combined = df_combined.dropna(subset=['Year']).copy()
df_combined['Year'] = df_combined['Year'].astype(int)
df_combined['Decade'] = (df_combined['Year'] // 10) * 10
df_combined['Duration'] = df_combined['Final Year'] - df_combined['Year']


# Filtrar valores nulos de texto
df_combined = df_combined[df_combined['Main_Country'] != 'nan']

# Configuración visual global
sns.set_theme(style="whitegrid")
colores = sns.color_palette("husl", 10)

# ==========================================
# GRÁFICO 1: GRÁFICO DE MANCUERNAS
# ==========================================
# Filtrar las 15 más longevas y ordenarlas por año de estreno
long_df = df_combined.dropna(subset=['Title', 'Final Year', 'Year']).copy()
top_15_long = long_df.sort_values(by='Duration', ascending=False).head(15)
top_15_long = top_15_long.sort_values(by='Year', ascending=False)

fig10, ax10 = plt.subplots(figsize=(12, 8))
# 1. Dibujar las líneas de duración (Cuerpo de la mancuerna)
ax10.hlines(y=top_15_long['Title'], xmin=top_15_long['Year'], xmax=top_15_long['Final Year'], color='grey', alpha=0.5, linewidth=4)
# 2. Dibujar Año de Inicio
ax10.scatter(top_15_long['Year'], top_15_long['Title'], color='skyblue', s=100, label='Año de Estreno', zorder=3)
# 3. Dibujar Año de Finalización
ax10.scatter(top_15_long['Final Year'], top_15_long['Title'], color='red', s=100, label='Año Final', zorder=3)

# 4. Añadir la duración encima de cada mancuerna
for _, row in top_15_long.iterrows():
    mid_x = row['Year'] + (row['Final Year'] - row['Year']) / 2
    ax10.text(mid_x, row['Title'], str(int(row['Duration'])) + " años",
              ha='center', va='bottom', fontsize=9, fontweight='bold', color='black')

ax10.set_title('Línea de Vida de las 15 Series más Longevas', fontsize=15, fontweight='bold')
ax10.set_xlabel('Línea de Tiempo (Años)')
ax10.legend()
ax10.grid(True, axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('mancuernas.png', dpi=300)

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
print("1. 'mancuernas.png'")
print("2. 'burbuja.png'")