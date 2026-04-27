import pandas as pd
import plotly.express as px
import json
from collections import Counter
from plotly.subplots import make_subplots
import plotly.graph_objects as go 
import unicodedata

PRIMARY_COLOR_1 = "#e4ab0d"  
PRIMARY_COLOR_2 = '#1A3650' 

def grafica(df_prueba:pd.DataFrame):
    df_prueba = df_prueba[df_prueba['Tipo'].isin(['casa', 'apartamento'])&(df_prueba['Categoria']=='venta')].copy()
    df_prueba= df_prueba[(df_prueba['Categoria']=='venta')]
    
    df_casa=df_prueba[(df_prueba['Tipo']=='casa')]
    df_apartamento=df_prueba[(df_prueba['Tipo']=='apartamento')]
    
    
    max_casa=df_casa["Precio"].max()
    max_apartamento=df_apartamento["Precio"].max()
    
    median_casa=df_casa["Precio"].median()
    median__apartamento=df_apartamento["Precio"].median()
    
    
    min_casa=df_casa["Precio"].min()
    min_apartamento=df_apartamento["Precio"].min()
    
    precio_data = { "datos": [
    {"medida": "max", "apartamento":max_apartamento,"casa":max_casa},
    {"medida": "median", "apartamento":median__apartamento,"casa":median_casa},
    {"medida": "min", "apartamento":min_apartamento,"casa":min_casa},
    ]}
    
    precio_data = pd.DataFrame(precio_data['datos'])
    fig = px.bar(
        precio_data, 
        x='medida', 
        y=['apartamento','casa'],
        barmode='group',
        title='Precio maximo , mediano y minimo',
                 labels={'value': 'Precio (USD)', 'variable': 'Métrica'},
                 color_discrete_sequence=[PRIMARY_COLOR_1, PRIMARY_COLOR_2]
    )
    return fig


def plot_properties_by_municipality(dataframe: pd.DataFrame, top_n: int = 10):
    counts = dataframe['Municipio'].value_counts().reset_index()
    counts.columns = ['Municipio', 'Cantidad']
    top_counts = counts.head(top_n)
    fig = px.bar(top_counts, x='Cantidad', y='Municipio', orientation='h',
                 title=f'Top {top_n} Municipios con más Propiedades',
                 labels={'Cantidad': 'Número de Propiedades', 'Municipio': 'Municipio'},
                 color='Cantidad',
                 color_continuous_scale=[PRIMARY_COLOR_2, PRIMARY_COLOR_1])
    return fig

def plot_category_distribution(dataframe: pd.DataFrame):
    counts = dataframe['Categoria'].value_counts().reset_index()
    counts.columns = ['Categoria', 'Cantidad']
    color_map = {
        'alquiler': PRIMARY_COLOR_1,
        'venta': PRIMARY_COLOR_2
    }
    fig = px.pie(counts, values='Cantidad', names='Categoria', 
                 title='Proporción Alquiler vs Venta',
                 hole=0.3, 
                 color='Categoria',
                 color_discrete_map=color_map)
    return fig

def plot_property_type_distribution(dataframe: pd.DataFrame):
    filtered_data = dataframe[dataframe['Tipo'].isin(['casa', 'apartamento'])]
    
    counts = filtered_data['Tipo'].value_counts().reset_index()
    counts.columns = ['Tipo', 'Cantidad']
    
    color_map = {
        'casa': PRIMARY_COLOR_1,
        'apartamento': PRIMARY_COLOR_2
    }
    fig = px.pie(counts, values='Cantidad', names='Tipo', 
                 title='Proporción Casas vs Apartamentos',
                 hole=0.3,
                 color='Tipo',
                 color_discrete_map=color_map)
    return fig

    
#  df_prueba= df_prueba[(df_prueba['Categoria']=='venta')]
#     price_data = df_prueba.groupby('Tipo')['Precio'].agg(['max','median','min']).reset_index()
#     price_data = price_data.sort_values('median', ascending=False)
#     fig = px.bar(price_data, 
#                  x=['max','median','min'], 
#                  y='Tipo',
#                  barmode='group',
#                  title='Precio maximo , mediano y minimo',
#                  labels={'value': 'Precio (USD)', 'variable': 'Métrica'},
#                  color_discrete_sequence=[PRIMARY_COLOR_1, PRIMARY_COLOR_2])
#     return fig

