import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import matplotlib.pyplot as plt

def cargar_datos(url):
    """
    Carga el archivo CSV desde la URL proporcionada y devuelve un DataFrame de Pandas.
    
    Args:
        url (str): URL del archivo CSV.
    
    Returns:
        pd.DataFrame: DataFrame con los datos cargados.
    """
    df = pd.read_csv(url)
    return df

def cargar_coordenadas_municipios(url):
    """
    Carga el archivo CSV con las coordenadas de los municipios y normaliza los nombres.
    
    Args:
        url (str): URL del archivo CSV.
    
    Returns:
        pd.DataFrame: DataFrame con los datos de coordenadas de los municipios.
    """
    df = pd.read_csv(url)
    # Convertir los nombres de los municipios a minúsculas conservando tildes y caracteres especiales
    df['NOMBRE_MUNICIPIO'] = df['NOMBRE_MUNICIPIO'].str.lower()
    return df

def calcular_maderas_comunes(df):
    """
    Calcula las especies de madera más comunes y sus volúmenes totales a nivel país y por departamento.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de madera.
    
    Returns:
        dict: Diccionario con los datos agregados a nivel país y por departamento.
    """
    df_agrupado_pais = df.groupby('ESPECIE')['VOLUMEN M3'].sum().reset_index()
    df_agrupado_pais = df_agrupado_pais.sort_values(by='VOLUMEN M3', ascending=False)
    
    df_agrupado_departamento = df.groupby(['DPTO', 'ESPECIE'])['VOLUMEN M3'].sum().reset_index()
    df_agrupado_departamento = df_agrupado_departamento.sort_values(by=['DPTO', 'VOLUMEN M3'], ascending=[True, False])
    
    return {
        'pais': df_agrupado_pais,
        'departamento': df_agrupado_departamento
    }

def mostrar_top_10_maderas(df):
    """
    Muestra un gráfico de barras con las diez especies de madera con mayor volumen movilizado.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de madera.
    """
    df_top_10 = df.groupby('ESPECIE')['VOLUMEN M3'].sum().reset_index()
    df_top_10 = df_top_10.sort_values(by='VOLUMEN M3', ascending=False).head(10)
    
    st.subheader("Top 10 especies de madera con mayor volumen movilizado")
    fig_top_10 = px.bar(df_top_10, x='ESPECIE', y='VOLUMEN M3', title='Top 10 especies con mayor volumen movilizado')
    st.plotly_chart(fig_top_10)

def mostrar_visualizaciones(datos):
    """
    Muestra gráficos en Streamlit con la información de las especies de madera más comunes.
    
    Args:
        datos (dict): Diccionario con los DataFrames de maderas más comunes a nivel país y por departamento.
    """
    st.subheader("Especies de madera más comunes a nivel país")
    fig_pais = px.bar(datos['pais'], x='ESPECIE', y='VOLUMEN M3', title='Volumen por especie (País)')
    st.plotly_chart(fig_pais)
    
    st.subheader("Especies de madera más comunes por departamento")
    departamentos = datos['departamento']['DPTO'].unique()
    departamento_seleccionado = st.selectbox("Selecciona un departamento", departamentos)
    
    df_filtrado = datos['departamento'][datos['departamento']['DPTO'] == departamento_seleccionado]
    fig_departamento = px.bar(df_filtrado, x='ESPECIE', y='VOLUMEN M3', title=f'Volumen por especie en {departamento_seleccionado}')
    st.plotly_chart(fig_departamento)

def generar_mapa_calor(df):
    """Genera un mapa de calor de volúmenes de madera por departamento."""
    df['DPTO'] = df['DPTO'].str.upper()
    # Cargar el archivo GeoJSON de Colombia
    colombia = gpd.read_file('https://raw.githubusercontent.com/Ritz38/Analisis_maderas/refs/heads/main/Colombia.geo.json')
    
    # Crear la figura y el eje
    fig, ax = plt.subplots()
    
    # Agrupar los volúmenes de madera por departamento
    vol_por_dpto = df.groupby('DPTO')['VOLUMEN M3'].sum().reset_index()
    
    # Unir los datos de volumen con el GeoDataFrame
    df_geo = colombia.merge(vol_por_dpto, left_on='NOMBRE_DPT', right_on='DPTO')
    
    # Graficar el mapa de calor con el nuevo colormap
    df_geo.plot(column='VOLUMEN M3', cmap='YlGnBu', linewidth=0.8, edgecolor='k', legend=True, ax=ax)
    
    # Establecer el título
    ax.set_title("Distribución de volúmenes de madera por departamento")
    
    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

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
    gdf.plot(ax=ax, color='red', markersize=50, edgecolor='k')
    
    # Añadir etiquetas con el nombre del municipio (sin el volumen)
    for idx, row in gdf.iterrows():
        ax.text(
            x=row['LONGITUD'],
            y=row['LATITUD'],
            s=row['MUNICIPIO'].title(), 
            fontsize=6, 
            ha='center',
            va='center',
            color='black',
            bbox=dict(facecolor='white', alpha=0.0, edgecolor='none') 
        )
    
    # Establecer el título
    ax.set_title("Top 10 municipios con mayor movilización de madera")
    
    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

