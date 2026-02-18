import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

px.defaults.template = "plotly_white"

# Page config
st.set_page_config(page_title="Smart Micro-Manufacturing Operator Dashboard", layout="wide")

# Title
st.title("🏭 Smart Micro-Manufacturing Operator Dashboard")

# Data loading - assumes data.csv is in the same directory as dashboard.py
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    df = df.rename(columns={'Timestamp': 'DateTime'})
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df = df.sort_values('DateTime').set_index('DateTime')
    df = df.rename(columns={
        'Timestamp': 'DateTime',
        'Vibration Level (mm/s)': 'Vibration_Level',
        'Machine Speed (RPM)': 'Machine_Speed',
        'Production Quality Score': 'Production_Quality_Score',
        'Optimal Conditions': 'Optimal_Conditions',
        'Energy Consumption (kWh)': 'Energy_Consumption',
        'Temperature (°C)': 'Temperature'
    })
    return df

df = load_data()

# Sidebar for data info
with st.sidebar:
    st.header("📈 Data Overview")
    st.metric("Total Records", len(df))
    st.metric("Date Range", f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")

# Main dashboard
st.header("📊 Overview KPIs")

# Prepare data
df_dashboard = df.copy()
df_hourly = df_dashboard.resample('1h').mean()
df_dashboard['DateTime'] = df_dashboard.index

# Row 1: Key metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Production Quality", f"{df['Production_Quality_Score'].mean():.2f}")
col2.metric("Avg Machine Speed (RPM)", f"{df['Machine_Speed'].mean():.0f}")
col3.metric("Avg Energy (kWh)", f"{df['Energy_Consumption'].mean():.2f}")
col4.metric("Optimal Conditions %", f"{(df['Optimal_Conditions'].sum() / len(df) * 100):.1f}%")

# Row 2: Overview scatter plot
st.subheader("Operations Overview")
fig_scatter = px.scatter(
    df_dashboard,
    x='Machine_Speed',
    y='Production_Quality_Score',
    color='Optimal_Conditions',
    size='Energy_Consumption',
    hover_name='DateTime',
    title="Machine Speed vs Production Quality (colored by Optimal Conditions, sized by Energy)"
)
fig_scatter.update_layout(height=500)
st.plotly_chart(fig_scatter, use_container_width=True)

# Row 3: Trends over time (hourly aggregates)
st.subheader("Hourly Trends")
col5, col6 = st.columns(2)
with col5:
    fig_speed = px.line(df_hourly, x=df_hourly.index, y='Machine_Speed', title="Hourly Machine Speed")
    st.plotly_chart(fig_speed, use_container_width=True)
with col6:
    fig_quality = px.line(df_hourly, x=df_hourly.index, y='Production_Quality_Score', title="Hourly Production Quality")
    st.plotly_chart(fig_quality, use_container_width=True)

# Additional visualizations based on typical manufacturing dashboard elements
st.subheader("Sensor Metrics")
col7, col8, col9 = st.columns(3)
with col7:
    fig_vib = px.line(df_dashboard.tail(1000), x='DateTime', y='Vibration_Level', title="Recent Vibration Levels")
    st.plotly_chart(fig_vib, use_container_width=True)
with col8:
    fig_temp = px.line(df_dashboard.tail(1000), x='DateTime', y='Temperature', title="Recent Temperature")
    st.plotly_chart(fig_temp, use_container_width=True)
with col9:
    fig_energy = px.line(df_dashboard.tail(1000), x='DateTime', y='Energy_Consumption', title="Recent Energy Consumption")
    st.plotly_chart(fig_energy, use_container_width=True)

# Alerts section
st.subheader("🚨 Quick Alerts")
alert_conditions = {
    'High Vibration': (df['Vibration_Level'] > df['Vibration_Level'].quantile(0.95)).sum(),
    'Low Quality': (df['Production_Quality_Score'] < df['Production_Quality_Score'].quantile(0.05)).sum(),
    'High Energy': (df['Energy_Consumption'] > df['Energy_Consumption'].quantile(0.95)).sum()
}
for alert, count in alert_conditions.items():
    if count > 0:
        st.error(f"⚠️ {alert}: {count} occurrences")
    else:
        st.success(f"✅ {alert}: No issues")

# Raw data preview
with st.expander("View Raw Data (last 1000 rows)"):
    st.dataframe(df_dashboard.tail(1000))