def plot_price_by_municipality(dataframe: pd.DataFrame):
    """Precio promedio y mediana por municipio"""
    price_data = dataframe.groupby('Municipio')['Precio'].agg(['mean', 'median']).reset_index()
    price_data = price_data.sort_values('mean', ascending=False)
    fig = px.bar(price_data, 
                 x='Municipio', 
                 y=['mean', 'median'],
                 barmode='group',
                 title='Precio Promedio y Mediano por Municipio',
                 labels={'value': 'Precio (USD)', 'variable': 'Métrica'},
                 color_discrete_sequence=[PRIMARY_COLOR_1, PRIMARY_COLOR_2])
    return fig

def plot_price_trend_by_property_type(dataframe: pd.DataFrame):
    """Línea de tiempo de precios medianos por tipo de propiedad"""
    filtered_data = dataframe[dataframe['Tipo'].isin(['casa', 'apartamento'])]
    filtered_data['Fecha'] = pd.to_datetime(filtered_data['Fecha'], errors='coerce')
    filtered_data['Mes'] = filtered_data['Fecha'].dt.to_period('M').dt.to_timestamp()
    price_data = filtered_data.groupby(['Mes', 'Tipo'])['Precio'].median().reset_index()
    fig = px.line(price_data, 
                  x='Mes', 
                  y='Precio', 
                  color='Tipo',
                  title='Evolución del Precio Mediano por Tipo de Propiedad',
                  labels={'Precio': 'Precio Mediano (USD)', 'Mes': 'Fecha'},
                  color_discrete_map={
                      'casa': PRIMARY_COLOR_1,
                      'apartamento': PRIMARY_COLOR_2
                  })
    return fig
 
def plot_price_trend(dataframe: pd.DataFrame):
    """Línea de tiempo de precio mediano filtrado"""
    if not pd.api.types.is_datetime64_any_dtype(dataframe['Fecha']):
        dataframe['Fecha'] = pd.to_datetime(dataframe['Fecha'], errors='coerce')
    
    dataframe['Mes'] = dataframe['Fecha'].dt.to_period('M').dt.to_timestamp()
    price_data = dataframe.groupby('Mes')['Precio'].median().reset_index()
    if len(price_data) < 2:
        return None
    
    fig = px.line(
        price_data, 
        x='Mes', 
        y='Precio',
        markers=True,
        title='Evolución del Precio Mediano',
        labels={'Precio': 'Precio Mediano (USD)', 'Mes': 'Fecha'},
        color_discrete_sequence=[PRIMARY_COLOR_1]
    )
    
    fig.update_traces(
        text=price_data['Precio'].apply(lambda x: f"${x:,.0f}"),
        textposition="top center",
        hovertemplate="<b>%{x|%b %Y}</b><br>Precio: $%{y:,.0f} USD"
    )
    
    fig.update_layout(
        hovermode="x unified",
        xaxis=dict(
            tickformat="%b %Y",
            tickmode='auto',
            nticks=min(12, len(price_data))  
    ))
    return fig

def plot_amenities_by_property_type(dataframe: pd.DataFrame, top_n: int = 10):
    """Analiza y grafica las amenidades más comunes por tipo de propiedad"""
    filtered_data = dataframe[dataframe['Tipo'].isin(['casa', 'apartamento'])].copy()
    filtered_data = filtered_data[filtered_data['Amenidades'].apply(lambda x: isinstance(x, list) and len(x) > 0)]
    
    houses_data = filtered_data[filtered_data['Tipo'] == 'casa']
    apartments_data = filtered_data[filtered_data['Tipo'] == 'apartamento']
    
    def count_amenities(data_group):
        counter = Counter()
        for amenities in data_group['Amenidades']:
            counter.update(amenities)
        return counter
    
    houses_counter = count_amenities(houses_data)
    apartments_counter = count_amenities(apartments_data)
    
    houses_count = pd.DataFrame(houses_counter.most_common(top_n), 
                                columns=['Amenidad', 'Casas'])
   
    apartments_count = pd.DataFrame(apartments_counter.most_common(top_n), 
                                    columns=['Amenidad', 'Apartamentos'])
   
    comparison_data = pd.merge(houses_count, apartments_count, 
                               on='Amenidad', how='outer').fillna(0)
   
    comparison_data['Total'] = comparison_data['Casas'] + comparison_data['Apartamentos']
    comparison_data = comparison_data.sort_values('Total', ascending=False).head(top_n)
    
    fig = px.bar(
        comparison_data,
        x='Amenidad',
        y=['Casas', 'Apartamentos'],
        title=f'Top {top_n} Amenidades por Tipo de Propiedad',
        labels={'value': 'Número de Propiedades', 'Amenidad': 'Amenidad'},
        barmode='group',
        color_discrete_sequence=[PRIMARY_COLOR_1, PRIMARY_COLOR_2]
    )
    
    fig.update_layout(
        legend_title_text='Tipo de Propiedad',
        xaxis_tickangle=-45,
        height=500,
        margin=dict(l=50, r=50, t=80, b=150)
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Tipo: %{meta[0]}<br>Propiedades: %{y}',
        marker_line_color='white',
        marker_line_width=1,
        meta=[['Casas']*len(comparison_data), ['Apartamentos']*len(comparison_data)]
    )
    
    return fig

