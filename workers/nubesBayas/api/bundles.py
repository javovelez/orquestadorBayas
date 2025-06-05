import pandas as pd
import numpy as np
import os
import glob

def get_last(list_df: pd.DataFrame) -> pd.Series:
    """
    Obtiene la última fila de un DataFrame.
    
    Args:
        list_df (pd.DataFrame): DataFrame del cual se extraerá la última fila.
        
    Returns:
        pd.Series: Última fila del DataFrame.
    """
    return list_df.iloc[-1]

def get_frame_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrae los índices de frame de los nombres de imagen.
    
    Args:
        df (pd.DataFrame): DataFrame que contiene una columna 'image_name' con nombres de archivo.
        
    Returns:
        pd.DataFrame: DataFrame con los índices numéricos extraídos de los nombres de imagen.
    """
    names = df['image_name'].str.replace('.png', '')
    frame_index = names.str.extract(r"(\d+)$")
    return frame_index

def procesar_datos(df: pd.DataFrame, label: str, track_id_sum: int = 2000) -> pd.DataFrame:
    """
    Procesa los datos duplicando y transformando las filas con un label específico.
    
    Args:
        df (pd.DataFrame): DataFrame de entrada con los datos a procesar.
        label (str): Etiqueta de las filas que se duplicarán y transformarán.
        track_id_sum (int, optional): Valor a sumar a los track_id duplicados. Default 2000.
        
    Returns:
        pd.DataFrame: DataFrame resultante con las filas originales más las transformadas.
    """
    df_aux = df.loc[df['label'] == label].copy()

    df_aux['x'] = df_aux['x'] + df_aux['r']
    df_aux['label'] = 'radio'
    df_aux['track_id'] = df_aux['track_id'] + track_id_sum

    df_final = pd.concat([df, df_aux], ignore_index=True)

    return df_final

def generate_image_table(df: pd.DataFrame, baya_thresh: float = 0.5, qr_thresh: float = 0.5) -> pd.DataFrame:
    """
    Genera una tabla pivoteada de imágenes con métricas y filtrado por umbrales.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de detección.
        baya_thresh (float, optional): Umbral para filtrar detecciones de bayas/radio. Default 0.5.
        qr_thresh (float, optional): Umbral para filtrar detecciones de QR. Default 0.5.
        
    Returns:
        pd.DataFrame: DataFrame pivoteado con las columnas reorganizadas y filtradas.
    """
    df['image_name'] = df['image_name'].astype(str)
    df['image_index'] = get_frame_index(df).astype(int)

    df = df.drop(columns=['...10'], errors='ignore')

    image_indices = sorted(df['image_index'].unique())

    # Pivotar el DataFrame
    wide_df = df.pivot(
        index=['track_id', 'label'],
        columns='image_index',
        values=['image_name', 'x', 'y', 'r']
    )

    # Aplanar el multi-index de columnas
    wide_df.columns = [f'{col[0]}_{col[1]}' for col in wide_df.columns]

    wide_df = wide_df.reset_index()

    # Agregar columnas calculadas
    wide_df['nro_kf'] = len(image_indices)
    wide_df['count_na'] = wide_df.filter(like='_').isna().sum(axis=1) / 4

    # Aplicar umbrales
    wide_df['threshold'] = wide_df['label'].apply(lambda x: baya_thresh if x in ['baya', 'radio'] else qr_thresh)
    wide_df = wide_df[wide_df['count_na'] < wide_df['threshold']]

    # Reordenar columnas
    cols = ['track_id', 'label', 'nro_kf']
    for index in image_indices:
        cols.extend([f'{val}_{index}' for val in ['image_name', 'x', 'y', 'r']])
    wide_df = wide_df[cols]
    
    # Ordenar por track_id
    wide_df = wide_df.sort_values(by='track_id').reset_index(drop=True)
    
    return wide_df

def obtener_rutas_deteccion(ruta_archivo_txt: str) -> list:
    """
    Obtiene las rutas de archivos de detección a partir de un archivo de texto con rutas de video.
    
    Args:
        ruta_archivo_txt (str): Ruta al archivo de texto con las rutas de video.
        
    Returns:
        list: Lista de listas con las rutas de archivos de detección encontrados.
    """
    with open(ruta_archivo_txt, 'r') as f:
        rutas_videos = [line.strip() for line in f]

    rutas_carpetas = [os.path.dirname(ruta_video) for ruta_video in rutas_videos]

    archivos_deteccion = []
    for carpeta in rutas_carpetas:
        patron = os.path.join(carpeta, "*detections*.csv")
        archivos_csv = glob.glob(patron)
        archivos_deteccion.append(archivos_csv)

    return archivos_deteccion

def read_w_same_type(route: str) -> pd.DataFrame:
    """
    Lee un archivo CSV y asegura los tipos de datos correctos en las columnas clave.
    
    Args:
        route (str): Ruta al archivo CSV a leer.
        
    Returns:
        pd.DataFrame: DataFrame con los tipos de datos convertidos correctamente.
    """
    df = pd.read_csv(route)
    df['x'] = df['x'].astype(float)
    df['y'] = df['y'].astype(float)
    df['r'] = df['r'].astype(float)
    
    print("DF")
    print(df.head(10))

    return df

def read_bind_rows(file_paths: list) -> pd.DataFrame:
    """
    Lee y combina múltiples archivos CSV en un solo DataFrame.
    
    Args:
        file_paths (list): Lista de rutas a archivos CSV.
        
    Returns:
        pd.DataFrame: DataFrame combinado de todos los archivos de entrada.
    """
    dataframes = [read_w_same_type(file_path) for file_path in file_paths]
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

def write_in_folder(df: pd.DataFrame, folder: str) -> None:
    """
    Escribe un DataFrame en un archivo CSV dentro de una carpeta específica.
    
    Args:
        df (pd.DataFrame): DataFrame a guardar.
        folder (str): Ruta de la carpeta destino.
    """
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, "bundles.csv")
    df.to_csv(file_path, index=False, na_rep="NULL")
