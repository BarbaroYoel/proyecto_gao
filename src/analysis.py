import pandas as pd
import plotly.express as px

COLOR_PRIMARY_1 = "#e4ab0d"  
COLOR_PRIMARY_2 = "#2A4A6B"  

def plot_properties_by_municipality(df: pd.DataFrame, top_n: int = 10):
    counts = df['Municipio'].value_counts().reset_index()
    counts.columns = ['Municipio', 'Cantidad']
    
    top_counts = counts.head(top_n)
    
    fig = px.bar(top_counts, x='Cantidad', y='Municipio', orientation='h',
                 title=f'Top {top_n} Municipios con más Propiedades',
                 labels={'Cantidad': 'Número de Propiedades', 'Municipio': 'Municipio'},
                 color='Cantidad',
                 color_continuous_scale=[COLOR_PRIMARY_2, COLOR_PRIMARY_1])
    return fig

def plot_category_distribution(df: pd.DataFrame):
    counts = df['Categoria'].value_counts().reset_index()
    counts.columns = ['Categoria', 'Cantidad']
    
    color_map = {
        'alquiler': COLOR_PRIMARY_1,
        'venta': COLOR_PRIMARY_2
    }
    
    fig = px.pie(counts, values='Cantidad', names='Categoria', 
                 title='Proporción Alquiler vs Venta',
                 hole=0.3, 
                 color='Categoria',
                 color_discrete_map=color_map)
    return fig

def plot_property_type_distribution(df: pd.DataFrame):
    df_filtered = df[df['Tipo'].isin(['casa', 'apartamento'])]
    
    counts = df_filtered['Tipo'].value_counts().reset_index()
    counts.columns = ['Tipo', 'Cantidad']
    
    color_map = {
        'casa': COLOR_PRIMARY_1,
        'apartamento': COLOR_PRIMARY_2
    }
    
    fig = px.pie(counts, values='Cantidad', names='Tipo', 
                 title='Proporción Casas vs Apartamentos',
                 hole=0.3,
                 color='Tipo',
                 color_discrete_map=color_map)
    return fig

def plot_price_by_municipality(df: pd.DataFrame):
    """Precio promedio y mediana por municipio"""
    price_data = df.groupby('Municipio')['Precio'].agg(['mean', 'median']).reset_index()
    price_data = price_data.sort_values('mean', ascending=False)
    
    fig = px.bar(price_data, 
                 x='Municipio', 
                 y=['mean', 'median'],
                 barmode='group',
                 title='Precio Promedio y Mediano por Municipio',
                 labels={'value': 'Precio (USD)', 'variable': 'Métrica'},
                 color_discrete_sequence=[COLOR_PRIMARY_1, COLOR_PRIMARY_2])
    return fig

def plot_price_trend_by_property_type(df: pd.DataFrame):
    """Línea de tiempo de precios por tipo de propiedad"""
    df = df[df['Tipo'].isin(['casa', 'apartamento'])]
    
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df['Mes'] = df['Fecha'].dt.to_period('M').dt.to_timestamp()
    
    price_data = df.groupby(['Mes', 'Tipo'])['Precio'].mean().reset_index()
    
    fig = px.line(price_data, 
                  x='Mes', 
                  y='Precio', 
                  color='Tipo',
                  title='Evolución de Precios por Tipo de Propiedad',
                  labels={'Precio': 'Precio Promedio (USD)', 'Mes': 'Fecha'},
                  color_discrete_map={
                      'casa': COLOR_PRIMARY_1,
                      'apartamento': COLOR_PRIMARY_2
                  })
    return fig

def normalize_amenity(amenity: str) -> str:
    """Normaliza el nombre de una amenidad para agrupar variaciones"""
    amenity = amenity.strip().lower()
    
    mappings = {
        'tel fijo': 'telefono fijo',
        'telef fijo': 'telefono fijo',
        'telefono': 'telefono fijo',
        'teléfono': 'telefono fijo',
        'tfijo': 'telefono fijo',
        'cisternas': 'cisterna',
        'tanques': 'tanque',
        'tanques elevados': 'tanque elevado',
        'tanque de agua': 'tanque',
        'split': 'aire acondicionado',
        'ac': 'aire acondicionado',
        'aa': 'aire acondicionado'
    }
    
    return mappings.get(amenity, amenity)

def plot_price_trend(df: pd.DataFrame):
    """Línea de tiempo de precio promedio filtrado"""
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df['Mes'] = df['Fecha'].dt.to_period('M').dt.to_timestamp()
    
    price_data = df.groupby('Mes')['Precio'].mean().reset_index()
    
    fig = px.line(price_data, 
                  x='Mes', 
                  y='Precio',
                  title='Evolución de Precio Promedio',
                  labels={'Precio': 'Precio Promedio (USD)', 'Mes': 'Fecha'},
                  color_discrete_sequence=[COLOR_PRIMARY_1])
    return fig