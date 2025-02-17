import streamlit as st
import pandas as pd
import plotly.express as px
import json
import requests
import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns

def cargar_datos(url):
    """
    Carga el archivo CSV desde la URL proporcionada y devuelve un DataFrame de Pandas.
    
    Args:
        url (str): URL del archivo CSV.
    
    Returns:
        pd.DataFrame: DataFrame con los datos cargados.
    """
    return pd.read_csv(url)

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
    """
    Genera un mapa de calor con los volúmenes de madera por departamento en Colombia.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de madera.
    """
    # Agrupar los volúmenes de madera por departamento
    volumen_por_departamento = df.groupby('DPTO')['VOLUMEN M3'].sum().reset_index()
    
    # Crear un DataFrame para el mapa de calor
    # Aseguramos que todos los departamentos estén listados (incluso si hay departamentos sin datos)
    departamentos = [
        'Amazonas', 'Antioquia', 'Arauca', 'Atlántico', 'Bolívar', 'Boyacá', 'Caldas', 'Caquetá', 
        'Casanare', 'Cauca', 'Cesar', 'Chocó', 'Córdoba', 'Cundinamarca', 'Guaviare', 'Guainía', 
        'Huila', 'La Guajira', 'Magdalena', 'Meta', 'Nariño', 'Norte de Santander', 'Putumayo', 
        'Quindío', 'Risaralda', 'San Andrés y Providencia', 'Santander', 'Sucre', 'Tolima', 
        'Valle del Cauca', 'Vaupés', 'Vichada'
    ]
    
    # Asegurar que todos los departamentos están en el DataFrame, aunque algunos pueden tener volumen = 0
    volumen_por_departamento = volumen_por_departamento.set_index('DPTO').reindex(departamentos, fill_value=0).reset_index()
    
    # Crear una tabla de volúmenes por departamento para el gráfico
    volumen_por_departamento = volumen_por_departamento.set_index('DPTO')

    # Crear un gráfico de mapa de calor
    plt.figure(figsize=(12, 8))
    sns.heatmap(volumen_por_departamento.T, annot=True, fmt=",.0f", cmap="Blues", cbar=True, linewidths=0.5)
    
    # Título y etiquetas
    plt.title('Mapa de Calor de Volúmenes de Madera por Departamento', fontsize=16)
    plt.xlabel('Volumen de Madera (m3)', fontsize=12)
    plt.ylabel('Departamento', fontsize=12)
    
    # Rotar las etiquetas del eje Y para mejor visibilidad
    plt.yticks(rotation=0)  # Asegura que los nombres de los departamentos estén horizontales
    
    # Mostrar el gráfico en Streamlit
    st.pyplot(plt)


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
