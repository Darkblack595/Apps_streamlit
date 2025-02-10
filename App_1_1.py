import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def leer_csv_resumen(url):
    """
    Lee un archivo CSV desde una URL y muestra un resumen de sus características.

    Args:
        url (str): URL del archivo CSV en GitHub.

    Returns:
        pd.DataFrame: DataFrame con los datos leídos y limpios.
    """
    # Leer el archivo CSV desde la URL
    df = pd.read_csv(url)

    # Llenar valores faltantes
    # 1. Nombre: Buscar el más parecido dentro del mismo género
    df['Nombre'] = df['Nombre'].mask(df['Nombre'].isna(), df.groupby('Género')['Nombre'].transform(lambda x: x.ffill()))

    # 2. Edad: Usar el promedio de edad para el mismo nombre y género
    df['Edad'] = df['Edad'].mask(df['Edad'].isna(), df.groupby(['Nombre', 'Género'])['Edad'].transform('mean'))

    # 3. Género: Usar la última aparición del mismo nombre
    df['Género'] = df['Género'].mask(df['Género'].isna(), df.groupby('Nombre')['Género'].transform(lambda x: x.ffill()))

    # 4. Ingreso_Anual_USD: Promedio según el género y edad similar
    df['Ingreso_Anual_USD'] = df['Ingreso_Anual_USD'].mask(df['Ingreso_Anual_USD'].isna(), df.groupby(['Género', 'Edad'])['Ingreso_Anual_USD'].transform('mean'))

    # 5. Historial_Compras: Promedio para mismo género y edad similar, con respaldo en la mediana global
    df['Historial_Compras'] = df['Historial_Compras'].mask(
        df['Historial_Compras'].isna(),
        df.groupby(['Género', 'Edad'])['Historial_Compras'].transform('mean')
    ).fillna(df['Historial_Compras'].median())

    # 6. Frecuencia_Compra: Moda entre edades similares
    df['Frecuencia_Compra'] = df['Frecuencia_Compra'].mask(df['Frecuencia_Compra'].isna(), df.groupby('Edad')['Frecuencia_Compra'].transform(lambda x: x.mode()[0] if not x.mode().empty else 'Media'))

    # 7. Latitud y Longitud: Interpolación lineal solo en valores nulos
    df[['Latitud', 'Longitud']] = df[['Latitud', 'Longitud']].interpolate(method='linear', limit_direction='both')

    # Mostrar resumen del DataFrame
    """print("Resumen del CSV:")
    print("-----------------------------------")
    print(f"Tamaño del dataset: {df.shape[0]} filas, {df.shape[1]} columnas")
    print(f"Columnas: {list(df.columns)}")
    print("Tipos de datos:")
    print(df.dtypes)
    print("Valores nulos por columna:")
    print(df.isnull().sum())"""

    return df


def mostrar_correlacion(df):
    """
    Muestra gráficos de correlación entre Edad e Ingreso Anual según la opción seleccionada en Streamlit.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de clientes.
    """
    st.title("Análisis de Correlación")
    opciones = ["Global", "Por Género", "Por Frecuencia de Compra"]
    seleccion = st.selectbox("Seleccione el tipo de análisis:", opciones)
    
    fig, ax = plt.subplots()
    if seleccion == "Global":
        sns.scatterplot(data=df, x='Edad', y='Ingreso_Anual_USD', ax=ax)
        ax.set_title("Correlación Global entre Edad e Ingreso Anual")
    elif seleccion == "Por Género":
        sns.scatterplot(data=df, x='Edad', y='Ingreso_Anual_USD', hue='Género', ax=ax)
        ax.set_title("Correlación por Género entre Edad e Ingreso Anual")
    elif seleccion == "Por Frecuencia de Compra":
        sns.scatterplot(data=df, x='Edad', y='Ingreso_Anual_USD', hue='Frecuencia_Compra', ax=ax)
        ax.set_title("Correlación por Frecuencia de Compra entre Edad e Ingreso Anual")
    
    st.pyplot(fig)


# URL del CSV
url = "https://raw.githubusercontent.com/gabrielawad/programacion-para-ingenieria/main/archivos-datos/aplicaciones/analisis_clientes.csv"

# Ejecutar la función
df = leer_csv_resumen(url)

# Funcionalidad de Analisis de correlacion
mostrar_correlacion(df)
