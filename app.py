import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Load data (ganti sesuai lokasi kamu)
@st.cache_data
def load_data():
    url = "https://storage.googleapis.com/stock-csvku/hasil_gabungan.csv"
    df = pd.read_csv(url)
    df['Last Trading Date'] = pd.to_datetime(df['Last Trading Date'])
    return df

df = load_data()

# --- Tabs
tab1, tab2, tab3, tab4 = st.tabs(["30 Hari", "60 Hari", "90 Hari", "Grafik Volume & Harga"])

with tab4:
    st.markdown("## 📊 Grafik Volume (Foreign, Non-Foreign) + Close Price")
    st.markdown("Visualisasi gabungan antara volume total (dibagi menjadi foreign & non-foreign) dan harga penutupan.")

    # Dropdown saham
    stock_list = df['Stock Code'].dropna().unique().tolist()
    selected_stock = st.selectbox("Pilih Stock Code", sorted(stock_list))

    # Rentang tanggal
    min_date = df['Last Trading Date'].min()
    max_date = df['Last Trading Date'].max()
    date_range = st.date_input("Pilih Rentang Tanggal", [min_date, max_date])

    # Filter dan olah data
    df_stock = df[df['Stock Code'] == selected_stock].copy()
    df_stock = df_stock[
        (df_stock['Last Trading Date'] >= pd.to_datetime(date_range[0])) &
        (df_stock['Last Trading Date'] <= pd.to_datetime(date_range[1]))
    ].sort_values('Last Trading Date')

    if df_stock.empty:
        st.warning("Data kosong untuk rentang dan saham yang dipilih.")
    else:
        # Hitung Volume Non-Foreign
        df_stock['Volume Non Foreign'] = df_stock['Volume'] - df_stock['Foreign Buy'] - df_stock['Foreign Sell']

        fig = go.Figure()

        # Bar volume - Non-Foreign (sisa volume)
        fig.add_trace(go.Bar(
            x=df_stock['Last Trading Date'],
            y=df_stock['Volume Non Foreign'],
            name='Volume (Non Foreign)',
            marker_color='cornflowerblue',
        ))

        # Bar volume - Foreign Sell
        fig.add_trace(go.Bar(
            x=df_stock['Last Trading Date'],
            y=df_stock['Foreign Sell'],
            name='Foreign Sell',
            marker_color='gold',
        ))

        # Bar volume - Foreign Buy
        fig.add_trace(go.Bar(
            x=df_stock['Last Trading Date'],
            y=df_stock['Foreign Buy'],
            name='Foreign Buy',
            marker_color='limegreen',
        ))

        # Line chart - Close Price
        fig.add_trace(go.Scatter(
            x=df_stock['Last Trading Date'],
            y=df_stock['Close'],
            name='Close Price',
            mode='lines+markers',
            line=dict(color='black', dash='dot'),
            yaxis='y2'
        ))

        fig.update_layout(
            title=f"Volume Saham dan Harga Penutupan - {selected_stock}",
            xaxis=dict(title='Tanggal'),
            yaxis=dict(title='Volume'),
            yaxis2=dict(title='Close Price', overlaying='y', side='right'),
            barmode='stack',
            legend=dict(orientation='h', y=-0.3),
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)
