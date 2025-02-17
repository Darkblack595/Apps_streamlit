def generar_mapa_top_10_municipios(df):
    """
    Genera un mapa de Colombia con los diez municipios con mayor movilización de madera.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de madera.
    """
    # Cargar el dataset de coordenadas de los municipios
    url_coordenadas = "https://github.com/Darkblack595/Apps_streamlit/raw/main/DIVIPOLA-_C_digos_municipios_geolocalizados_20250217.csv"
    df_coordenadas = pd.read_csv(url_coordenadas)
    
    # Convertir los nombres de los municipios a minúsculas en ambos datasets
    df['MUNICIPIO'] = df['MUNICIPIO'].str.lower()
    df_coordenadas['NOM_MPIO'] = df_coordenadas['NOM_MPIO'].str.lower()
    
    # Agrupar los volúmenes de madera por municipio
    vol_por_municipio = df.groupby('MUNICIPIO')['VOLUMEN M3'].sum().reset_index()
    
    # Ordenar y seleccionar los 10 municipios con mayor volumen
    top_10_municipios = vol_por_municipio.sort_values(by='VOLUMEN M3', ascending=False).head(10)
    
    # Unir los datos de los municipios con mayor volumen con las coordenadas
    top_10_municipios = top_10_municipios.merge(
        df_coordenadas,
        left_on='MUNICIPIO',
        right_on='NOM_MPIO',
        how='inner'
    )
    
    # Crear un GeoDataFrame con los municipios y sus coordenadas
    gdf = gpd.GeoDataFrame(
        top_10_municipios,
        geometry=gpd.points_from_xy(top_10_municipios['LONGITUD'], top_10_municipios['LATITUD'])
    )
    
    # Cargar el archivo GeoJSON de Colombia
    colombia = gpd.read_file('https://raw.githubusercontent.com/Ritz38/Analisis_maderas/refs/heads/main/Colombia.geo.json')
    
    # Crear la figura y el eje
    fig, ax = plt.subplots()
    
    # Graficar el mapa base de Colombia
    colombia.plot(ax=ax, color='lightgray', linewidth=0.8, edgecolor='k')
    
    # Graficar los 10 municipios con mayor volumen (círculos más pequeños)
    gdf.plot(ax=ax, color='red', markersize=50, edgecolor='k', label='Top 10 municipios')
    
    # Añadir etiquetas con el nombre del municipio (sin el volumen)
    for idx, row in gdf.iterrows():
        ax.text(
            x=row['LONGITUD'],
            y=row['LATITUD'],
            s=row['MUNICIPIO'].title(),  # Solo el nombre del municipio
            fontsize=6,  # Fuente más pequeña
            ha='center',
            va='center',
            color='black',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.1')  # Cuadros más pequeños
        )
    
    # Crear una leyenda con los nombres de los municipios
    legend_labels = [f"{row['MUNICIPIO'].title()}" for _, row in gdf.iterrows()]
    ax.legend(handles=[plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8)],
              labels=legend_labels,
              title="Municipios",
              loc='upper right',
              fontsize='small')
    
    # Establecer el título
    ax.set_title("Top 10 municipios con mayor movilización de madera")
    
    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)
