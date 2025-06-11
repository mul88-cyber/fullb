import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Setup page
st.set_page_config(page_title="Bandarmologi Dashboard", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stTabs [role="tablist"] { justify-content: center; }
    .stDataFrame { font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# --- Load data
@st.cache_data
def load_data():
    url = "https://storage.googleapis.com/stock-csvku/hasil_gabungan.csv"
    df = pd.read_csv(url)
    df['Last Trading Date'] = pd.to_datetime(df['Last Trading Date'])
    return df

df = load_data()
today = df['Last Trading Date'].max()

# --- Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 30 Hari", "📊 60 Hari", "📊 90 Hari", "📈 Grafik Volume & Harga"])

# --- Tab 1: 30 Hari
with tab1:
    st.subheader("📈 Top 25 Akumulasi - 30 Hari Terakhir")
    df_30 = df[df['Last Trading Date'] >= today - pd.Timedelta(days=30)].copy()

    if df_30.empty:
        st.warning("Tidak ada data dalam 30 hari terakhir.")
    else:
        grouped = df_30.groupby('Stock Code').agg({
            'Volume': 'sum',
            'Foreign Buy': 'sum',
            'Foreign Sell': 'sum',
            'Close': 'last'
        }).reset_index()
        grouped['Net Foreign'] = grouped['Foreign Buy'] - grouped['Foreign Sell']
        grouped['Inflow Ratio'] = grouped['Net Foreign'] / grouped['Volume'].replace(0, 1)
        top25 = grouped.sort_values('Inflow Ratio', ascending=False).head(25)

        st.dataframe(top25.style.format({
            'Volume': '{:,.0f}', 'Foreign Buy': '{:,.0f}', 'Foreign Sell': '{:,.0f}',
            'Net Foreign': '{:,.0f}', 'Inflow Ratio': '{:.2%}', 'Close': '{:,.2f}'
        }), use_container_width=True)

# --- Tab 2: 60 Hari
with tab2:
    st.subheader("📈 Top 25 Akumulasi - 60 Hari Terakhir")
    df_60 = df[df['Last Trading Date'] >= today - pd.Timedelta(days=60)].copy()

    if df_60.empty:
        st.warning("Tidak ada data dalam 60 hari terakhir.")
    else:
        grouped = df_60.groupby('Stock Code').agg({
            'Volume': 'sum',
            'Foreign Buy': 'sum',
            'Foreign Sell': 'sum',
            'Close': 'last'
        }).reset_index()
        grouped['Net Foreign'] = grouped['Foreign Buy'] - grouped['Foreign Sell']
        grouped['Inflow Ratio'] = grouped['Net Foreign'] / grouped['Volume'].replace(0, 1)
        top25 = grouped.sort_values('Inflow Ratio', ascending=False).head(25)

        st.dataframe(top25.style.format({
            'Volume': '{:,.0f}', 'Foreign Buy': '{:,.0f}', 'Foreign Sell': '{:,.0f}',
            'Net Foreign': '{:,.0f}', 'Inflow Ratio': '{:.2%}', 'Close': '{:,.2f}'
        }), use_container_width=True)

# --- Tab 3: 90 Hari
with tab3:
    st.subheader("📈 Top 25 Akumulasi - 90 Hari Terakhir")
    df_90 = df[df['Last Trading Date'] >= today - pd.Timedelta(days=90)].copy()

    if df_90.empty:
        st.warning("Tidak ada data dalam 90 hari terakhir.")
    else:
        grouped = df_90.groupby('Stock Code').agg({
            'Volume': 'sum',
            'Foreign Buy': 'sum',
            'Foreign Sell': 'sum',
            'Close': 'last'
        }).reset_index()
        grouped['Net Foreign'] = grouped['Foreign Buy'] - grouped['Foreign Sell']
        grouped['Inflow Ratio'] = grouped['Net Foreign'] / grouped['Volume'].replace(0, 1)
        top25 = grouped.sort_values('Inflow Ratio', ascending=False).head(25)

        st.dataframe(top25.style.format({
            'Volume': '{:,.0f}', 'Foreign Buy': '{:,.0f}', 'Foreign Sell': '{:,.0f}',
            'Net Foreign': '{:,.0f}', 'Inflow Ratio': '{:.2%}', 'Close': '{:,.2f}'
        }), use_container_width=True)

# --- Tab 4: Grafik Volume & Harga
with tab4:
    st.subheader("📉 Grafik Volume Saham & Harga Penutupan")

    stock_list = df['Stock Code'].dropna().unique().tolist()
    selected_stock = st.selectbox("Pilih Stock Code", sorted(stock_list))

    min_date = df['Last Trading Date'].min()
    max_date = df['Last Trading Date'].max()
    date_range = st.date_input("Pilih Rentang Tanggal", [min_date, max_date])

    df_stock = df[df['Stock Code'] == selected_stock].copy()
    df_stock = df_stock[
        (df_stock['Last Trading Date'] >= pd.to_datetime(date_range[0])) &
        (df_stock['Last Trading Date'] <= pd.to_datetime(date_range[1]))
    ].sort_values('Last Trading Date')

    if df_stock.empty:
        st.warning("Data kosong untuk rentang dan saham yang dipilih.")
    else:
        df_stock['Volume Non Foreign'] = df_stock['Volume'] - df_stock['Foreign Buy'] - df_stock['Foreign Sell']

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_stock['Last Trading Date'],
            y=df_stock['Volume Non Foreign'],
            name='Volume (Non Foreign)',
            marker_color='cornflowerblue',
        ))

        fig.add_trace(go.Bar(
            x=df_stock['Last Trading Date'],
            y=df_stock['Foreign Sell'],
            name='Foreign Sell',
            marker_color='gold',
        ))

        fig.add_trace(go.Bar(
            x=df_stock['Last Trading Date'],
            y=df_stock['Foreign Buy'],
            name='Foreign Buy',
            marker_color='limegreen',
        ))

        fig.add_trace(go.Scatter(
            x=df_stock['Last Trading Date'],
            y=df_stock['Close'],
            name='Close Price',
            mode='lines+markers',
            line=dict(color='black', dash='dot'),
            yaxis='y2'
        ))

        fig.update_layout(
            title=f"Volume dan Harga Penutupan Saham - {selected_stock}",
            xaxis=dict(title='Tanggal'),
            yaxis=dict(title='Volume'),
            yaxis2=dict(title='Close Price', overlaying='y', side='right'),
            barmode='stack',
            legend=dict(orientation='h', y=-0.3),
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)