def analizar_evolucion_temporal(df):
    """
    Analiza la evolución temporal del volumen de madera movilizada por especie y tipo de producto.
    Filtra las opciones de tipo de producto para mostrar solo aquellos con datos disponibles para la especie seleccionada.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de madera.
    """
    st.subheader("Evolución temporal del volumen de madera movilizada")
    
    # Obtener listas únicas de especies y tipos de producto
    especies = df['ESPECIE'].unique()
    tipos_producto = df['TIPO PRODUCTO'].unique()
    
    # Seleccionar la especie
    especie_seleccionada = st.selectbox("Selecciona una especie", especies)
    
    # Filtrar tipos de producto válidos para la especie seleccionada
    tipos_producto_filtrados = df[
        df['ESPECIE'] == especie_seleccionada
    ]['TIPO PRODUCTO'].unique()
    
    # Mostrar mensaje si no hay tipos de producto válidos
    if len(tipos_producto_filtrados) == 0:
        st.warning(f"No hay datos disponibles para la especie '{especie_seleccionada}'.")
        return
    
    # Seleccionar el tipo de producto (solo opciones válidas)
    tipo_producto_seleccionado = st.selectbox(
        "Selecciona un tipo de producto",
        tipos_producto_filtrados
    )
    
    # Filtrar el DataFrame por la especie y tipo de producto seleccionados
    df_filtrado = df[
        (df['ESPECIE'] == especie_seleccionada) & 
        (df['TIPO PRODUCTO'] == tipo_producto_seleccionado)
    ]
    
    # Agrupar por año, semestre o trimestre según la selección del usuario
    periodo = st.radio("Selecciona el período de tiempo", ['AÑO', 'SEMESTRE', 'TRIMESTRE'])
    
    if periodo == 'AÑO':
        df_agrupado = df_filtrado.groupby('AÑO')['VOLUMEN M3'].sum().reset_index()
        x_axis = 'AÑO'
    elif periodo == 'SEMESTRE':
        df_agrupado = df_filtrado.groupby(['AÑO', 'SEMESTRE'])['VOLUMEN M3'].sum().reset_index()
        df_agrupado['PERIODO'] = df_agrupado['AÑO'].astype(str) + ' - ' + df_agrupado['SEMESTRE'].astype(str)
        x_axis = 'PERIODO'
    elif periodo == 'TRIMESTRE':
        df_agrupado = df_filtrado.groupby(['AÑO', 'TRIMESTRE'])['VOLUMEN M3'].sum().reset_index()
        df_agrupado['PERIODO'] = df_agrupado['AÑO'].astype(str) + ' - ' + df_agrupado['TRIMESTRE'].astype(str)
        x_axis = 'PERIODO'
    
    # Mostrar el gráfico de línea si hay datos
    if len(df_agrupado) > 0:
        fig = px.line(
            df_agrupado, 
            x=x_axis, 
            y='VOLUMEN M3', 
            title=f'Evolución temporal de {especie_seleccionada} - {tipo_producto_seleccionado}'
        )
        st.plotly_chart(fig)
    else:
        st.warning(f"No hay datos disponibles para la combinación seleccionada: {especie_seleccionada} - {tipo_producto_seleccionado}.")


def identificar_outliers(df):
    """
    Identifica outliers en los volúmenes de madera utilizando el rango intercuartílico (IQR)
    y muestra solo los datos de los outliers en una tabla, manteniendo los índices originales.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de madera.
    """
    st.subheader("Análisis de outliers en los volúmenes de madera")
    
    # Seleccionar la columna de volumen
    volumen = df['VOLUMEN M3']
    
    # Calcular el rango intercuartílico (IQR)
    Q1 = volumen.quantile(0.25)  # Primer cuartil (25%)
    Q3 = volumen.quantile(0.75)  # Tercer cuartil (75%)
    IQR = Q3 - Q1  # Rango intercuartílico
    
    # Definir los límites para identificar outliers
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    
    # Identificar outliers
    outliers = df[(volumen < limite_inferior) | (volumen > limite_superior)]
    
    # Mostrar el número de outliers encontrados
    st.write(f"Se encontraron **{len(outliers)} outliers** en los volúmenes de madera.")
    
    # Mostrar solo los datos de los outliers en una tabla, manteniendo los índices originales
    if len(outliers) > 0:
        st.write("### Datos de los outliers:")
        st.dataframe(outliers)  # Mostrar la tabla con los índices originales
    else:
        st.write("No se encontraron outliers en los datos.")
    
    # Mostrar un gráfico de caja (boxplot) para visualizar los outliers
    st.write("### Gráfico de caja (Boxplot) para visualizar los outliers:")
    fig = px.box(df, y='VOLUMEN M3', title='Distribución de volúmenes de madera con outliers')
    st.plotly_chart(fig)

def agrupar_por_municipio(df):
    """
    Agrupa los datos por municipio y calcula el volumen total de madera movilizada en cada uno.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de madera.
    """
    st.subheader("Volumen total de madera movilizada por municipio")
    
    # Agrupar por municipio y calcular el volumen total
    df_agrupado = df.groupby('MUNICIPIO')['VOLUMEN M3'].sum().reset_index()
    df_agrupado = df_agrupado.sort_values(by='VOLUMEN M3', ascending=False)  # Ordenar de mayor a menor
    
    # Mostrar la tabla con los resultados
    st.write("### Volumen total de madera por municipio:")
    st.dataframe(df_agrupado)
    
    # Mostrar un gráfico de barras para visualizar los resultados
    st.write("### Gráfico de barras: Volumen total por municipio")
    fig = px.bar(df_agrupado, x='MUNICIPIO', y='VOLUMEN M3', title='Volumen total de madera por municipio')
    st.plotly_chart(fig)

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
