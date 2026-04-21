import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# =====================================================================
# 1. CARGA Y LIMPIEZA DE DATOS
# =====================================================================

# Cargar archivos y unificar la columna del año de estreno
try:
    df1 = pd.read_csv('1948 - 1986.csv').rename(columns={'Premiere Year': 'Year'})
    df2 = pd.read_csv('1987 - 2022.csv').rename(columns={'Premiere Year': 'Year'})
    df3 = pd.read_csv('2023.csv').rename(columns={'Original channel': 'Original Channel'})
    
    # Concatenar todos los datos en un solo DataFrame
    df_combined = pd.concat([df1, df2, df3], ignore_index=True)
except FileNotFoundError as e:
    print(f"Error al cargar archivos: {e}. Asegúrate de que estén en la misma carpeta.")
    exit()

# Limpieza básica de la columna de Años
df_combined['Year'] = pd.to_numeric(df_combined['Year'], errors='coerce')
df_combined = df_combined.dropna(subset=['Year'])
df_combined['Year'] = df_combined['Year'].astype(int)

# Limpieza de Países
# Rellenar nulos y convertir a texto
df_combined['Country'] = df_combined['Country'].fillna('Unknown').astype(str)

# Unificar nomenclaturas comunes para evitar duplicados
df_combined['Country'] = df_combined['Country'].replace({
    'US': 'United States', 
    'USA': 'United States', 
    ' US' : 'United States',
    'US ' : 'United States',
    'USA ' : 'United States',
    ' USA' : 'United States',
    'U S' : 'United States',
    'UK': 'United Kingdom'
})

# Muchas series son coproducciones (ej. "United States, Canada").
# Aquí separamos esas listas y creamos una fila por cada país participante.
df_expanded = df_combined.assign(Country=df_combined['Country'].str.split(',')).explode('Country')
df_expanded['Country'] = df_expanded['Country'].str.strip() # Quitar espacios en blanco

# Obtener los 8 países con mayor cantidad de series producidas
top_countries = df_expanded['Country'].value_counts().head(8).index.tolist()

# Si 'Unknown' se coló en el top, lo sacamos y agregamos el siguiente en la lista
if 'Unknown' in top_countries:
    top_countries.remove('Unknown')
    top_countries.append(df_expanded['Country'].value_counts().index[8])

# dksajkghs
if 'US' in top_countries:
    top_countries.remove('US')
    top_countries.append(df_expanded['Country'].value_counts().index[8])

# Filtrar el DataFrame final solo con esos países top
df_top_countries = df_expanded[df_expanded['Country'].isin(top_countries)]

# =====================================================================
# 2. CREACIÓN DEL GRÁFICO NOVEDOSO: RIDGELINE PLOT
# =====================================================================

# Configurar el estilo visual base de Seaborn (fondo transparente para el efecto)
sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

# Crear una paleta de colores vibrante y distinta para cada país
paleta_colores = sns.color_palette("husl", len(top_countries))

# Inicializar un FacetGrid. Esto crea una fila de gráfico por cada país.
# aspect ajusta el ancho y height la altura de cada "cresta"
g = sns.FacetGrid(df_top_countries, row="Country", hue="Country", 
                  aspect=10, height=1.2, palette=paleta_colores)

# 2.1 - Dibujar el área rellena de color de la densidad de años
g.map(sns.kdeplot, "Year", bw_adjust=.5, clip_on=False, fill=True, alpha=0.8, linewidth=1.5)

# 2.2 - Dibujar un borde blanco grueso y luego uno negro delgado encima 
# para dar el efecto de sombra/relieve separando las "montañas"
g.map(sns.kdeplot, "Year", clip_on=False, color="white", lw=2, bw_adjust=.5)
g.map(sns.kdeplot, "Year", clip_on=False, color="black", lw=1, bw_adjust=.5)

# 2.3 - Añadir una línea horizontal negra sólida que sirva de "suelo" a cada país
g.map(plt.axhline, y=0, lw=2, clip_on=False, color='black')

# Función auxiliar para escribir el nombre del país encima de su curva respectiva
def label_country(x, color, label):
    ax = plt.gca() # Obtener el eje actual
    ax.text(0, .2, label, fontweight="bold", color=color,
            ha="left", va="center", transform=ax.transAxes, fontsize=12)

# Mapear la función a la cuadrícula
g.map(label_country, "Year")

# Ajustar el espacio vertical a un valor negativo para que las curvas se solapen (Efecto 3D)
g.figure.subplots_adjust(hspace=-0.4)

# Limpieza estética: quitar títulos por defecto de Seaborn, quitar marcas del eje Y y bordes
g.set_titles("")
g.set(yticks=[], ylabel="")
g.despine(bottom=True, left=True)

# Título general de la visualización
plt.suptitle('Evolución Histórica de la Producción de Series Animadas', 
             fontsize=18, fontweight='bold', y=0.98)

# Configurar el eje X con los años
plt.xlabel("Año de Estreno", fontsize=14, fontweight='bold', labelpad=20)

# =====================================================================
# 3. GUARDAR Y RENDERIZAR
# =====================================================================

# Guardar la imagen en alta resolución
plt.savefig('ridgeline_paises.png', dpi=300, bbox_inches='tight')
print("¡El gráfico ha sido generado y guardado exitosamente como 'ridgeline_paises.png'!")