def especies_menor_volumen_distribucion(df):
    """
    Identifica las especies de madera con menor volumen movilizado y analiza su distribución geográfica
    utilizando puntos de colores en el mapa de Colombia, donde cada color representa una especie.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de madera.
    """
    st.subheader("Especies con menor volumen movilizado y su distribución geográfica")
    
    # Agrupar por especie y calcular el volumen total movilizado
    df_agrupado_especies = df.groupby('ESPECIE')['VOLUMEN M3'].sum().reset_index()
    
    # Ordenar por volumen (de menor a mayor) y seleccionar las 10 especies con menor volumen
    df_menor_volumen = df_agrupado_especies.sort_values(by='VOLUMEN M3', ascending=True).head(10)
    
    # Mostrar las especies con menor volumen
    st.write("### Especies con menor volumen movilizado:")
    st.dataframe(df_menor_volumen)
    
    # Filtrar el DataFrame para incluir solo las especies con menor volumen
    df_filtrado = df[df['ESPECIE'].isin(df_menor_volumen['ESPECIE'])]
    
    # Cargar el dataset de coordenadas de los municipios
    url_coordenadas = "https://github.com/Darkblack595/Apps_streamlit/raw/main/DIVIPOLA-_C_digos_municipios_geolocalizados_20250217.csv"
    df_coordenadas = pd.read_csv(url_coordenadas)
    
    # Convertir los nombres de los municipios a minúsculas en ambos datasets
    df_filtrado['MUNICIPIO'] = df_filtrado['MUNICIPIO'].str.lower()
    df_coordenadas['NOM_MPIO'] = df_coordenadas['NOM_MPIO'].str.lower()
    
    # Unir los datos de los municipios con las coordenadas
    df_municipios_coordenadas = df_filtrado.merge(
        df_coordenadas,
        left_on='MUNICIPIO',
        right_on='NOM_MPIO',
        how='inner'
    )
    
    # Crear un GeoDataFrame con los municipios y sus coordenadas
    gdf = gpd.GeoDataFrame(
        df_municipios_coordenadas,
        geometry=gpd.points_from_xy(df_municipios_coordenadas['LONGITUD'], df_municipios_coordenadas['LATITUD'])
    )
    
    # Cargar el archivo GeoJSON de Colombia
    colombia = gpd.read_file('https://raw.githubusercontent.com/Ritz38/Analisis_maderas/refs/heads/main/Colombia.geo.json')
    
    # Crear la figura y el eje
    fig, ax = plt.subplots()
    
    # Graficar el mapa base de Colombia
    colombia.plot(ax=ax, color='lightgray', linewidth=0.8, edgecolor='k')
    
    # Asignar un color único a cada especie
    especies = gdf['ESPECIE'].unique()
    colores = plt.cm.tab20.colors  # Usar una paleta de colores (tab20 tiene 20 colores distintos)
    color_por_especie = {especie: colores[i % len(colores)] for i, especie in enumerate(especies)}
    
    # Graficar los municipios con colores según la especie
    for especie, color in color_por_especie.items():
        gdf_especie = gdf[gdf['ESPECIE'] == especie]
        gdf_especie.plot(ax=ax, color=color, markersize=50, label=especie)
    
    # Añadir etiquetas con el nombre del municipio
    for idx, row in gdf.iterrows():
        ax.text(
            x=row['LONGITUD'],
            y=row['LATITUD'],
            s=row['MUNICIPIO'].title(),  # Nombre del municipio en formato título
            fontsize=6, 
            ha='center',
            va='center',
            color='black',
            bbox=dict(facecolor='white', alpha=0.5, edgecolor='none')  # Fondo blanco para mejor legibilidad
        )
    
    # Establecer el título
    ax.set_title("Distribución geográfica de especies con menor volumen movilizado")
    
    # Mostrar la leyenda
    ax.legend(title="Especies", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

def main():
    """
    Función principal para ejecutar la aplicación en Streamlit.
    """
    st.title("Análisis de Especies de Madera")
    url = "https://raw.githubusercontent.com/Darkblack595/Apps_streamlit/refs/heads/main/base_datos_madera.csv"
    
    df = cargar_datos(url)
    datos = calcular_maderas_comunes(df)
    
    opcion = st.sidebar.selectbox("Selecciona una funcionalidad", [
        "Especies más comunes",
        "Top 10 especies con mayor volumen",
        "Mapa de calor por departamento",
        "Top 10 municipios con mayor movilización",
        "Evolución temporal por especie y tipo de producto",
        "Identificar outliers en los volúmenes de madera",
        "Volumen total de madera por municipio",
        "Especies con menor volumen y distribución geográfica"
    ])
    
    if opcion == "Especies más comunes":
        mostrar_visualizaciones(datos)
    elif opcion == "Top 10 especies con mayor volumen":
        mostrar_top_10_maderas(df)
    elif opcion == "Mapa de calor por departamento":
        generar_mapa_calor(df)
    elif opcion == "Top 10 municipios con mayor movilización":
        generar_mapa_top_10_municipios(df)
    elif opcion == "Evolución temporal por especie y tipo de producto":
        analizar_evolucion_temporal(df)
    elif opcion == "Identificar outliers en los volúmenes de madera":
        identificar_outliers(df)
    elif opcion == "Volumen total de madera por municipio":
        agrupar_por_municipio(df)
    elif opcion == "Especies con menor volumen y distribución geográfica":
        especies_menor_volumen_distribucion(df)

if __name__ == "__main__":
    main()
