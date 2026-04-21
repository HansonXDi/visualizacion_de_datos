import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# =================================================================
# 1. CARGA Y PREPARACIÓN DE DATOS
# =================================================================

# Cargamos los tres archivos
try:
    df1 = pd.read_csv('1948 - 1986.csv')
    df2 = pd.read_csv('1987 - 2022.csv')
    df3 = pd.read_csv('2023.csv')
    
    # Estandarizamos el nombre de la columna del año de estreno
    df1 = df1.rename(columns={'Premiere Year': 'Year'})
    df2 = df2.rename(columns={'Premiere Year': 'Year'})
    # El archivo 2023 ya usa 'Year'
    
    # Combinamos todos los datasets en uno solo
    df_full = pd.concat([df1, df2, df3], ignore_index=True, sort=False)
except FileNotFoundError:
    print("Error: Asegúrate de tener los archivos CSV en la misma carpeta que este script.")
    exit()

# Limpieza rápida: Estandarizar nombres de países (ej: US y United States)
def limpiar_pais(pais):
    if pd.isna(pais): return "Desconocido"
    # Tomamos solo el primer país si es una coproducción y limpiamos espacios
    p = str(pais).split(',')[0].strip().replace('"', '')
    mapping = {
        'US': 'USA', 'United States': 'USA', 'United Kingdom': 'UK',
        'Britain': 'UK', 'Soviet Union': 'Russia'
    }
    return mapping.get(p, p)

df_full['Country_Clean'] = df_full['Country'].apply(limpiar_pais)

# Obtenemos el conteo de series por país y seleccionamos el Top 20
data = df_full['Country_Clean'].value_counts().head(20).reset_index()
data.columns = ['Country', 'Count']
# Ordenamos de menor a mayor para que el espiral radial se vea armónico
data = data.sort_values(by='Count')

# =================================================================
# 2. CONFIGURACIÓN DEL GRÁFICO RADIAL (NOVEDOSO)
# =================================================================

# Parámetros básicos
labels = data['Country']
values = data['Count']
n_obs = len(data)

# Calculamos los ángulos para cada barra en el círculo
# Dejamos un espacio (gap) al final para que no se cierre el círculo completo
angles = np.linspace(0, 2 * np.pi, n_obs, endpoint=False)

# Configuración de la figura con proyección polar
plt.figure(figsize=(12, 12), facecolor='#f9f9f9')
ax = plt.subplot(111, polar=True)
ax.set_theta_offset(np.pi / 2) # Empezar desde arriba
ax.set_theta_direction(-1)     # Dirección de las agujas del reloj
ax.set_facecolor('#f9f9f9')

# Quitar cuadrículas y ejes estándar para un look limpio
ax.set_yticklabels([])
ax.set_xticklabels([])
ax.spines['polar'].set_visible(False)

# Colores: un degradado basado en la cantidad de series
colors = plt.cm.viridis(values / max(values))

# Dibujar las barras radiales
bars = ax.bar(angles, values, color=colors, alpha=0.9, width=0.2, edgecolor='white', linewidth=1)

# =================================================================
# 3. AÑADIR ETIQUETAS Y ESTILO
# =================================================================

# Añadir los nombres de los países y los valores
for angle, value, label in zip(angles, values, labels):
    # Rotación del texto para que sea legible
    rotation = np.rad2deg(angle)
    if angle >= np.pi:
        alignment = "right"
        rotation += 180
    else:
        alignment = "left"
    
    # Colocar el texto justo al final de cada barra
    ax.text(
        x=angle, y=value + 10, s=f"{label} ({value})", 
        ha=alignment, va='center', rotation=rotation, 
        rotation_mode="anchor", fontsize=10, fontweight='bold', color='#333333'
    )

# Título central estilizado
plt.title("Potencias Mundiales de la Animación\n", size=22, fontweight='bold', color='#2c3e50', pad=30)
plt.suptitle("Total de series producidas por país (1948 - 2023)", y=0.88, fontsize=12, color='#7f8c8d')

# Nota al pie
plt.figtext(0.5, 0.05, "Fuente: Análisis histórico de series de animación", ha="center", fontsize=9, color='gray')

# Guardar el resultado
plt.savefig('radial_animation_chart.png', dpi=300, bbox_inches='tight')
print("¡Gráfico radial generado con éxito como 'radial_animation_chart.png'!")