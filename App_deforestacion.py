import streamlit as st
import pandas as pd

def cargar_datos():
    """
    Permite al usuario cargar un archivo CSV desde su computadora o mediante una URL.

    Returns:
        pd.DataFrame or None: Un DataFrame con los datos cargados o None si no se cargó nada.
    """
    st.sidebar.title("Cargar Datos")
    st.sidebar.write("Suba un archivo CSV o ingrese una URL para cargar los datos.")

    # Opción para subir un archivo CSV
    archivo_subido = st.sidebar.file_uploader(
        "Suba un archivo CSV",
        type=["csv"],
        help="Suba un archivo CSV desde su computadora."
    )

    # Opción para ingresar una URL
    url = st.sidebar.text_input(
        "Ingrese la URL de un archivo CSV",
        help="Ingrese la URL de un archivo CSV para cargar los datos."
    )

    # Cargar datos desde el archivo subido
    if archivo_subido is not None:
        try:
            datos = pd.read_csv(archivo_subido)
            st.sidebar.success("Archivo CSV cargado correctamente.")
            return datos
        except Exception as e:
            st.sidebar.error(f"Error al cargar el archivo CSV: {e}")
            return None

    # Cargar datos desde la URL
    elif url:
        try:
            datos = pd.read_csv(url)
            st.sidebar.success("Datos cargados correctamente desde la URL.")
            return datos
        except Exception as e:
            st.sidebar.error(f"Error al cargar los datos desde la URL: {e}")
            return None

    # Si no se cargó nada
    else:
        return None


def mostrar_caracteristicas(datos):
    """
    Muestra las características principales del dataset.

    Args:
        datos (pd.DataFrame): El DataFrame del cual se mostrarán las características.
    """
    st.subheader("Características principales del dataset")

    # Crear un diccionario con las características principales
    caracteristicas = {
        "Número de filas": datos.shape[0],
        "Número de columnas": datos.shape[1],
        "Columnas": list(datos.columns),
        "Tipos de datos": datos.dtypes.to_dict(),
        "Valores nulos": datos.isnull().sum().to_dict(),
    }

    # Mostrar las características en una tabla
    st.table(pd.DataFrame.from_dict(caracteristicas, orient="index"))


def main():
    """
    Función principal de la aplicación Streamlit.
    """
    st.title("Aplicación de Análisis de Datos")
    st.write("Bienvenido a la aplicación de análisis de datos.")

    # Cargar los datos
    datos = cargar_datos()

    # Verificar si los datos se cargaron correctamente
    if datos is not None:
        # Mostrar características principales del dataset
        mostrar_caracteristicas(datos)

        # Mostrar una muestra de los primeros 5 elementos
        st.subheader("Muestra de los primeros 5 elementos")
        st.dataframe(datos.head())
    else:
        st.warning("Por favor, suba un archivo CSV o ingrese una URL para continuar.")


if __name__ == "__main__":
    main()