def plot_top_amenities_by_filters(dataframe: pd.DataFrame, top_n: int = 10) -> go.Figure:
    filtered_data = dataframe[dataframe['Amenidades'].apply(lambda x: isinstance(x, list) and len(x) > 0)].copy()
    
    amenities_counter = Counter()
    for amenities in filtered_data['Amenidades']:
        amenities_counter.update(amenities)
    
    top_amenities = amenities_counter.most_common(top_n)
    amenities_data = pd.DataFrame(top_amenities, columns=['Amenidad', 'Cantidad'])
    
    amenities_data = amenities_data.sort_values('Cantidad', ascending=True)
    
    title = "Top Amenidades"
    if len(filtered_data) > 0:
        category = filtered_data['Categoria'].iloc[0] if 'Categoria' in filtered_data.columns and len(filtered_data['Categoria'].unique()) == 1 else None
        property_type = filtered_data['Tipo'].iloc[0] if 'Tipo' in filtered_data.columns and len(filtered_data['Tipo'].unique()) == 1 else None
        
        if category and property_type:
            title = f"Amenidades más Comunes en {property_type.capitalize()}s para {'Venta' if category == 'venta' else 'Alquiler'}"
        elif category:
            title = f"Amenidades más Comunes en Propiedades para {'Venta' if category == 'venta' else 'Alquiler'}"
        elif property_type:
            title = f"Amenidades más Comunes en {property_type.capitalize()}s"
    
    fig = px.bar(
        amenities_data,
        x='Cantidad',
        y='Amenidad',
        orientation='h',
        title=title,
        labels={'Cantidad': 'Número de Propiedades', 'Amenidad': ''},
        color='Cantidad',
        color_continuous_scale=[PRIMARY_COLOR_2, PRIMARY_COLOR_1]
    )
    
    fig.update_layout(
        showlegend=False,
        height=500,
        margin=dict(l=150, r=50, t=80, b=50),
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

def get_top_amenities_description(dataframe: pd.DataFrame) -> str:
    if dataframe.empty:
        return "No hay datos disponibles"
    
    amenities_counter = Counter()
    for amenities in dataframe['Amenidades']:
        if isinstance(amenities, list):
            amenities_counter.update(amenities)
    
    top_amenities = [amenity for amenity, _ in amenities_counter.most_common(3)]
    return ", ".join(top_amenities)



def plot_amenities_distribution(dataframe: pd.DataFrame, top_n: int = 15) -> go.Figure:
    amenities_counter = Counter()
    for amenities in dataframe['Amenidades']:
        if isinstance(amenities, list):
            amenities_counter.update(amenities)
    
    top_amenities = amenities_counter.most_common(top_n)
    amenities_data = pd.DataFrame(top_amenities, columns=['Amenidad', 'Cantidad'])
    
    if amenities_data.empty:
        return None
    
    fig_bar = px.bar(
        amenities_data.sort_values('Cantidad', ascending=True),
        x='Cantidad',
        y='Amenidad',
        orientation='h',
        title='Amenidades más Comunes',
        labels={'Cantidad': 'Número de Propiedades', 'Amenidad': ''},
        color_discrete_sequence=[PRIMARY_COLOR_1]
    )
    
    fig_bar.update_layout(
        showlegend=False,
        height=500,
        margin=dict(l=100, r=50, t=80, b=50)
    )
    
    fig_pie = px.pie(
        amenities_data,
        names='Amenidad',
        values='Cantidad',
        title='Distribución de Amenidades',
        hole=0.3
    )
    
    fig_pie.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>%{value} propiedades (%{percent})',
        marker=dict(colors=[PRIMARY_COLOR_1, PRIMARY_COLOR_2] + px.colors.sequential.Blues[2:])
    )
    
    fig_final = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "bar"}, {"type": "pie"}]],
        subplot_titles=('Top Amenidades', 'Distribución Porcentual'),
        horizontal_spacing=0.1
    )

    for trace in fig_bar.data:
        fig_final.add_trace(trace, row=1, col=1)
    
    fig_final.add_trace(fig_pie.data[0], row=1, col=2)
    
    fig_final.update_layout(
        title_text='Análisis de Amenidades',
        height=400,
        showlegend=False,
        margin=dict(t=100)
    )
    
    return fig_final

