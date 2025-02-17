import streamlit as st
import pandas as pd
import plotly.express as px
import json
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
    Genera un mapa de Sudamérica utilizando GeoPandas y Matplotlib,
    resaltando a Colombia con base en el volumen total de madera,
    utilizando un archivo ZIP con los límites de los países.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de madera.
    """
    # Se asume que el CSV contiene información de departamentos de Colombia.
    # Se agrupa y se obtiene el total de madera para Colombia.
    volumen_total = df['VOLUMEN M3'].sum()
    
    # Cargar el conjunto de datos de países desde el archivo ZIP en la URL proporcionada
    url = "https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_0_countries.zip"
    
    # Leer los datos directamente desde el archivo ZIP en la URL
    world = gpd.read_file(url)
    
    # Filtrar solo los países de Sudamérica
    south_america = world[world['continent'] == "South America"].copy()
    
    # Crear una nueva columna para almacenar el volumen de madera (inicialmente en 0)
    south_america["wood_volume"] = 0.0
    
    # Asumimos que todos los datos corresponden a Colombia.
    # Resaltamos a Colombia asignándole el volumen total de madera.
    south_america.loc[south_america['name'] == "Colombia", "wood_volume"] = volumen_total
    
    # Plotear el mapa
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    # Se pinta el mapa usando la columna "wood_volume". Los países sin datos se muestran en gris claro.
    south_america.plot(column="wood_volume", 
                       ax=ax, 
                       legend=True,
                       cmap="Blues", 
                       missing_kwds={"color": "lightgrey", "edgecolor": "red", "hatch": "///", "label": "Sin datos"})
    
    ax.set_title("Mapa de madera en Sudamérica (Colombia resaltada)", fontsize=15)
    ax.set_axis_off()
    
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
