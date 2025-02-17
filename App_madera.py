import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import requests

def cargar_datos(url):
    """
    Carga el archivo CSV desde la URL proporcionada y devuelve un DataFrame de Pandas.
    
    Args:
        url (str): URL del archivo CSV.
    
    Returns:
        pd.DataFrame: DataFrame con los datos cargados.
    """
    return pd.read_csv(url)

def mostrar_top_10_maderas(df):
    """
    Muestra un gráfico de barras con las diez especies de madera más comunes y sus volúmenes asociados.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de madera.
    """
    # Identificar las especies más comunes (frecuencia de aparición)
    especies_comunes = df['ESPECIE'].value_counts().reset_index()
    especies_comunes.columns = ['ESPECIE', 'FRECUENCIA']
    especies_comunes = especies_comunes.sort_values(by='FRECUENCIA', ascending=False).head(10)
    
    # Filtrar el DataFrame original para obtener solo las especies más comunes
    df_filtrado = df[df['ESPECIE'].isin(especies_comunes['ESPECIE'])]
    
    # Calcular el volumen total por especie
    df_top_10 = df_filtrado.groupby('ESPECIE')['VOLUMEN M3'].sum().reset_index()
    df_top_10 = df_top_10.sort_values(by='VOLUMEN M3', ascending=False)
    
    st.subheader("Top 10 especies de madera más comunes y sus volúmenes asociados")
    fig_top_10 = px.bar(df_top_10, x='ESPECIE', y='VOLUMEN M3', title='Top 10 especies más comunes y sus volúmenes')
    st.plotly_chart(fig_top_10)
    

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
    fig_pais = px.bar(datos['pais'], x='ESPECIE', y='FRECUENCIA', title='Frecuencia por especie (País)')
    st.plotly_chart(fig_pais)
    
    st.subheader("Especies de madera más comunes por departamento")
    departamentos = datos['departamento']['DPTO'].unique()
    departamento_seleccionado = st.selectbox("Selecciona un departamento", departamentos)
    
    df_filtrado = datos['departamento'][datos['departamento']['DPTO'] == departamento_seleccionado]
    fig_departamento = px.bar(df_filtrado, x='ESPECIE', y='FRECUENCIA', title=f'Frecuencia por especie en {departamento_seleccionado}')
    st.plotly_chart(fig_departamento)

def generar_mapa_calor(df):
    """
    Genera un mapa de calor con los volúmenes de madera por departamento en Colombia.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de madera.
    """
    # Agrupar los volúmenes de madera por departamento
    volumen_por_departamento = df.groupby('DPTO')['VOLUMEN M3'].sum().reset_index()
    
    # Cargar el GeoJSON desde la URL
    url_geojson = "https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/3aadedf47badbdac823b00dbe259f6bc6d9e1899/colombia.geo.json"
    response = requests.get(url_geojson)
    colombia_geo = response.json()
    
    # Crear un DataFrame con los nombres de los departamentos del GeoJSON
    departamentos_geojson = [feature['properties']['NOMBRE_DPT'] for feature in colombia_geo['features']]
    df_geojson = pd.DataFrame({'DPTO': departamentos_geojson})
    
    # Unir los datos de volumen con los nombres de los departamentos del GeoJSON
    df_merged = df_geojson.merge(volumen_por_departamento, on='DPTO', how='left')
    df_merged['VOLUMEN M3'] = df_merged['VOLUMEN M3'].fillna(0)  # Rellenar con 0 si no hay datos
    
    # Crear el mapa coroplético
    fig = px.choropleth(df_merged, 
                        geojson=colombia_geo, 
                        locations='DPTO', 
                        featureidkey="properties.NOMBRE_DPT",
                        color='VOLUMEN M3',
                        hover_name='DPTO',
                        color_continuous_scale="Blues",
                        title='Distribución de Volúmenes de Madera por Departamento en Colombia')
    
    # Ajustar el layout del mapa
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    
    # Mostrar el mapa en Streamlit
    st.plotly_chart(fig)

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
        "Mapa de calor por departamento"
    ])
    
    if opcion == "Especies más comunes":
        mostrar_visualizaciones(datos)
    elif opcion == "Top 10 especies con mayor volumen":
        mostrar_top_10_maderas(df)
    elif opcion == "Mapa de calor por departamento":
        generar_mapa_calor(df)
    

if __name__ == "__main__":
    main()
