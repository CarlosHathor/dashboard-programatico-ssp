import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Programático El Español",
    page_icon="📊",
    layout="wide"
)

# CSS personalizado con colores de El Español
st.markdown("""
<style>
    .main-header {
        color: #C41E3A;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #C41E3A;
        margin: 0.5rem 0;
    }
    .alert-success {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #c3e6cb;
    }
    .alert-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #ffeaa7;
    }
    .alert-danger {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Función para generar datos de ejemplo
def generate_sample_data():
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')

    # Lista de todas las fuentes individuales
    sources = [
        'Google_AdEx', 'Google_OpenBidding',
        # Prebid SSPs
        'Prebid_Nexx360', 'Prebid_Richaudience', 'Prebid_AppNexus', 
        'Prebid_Ogury', 'Prebid_Criteo', 'Prebid_Optidigital',
        # TAM Partners
        'TAM_Amazon', 'TAM_IndexExchange', 'TAM_Outbrain', 
        'TAM_Pubmatic', 'TAM_Onetag', 'TAM_MediaNet', 'TAM_Equativ'
    ]

    data = []
    for date in dates:
        for source in sources:
            # Generar datos realistas según la fuente
            if 'Google' in source:
                base_revenue = np.random.normal(8000, 1500)
                base_impressions = np.random.normal(2000000, 300000)
            elif 'Prebid' in source:
                base_revenue = np.random.normal(3000, 800)
                base_impressions = np.random.normal(800000, 150000)
            else:  # TAM
                base_revenue = np.random.normal(2500, 600)
                base_impressions = np.random.normal(600000, 100000)

            revenue = max(0, base_revenue)
            impressions = max(1000, int(base_impressions))
            page_rpm = (revenue / impressions) * 1000 if impressions > 0 else 0
            fill_rate = np.random.uniform(75, 95)
            ecpm = (revenue / impressions) * 1000 if impressions > 0 else 0
            ctr = np.random.uniform(0.1, 2.5)

            data.append({
                'Fecha': date.strftime('%Y-%m-%d'),
                'Fuente': source,
                'Revenue': round(revenue, 2),
                'Impresiones': impressions,
                'Page_RPM': round(page_rpm, 2),
                'Fill_Rate': round(fill_rate, 2),
                'eCPM': round(ecpm, 2),
                'CTR': round(ctr, 2)
            })

    return pd.DataFrame(data)

# Función para validar datos
def validate_data(df):
    required_columns = ['Fecha', 'Fuente', 'Revenue', 'Impresiones', 'Page_RPM', 'Fill_Rate', 'eCPM', 'CTR']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        return False, f"Faltan las siguientes columnas: {', '.join(missing_columns)}"

    # Validar formatos
    try:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
    except:
        return False, "Error en formato de fechas. Use YYYY-MM-DD"

    numeric_columns = ['Revenue', 'Impresiones', 'Page_RPM', 'Fill_Rate', 'eCPM', 'CTR']
    for col in numeric_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return False, f"La columna {col} debe ser numérica"

    return True, "Datos válidos"

# Función para mostrar alertas
def show_alerts(df):
    alerts = []

    # Agrupar por fuente para calcular promedios
    source_metrics = df.groupby('Fuente').agg({
        'Fill_Rate': 'mean',
        'Revenue': 'sum',
        'eCPM': 'mean'
    }).round(2)

    for source, metrics in source_metrics.iterrows():
        if metrics['Fill_Rate'] < 80:
            alerts.append(('danger', f"⚠️ {source}: Fill Rate bajo ({metrics['Fill_Rate']:.1f}%)"))

        if metrics['eCPM'] < 1.0:
            alerts.append(('warning', f"⚡ {source}: eCPM bajo (${metrics['eCPM']:.2f})"))

    if not alerts:
        st.markdown('<div class="alert-success">✅ Todas las fuentes funcionan correctamente</div>', 
                   unsafe_allow_html=True)
    else:
        for alert_type, message in alerts:
            st.markdown(f'<div class="alert-{alert_type}">{message}</div>', 
                       unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">📊 Dashboard Programático El Español</h1>', 
           unsafe_allow_html=True)

# Sidebar para carga de datos
st.sidebar.header("📁 Gestión de Datos")

uploaded_file = st.sidebar.file_uploader(
    "Subir archivo CSV con datos",
    type=['csv'],
    help="Sube tu archivo CSV con las métricas de todas las fuentes programáticas"
)

# Checkbox para usar datos de ejemplo
use_sample = st.sidebar.checkbox(
    "Usar datos de ejemplo",
    value=not uploaded_file,
    help="Activa para ver el dashboard con datos de muestra"
)

# Cargar datos
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        is_valid, message = validate_data(df)

        if not is_valid:
            st.error(f"Error en los datos: {message}")
            st.stop()
        else:
            st.sidebar.success("✅ Datos cargados correctamente")
            df['Fecha'] = pd.to_datetime(df['Fecha'])
    except Exception as e:
        st.error(f"Error al cargar el archivo: {str(e)}")
        st.stop()
elif use_sample:
    df = generate_sample_data()
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    st.sidebar.info("📊 Usando datos de ejemplo")
else:
    st.warning("Por favor sube un archivo CSV o activa los datos de ejemplo")
    st.stop()

# Filtros
st.sidebar.header("🔍 Filtros")

# Filtro de fechas
date_range = st.sidebar.date_input(
    "Rango de fechas",
    value=[df['Fecha'].min().date(), df['Fecha'].max().date()],
    min_value=df['Fecha'].min().date(),
    max_value=df['Fecha'].max().date()
)

# Filtro de fuentes
all_sources = sorted(df['Fuente'].unique())
selected_sources = st.sidebar.multiselect(
    "Seleccionar fuentes",
    options=all_sources,
    default=all_sources
)

# Aplicar filtros
if len(date_range) == 2:
    filtered_df = df[
        (df['Fecha'].dt.date >= date_range[0]) & 
        (df['Fecha'].dt.date <= date_range[1]) &
        (df['Fuente'].isin(selected_sources))
    ]
else:
    filtered_df = df[df['Fuente'].isin(selected_sources)]

if filtered_df.empty:
    st.warning("No hay datos para los filtros seleccionados")
    st.stop()

# Sistema de alertas
st.header("🚨 Sistema de Alertas")
show_alerts(filtered_df)

# Métricas principales
st.header("📈 Métricas Principales")

col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered_df['Revenue'].sum()
total_impressions = filtered_df['Impresiones'].sum()
avg_page_rpm = (total_revenue / total_impressions) * 1000 if total_impressions > 0 else 0
avg_fill_rate = filtered_df['Fill_Rate'].mean()

with col1:
    st.metric(
        label="💰 Revenue Total",
        value=f"€{total_revenue:,.2f}",
        delta=f"{total_revenue*0.05:+,.2f}"
    )

with col2:
    st.metric(
        label="📊 Page RPM",
        value=f"€{avg_page_rpm:.2f}",
        delta=f"{avg_page_rpm*0.03:+,.2f}"
    )

with col3:
    st.metric(
        label="📍 Fill Rate",
        value=f"{avg_fill_rate:.1f}%",
        delta=f"{np.random.uniform(-2, 5):.1f}%"
    )

with col4:
    st.metric(
        label="💎 eCPM Promedio",
        value=f"€{filtered_df['eCPM'].mean():.2f}",
        delta=f"{filtered_df['eCPM'].mean()*0.02:+,.2f}"
    )

# Separadores por tecnología
st.header("🔧 Análisis por Tecnología")

# Crear tabs para cada tecnología
tab1, tab2, tab3 = st.tabs(["Google (AdEx & Open Bidding)", "Prebid SSPs", "Amazon TAM Partners"])

with tab1:
    google_data = filtered_df[filtered_df['Fuente'].str.contains('Google')]
    if not google_data.empty:
        google_metrics = google_data.groupby('Fuente').agg({
            'Revenue': 'sum',
            'Impresiones': 'sum',
            'Fill_Rate': 'mean',
            'eCPM': 'mean'
        }).round(2)

        st.subheader("Métricas Google")
        st.dataframe(google_metrics, use_container_width=True)

        # Gráfico de revenue por día
        daily_google = google_data.groupby(['Fecha', 'Fuente'])['Revenue'].sum().reset_index()
        fig_google = px.line(daily_google, x='Fecha', y='Revenue', color='Fuente',
                           title="Revenue Diario - Google AdEx vs Open Bidding")
        st.plotly_chart(fig_google, use_container_width=True)

with tab2:
    prebid_data = filtered_df[filtered_df['Fuente'].str.contains('Prebid')]
    if not prebid_data.empty:
        prebid_metrics = prebid_data.groupby('Fuente').agg({
            'Revenue': 'sum',
            'Impresiones': 'sum',
            'Fill_Rate': 'mean',
            'eCPM': 'mean'
        }).round(2)

        st.subheader("Métricas Prebid SSPs")
        st.dataframe(prebid_metrics, use_container_width=True)

        # Gráfico circular de distribución de revenue
        prebid_revenue = prebid_data.groupby('Fuente')['Revenue'].sum()
        fig_prebid = px.pie(values=prebid_revenue.values, names=prebid_revenue.index,
                           title="Distribución Revenue - Prebid SSPs")
        st.plotly_chart(fig_prebid, use_container_width=True)

with tab3:
    tam_data = filtered_df[filtered_df['Fuente'].str.contains('TAM')]
    if not tam_data.empty:
        tam_metrics = tam_data.groupby('Fuente').agg({
            'Revenue': 'sum',
            'Impresiones': 'sum',
            'Fill_Rate': 'mean',
            'eCPM': 'mean'
        }).round(2)

        st.subheader("Métricas Amazon TAM Partners")
        st.dataframe(tam_metrics, use_container_width=True)

        # Gráfico de barras comparativo
        fig_tam = px.bar(tam_metrics.reset_index(), x='Fuente', y='Revenue',
                        title="Revenue Total por TAM Partner")
        fig_tam.update_xaxis(tickangle=45)
        st.plotly_chart(fig_tam, use_container_width=True)

# Análisis comparativo general
st.header("📊 Análisis Comparativo General")

col1, col2 = st.columns(2)

with col1:
    # Top 10 fuentes por revenue
    top_sources = filtered_df.groupby('Fuente')['Revenue'].sum().sort_values(ascending=False).head(10)
    fig_top = px.bar(x=top_sources.values, y=top_sources.index, orientation='h',
                    title="Top 10 Fuentes por Revenue")
    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    # Evolución temporal del revenue total
    daily_total = filtered_df.groupby('Fecha')['Revenue'].sum().reset_index()
    fig_evolution = px.line(daily_total, x='Fecha', y='Revenue',
                           title="Evolución Revenue Total Diario")
    st.plotly_chart(fig_evolution, use_container_width=True)

# Tabla detallada por fuente
st.header("📋 Datos Detallados por Fuente")

detailed_metrics = filtered_df.groupby('Fuente').agg({
    'Revenue': ['sum', 'mean'],
    'Impresiones': 'sum',
    'Page_RPM': 'mean',
    'Fill_Rate': 'mean',
    'eCPM': 'mean',
    'CTR': 'mean'
}).round(2)

detailed_metrics.columns = ['Revenue Total', 'Revenue Promedio', 'Impresiones Total', 
                           'Page RPM', 'Fill Rate %', 'eCPM', 'CTR %']

st.dataframe(detailed_metrics, use_container_width=True)

# Exportar datos
st.header("📤 Exportar Datos")
csv_data = filtered_df.to_csv(index=False)
st.download_button(
    label="📥 Descargar datos filtrados (CSV)",
    data=csv_data,
    file_name=f"dashboard_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv"
)

# Footer
st.markdown("---")
st.markdown("**Dashboard Programático El Español** | Actualizado automáticamente | 📊 Versión SSP Individual")
