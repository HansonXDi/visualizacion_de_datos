import pandas as pd
import matplotlib.pyplot as plt
import math
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
# GRÁFICO 2: GRÁFICO RADIAL
# ==========================================

# 1. Crear explícitamente la columna 'Decade' usando el Año
df_combined['Decade'] = (df_combined['Year'] // 10) * 10

# 2. Identificar la columna de estilo/técnica de animación de forma dinámica
col_estilo = 'Technique' # Valor por defecto
for col in ['Animation technique', 'Animation Technique', 'Technique', 'Style']:
    if col in df_combined.columns:
        col_estilo = col
        break

# 3. Filtrar nulos para evitar errores (ahora 'Decade' seguro existe)
df_radar = df_combined.dropna(subset=[col_estilo, 'Decade']).copy()

# Obtener décadas disponibles y ordenarlas
decadas = sorted(df_radar['Decade'].unique())

# Configurar la grilla de subplots (ej. 3 columnas)
n_cols = 3
n_rows = math.ceil(len(decadas) / n_cols)

# Crear la figura con proyección polar (radial)
fig3, axes = plt.subplots(n_rows, n_cols, figsize=(15, 6 * n_rows), subplot_kw={'projection': 'polar'})
# Asegurar que axes sea iterable incluso si es un solo subplot
if n_rows * n_cols == 1:
    axes = [axes]
else:
    axes = axes.flatten()

# --- AQUÍ SE AGREGA EL TÍTULO GLOBAL EN GRANDE ---
fig3.suptitle('EVOLUCIÓN E IMPACTO DE LOS ESTILOS DE ANIMACIÓN POR DÉCADA', 
               fontsize=24, fontweight='bold', color='navy', y=0.95)

# Colores para los gráficos
color_radar = sns.color_palette("husl", len(decadas))

for i, decada in enumerate(decadas):
    ax = axes[i]
    
    # Filtrar datos por la década actual
    datos_decada = df_radar[df_radar['Decade'] == decada]
    
    # Obtener el Top 5 de estilos de animación para esta década
    top_5 = datos_decada[col_estilo].value_counts().head(5)
    
    # Si una década tiene muy pocos o ningún dato, la saltamos
    if len(top_5) < 3: 
        ax.set_title(f'{int(decada)}s\n(Datos insuficientes)', size=12, fontweight='bold', position=(0.5, 1.1))
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        continue
        
    categorias = top_5.index.astype(str).tolist()
    valores = top_5.values.tolist()
    
    # Para cerrar el polígono del gráfico radial, repetir el primer valor al final
    categorias += [categorias[0]]
    valores += [valores[0]]
    
    # Calcular los ángulos para cada eje (atributo)
    angulos = np.linspace(0, 2 * np.pi, len(categorias) - 1, endpoint=False).tolist()
    angulos += [angulos[0]] # Cerrar el círculo
    
    # Dibujar la línea y rellenar el área
    ax.plot(angulos, valores, color=color_radar[i], linewidth=2, linestyle='solid')
    ax.fill(angulos, valores, color=color_radar[i], alpha=0.3)
    
    # Ajustar etiquetas de los ejes (categorías)
    ax.set_xticks(angulos[:-1])
    # Envolver textos largos para que no se superpongan
    etiquetas_formateadas = [cat.replace(' ', '\n') if len(cat) > 10 else cat for cat in categorias[:-1]]
    ax.set_xticklabels(etiquetas_formateadas, fontsize=10)
    
    # Ocultar las etiquetas de los valores numéricos concéntricos
    ax.set_yticklabels([]) 
    
    # Título de cada subplot
    ax.set_title(f'Década: {int(decada)}s', size=14, fontweight='bold', position=(0.5, 1.1))

# Ocultar los subplots sobrantes si la cuadrícula es mayor a la cantidad de décadas
for j in range(len(decadas), len(axes)):
    axes[j].set_visible(False)
fig3.set
plt.tight_layout(pad=3.0)
fig3.savefig('radial.png', dpi=300)
plt.close(fig3)



print("¡Proceso terminado con éxito!")
print("Se han generado 2 gráficos, separados y adaptados a tus datos de series animadas:")
print("1. 'area_apilada.png'")
print("2. 'radial.png'")