def plot_housing_construction(onei_data: json) -> go.Figure:
    construction_data = pd.DataFrame(onei_data['viviendas_terminadas'])
    
    fig = px.bar(
        construction_data, 
        x='año', 
        y='cantidad',
        title='Viviendas Terminadas en La Habana (2020-2024)',
        labels={'cantidad': 'Viviendas Terminadas', 'año': 'Año'},
        text='cantidad',
        color_discrete_sequence=[PRIMARY_COLOR_1]
    )
    
    fig.update_traces(
        textposition='outside',
        marker_line_color='black',
        marker_line_width=1
    )
    
    fig.update_layout(
        yaxis_range=[0, construction_data['cantidad'].max() + 1000],
        xaxis=dict(tickmode='linear')
    )
    return fig

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def plot_habana_map(dataframe: pd.DataFrame, geojson_path: str, category: str) -> px.choropleth:
    PRIMARY_COLOR = "#1b4a92"  
    SECONDARY_COLOR = "#e4ab0d" 
    BACKGROUND_COLOR = "#091b3f" 
    TEXT_COLOR = "#e4ab0d"  
    
    cat_map = {"Alquileres": "alquiler", "Ventas": "venta"}
    filtered_data = dataframe[dataframe["Categoria"] == cat_map[category]].copy()
    
    if len(filtered_data) < 3:
        fig = go.Figure()
        fig.add_annotation(
            text="⚠️ No hay suficientes datos para mostrar este mapa",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color=TEXT_COLOR))
        fig.update_layout(
            title=f"Precio Mediano de {category} por Municipio",
            paper_bgcolor=BACKGROUND_COLOR,
            plot_bgcolor=BACKGROUND_COLOR,
            font=dict(color=TEXT_COLOR)
        )
        return fig
    
    filtered_data["Municipio"] = filtered_data["Municipio"].apply(lambda x: remove_accents(x).lower().strip())
    
    median_price = filtered_data.groupby("Municipio", as_index=False)["Precio"].median()
    try:
        with open(geojson_path, encoding="utf-8") as f:
            geojson = json.load(f)
    except Exception as e:
        print(f"Error cargando GeoJSON: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error cargando GeoJSON: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=15, color=TEXT_COLOR))
        fig.update_layout(
            title=f"Precio Mediano de {category} por Municipio",
            paper_bgcolor=BACKGROUND_COLOR,
            plot_bgcolor=BACKGROUND_COLOR,
            font=dict(color=TEXT_COLOR))
        return fig
    
    for feature in geojson['features']:
        municipio_name = feature['properties']['municipality']
        feature['properties']['municipality_clean'] = remove_accents(municipio_name).lower().strip()
    
    fig = px.choropleth(
        median_price,
        geojson=geojson,
        locations="Municipio",
        featureidkey="properties.municipality_clean",
        color="Precio",
        color_continuous_scale=[PRIMARY_COLOR, SECONDARY_COLOR],  # Escala azul a dorado
        range_color=(median_price["Precio"].min(), median_price["Precio"].max()),
        labels={"Precio": "Precio Mediano (USD)"},
        title=f"Precio Mediano de {category} por Municipio",
        hover_data={"Municipio": True, "Precio": ":.0f"}
    )
    
    fig.update_traces(
        hovertemplate="<b>%{location}</b><br>Precio: $%{z:,.0f} USD<extra></extra>"
    )
    
    fig.update_geos(
        visible=False,
        center={"lat": 23.1136, "lon": -82.3666},
        projection_scale=9,
        fitbounds="locations",
        bgcolor=BACKGROUND_COLOR
    )
    
    fig.update_layout(
        margin={"r": 0, "t": 60, "l": 0, "b": 0},
        height=550,
        coloraxis_colorbar=dict(
            title="USD",
            thickness=15,
            len=0.75,
            tickformat=",",
            tickprefix="$",
            yanchor="middle",
            y=0.5
        ),
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        font=dict(color=TEXT_COLOR),
        title_font=dict(size=20, color=SECONDARY_COLOR),
        coloraxis_colorbar_title_side="right",
        annotations=[
            dict(
                x=0.5,
                y=-0.1,
                showarrow=False,
                text="Fuente: Análisis GAO | Datos 2024-2025",
                xref="paper",
                yref="paper",
                font=dict(size=12, color=TEXT_COLOR))
        ]
    )
    
    return fig