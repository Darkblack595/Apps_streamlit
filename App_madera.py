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

def generar_mapa_top_10_municipios(df, df_coordenadas):
    """
    Genera un mapa de Colombia con los diez municipios con mayor movilización de madera.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de madera.
        df_coordenadas (pd.DataFrame): DataFrame con las coordenadas de los municipios.
    """
    # Convertir los nombres de los municipios a minúsculas en el dataset original
    df['MUNICIPIO'] = df['MUNICIPIO'].str.lower()
    
    # Agrupar los volúmenes de madera por municipio
    vol_por_municipio = df.groupby('MUNICIPIO')['VOLUMEN M3'].sum().reset_index()
    
    # Ordenar y seleccionar los 10 municipios con mayor volumen
    top_10_municipios = vol_por_municipio.sort_values(by='VOLUMEN M3', ascending=False).head(10)
    
    # Unir los datos de los municipios con mayor volumen con las coordenadas
    top_10_municipios = top_10_municipios.merge(
        df_coordenadas,
        left_on='MUNICIPIO',
        right_on='NOMBRE_MUNICIPIO',
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
    
    # Graficar los 10 municipios con mayor volumen
    gdf.plot(ax=ax, color='red', markersize=100, edgecolor='k', label='Top 10 municipios')
    
    # Añadir etiquetas con el nombre del municipio y el volumen
    for idx, row in gdf.iterrows():
        ax.text(
            x=row['LONGITUD'],
            y=row['LATITUD'],
            s=f"{row['MUNICIPIO'].title()}\n{row['VOLUMEN M3']:.2f} m³",
            fontsize=8,
            ha='center',
            va='center',
            color='black',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
        )
    
    # Establecer el título
    ax.set_title("Top 10 municipios con mayor movilización de madera")
    
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
        "Top 10 municipios con mayor movilización"
    ])
    
    if opcion == "Especies más comunes":
        mostrar_visualizaciones(datos)
    elif opcion == "Top 10 especies con mayor volumen":
        mostrar_top_10_maderas(df)
    elif opcion == "Mapa de calor por departamento":
        generar_mapa_calor(df)
    elif opcion == "Top 10 municipios con mayor movilización":
        df_coordenadas = pd.read_csv('https://raw.githubusercontent.com/Darkblack595/Apps_streamlit/refs/heads/main/DIVIPOLA_C_digos_municipios_geolocalizados_20250217.csv')
        generar_mapa_top_10_municipios(df, df_coordenadas)
    

if __name__ == "__main__":
    main()
