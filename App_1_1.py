def mostrar_mapa(df):
    """
    Muestra mapas de ubicación de clientes en Streamlit con un mapa base usando GeoPandas.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de clientes.
    """
    st.title("Mapa de Ubicación de Clientes")
    opciones_genero = ["Deshabilitar"] + list(df['Género'].dropna().unique())
    opciones_frecuencia = ["Deshabilitar"] + list(df['Frecuencia_Compra'].dropna().unique())
    
    genero_seleccionado = st.selectbox("Seleccione un género:", opciones_genero)
    frecuencia_seleccionada = st.selectbox("Seleccione una frecuencia de compra:", opciones_frecuencia)
    
    datos_filtrados = df.copy()
    if genero_seleccionado != "Deshabilitar":
        datos_filtrados = datos_filtrados[datos_filtrados['Género'] == genero_seleccionado]
    if frecuencia_seleccionada != "Deshabilitar":
        datos_filtrados = datos_filtrados[datos_filtrados['Frecuencia_Compra'] == frecuencia_seleccionada]
    
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    gdf = gpd.GeoDataFrame(datos_filtrados, geometry=gpd.points_from_xy(datos_filtrados.Longitud, datos_filtrados.Latitud))
    
    st.subheader("Mapa de Ubicación de Clientes")
    fig, ax = plt.subplots(figsize=(10, 6))
    world.plot(ax=ax, color='lightgrey')
    gdf.plot(ax=ax, markersize=10, color='red', alpha=0.5)
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.set_title("Distribución Geográfica de Clientes")
    st.pyplot(fig)
