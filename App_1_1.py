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
    opciones_genero = ["Deshabilitar"] + list(df['Género'].dropna().unique())
    opciones_frecuencia = ["Deshabilitar"] + list(df['Frecuencia_Compra'].dropna().unique())
    
    genero_seleccionado = st.selectbox("Seleccione un género:", opciones_genero)
    frecuencia_seleccionada = st.selectbox("Seleccione una frecuencia de compra:", opciones_frecuencia)
    
    datos_filtrados = df.copy()
    if genero_seleccionado != "Deshabilitar":
        datos_filtrados = datos_filtrados[datos_filtrados['Género'] == genero_seleccionado]
    if frecuencia_seleccionada != "Deshabilitar":
        datos_filtrados = datos_filtrados[datos_filtrados['Frecuencia_Compra'] == frecuencia_seleccionada]
    
    fig, ax = plt.subplots()
    sns.scatterplot(data=datos_filtrados, x='Edad', y='Ingreso_Anual_USD', ax=ax)
    sns.regplot(data=datos_filtrados, x='Edad', y='Ingreso_Anual_USD', scatter=False, ax=ax, color='red')
    titulo = "Correlación Global entre Edad e Ingreso Anual"
    if genero_seleccionado != "Deshabilitar":
        titulo += f" - Género: {genero_seleccionado}"
    if frecuencia_seleccionada != "Deshabilitar":
        titulo += f" - Frecuencia: {frecuencia_seleccionada}"
    ax.set_title(titulo)
    st.pyplot(fig)
    
    st.subheader("Análisis de la Correlación")
    correlacion = datos_filtrados[['Edad', 'Ingreso_Anual_USD']].corr().iloc[0, 1]
    st.write(f"El coeficiente de correlación entre la Edad y el Ingreso Anual es de {correlacion:.2f}.")
    if correlacion > 0.5:
        st.write("Existe una fuerte correlación positiva, lo que indica que a mayor edad, mayor ingreso anual en esta muestra.")
    elif correlacion < -0.5:
        st.write("Existe una fuerte correlación negativa, indicando que a mayor edad, menor ingreso anual en esta muestra.")
    else:
        st.write("La correlación entre la Edad y el Ingreso Anual no es significativa en esta muestra de datos.")



# URL del CSV
url = "https://raw.githubusercontent.com/gabrielawad/programacion-para-ingenieria/main/archivos-datos/aplicaciones/analisis_clientes.csv"

# Ejecutar la función
df = leer_csv_resumen(url)

# Funcionalidad de Analisis de correlacion
mostrar_correlacion(df)
