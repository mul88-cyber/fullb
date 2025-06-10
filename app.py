import streamlit as st
import pandas as pd
import plotly.express as px

# 📥 Load Data
@st.cache_data
def load_data():
    return pd.read_csv("hasil_gabungan.csv", parse_dates=["Last Trading Date"])

df = load_data()

# 📊 Sidebar Filters
st.sidebar.header("📊 Filter Data")
weeks = sorted(df["Week"].dropna().unique())
sectors = sorted(df["Sector"].dropna().unique())
signals = sorted(df["Final Signal"].dropna().unique())

selected_week = st.sidebar.multiselect("Week", weeks, default=weeks)
selected_sector = st.sidebar.multiselect("Sector", sectors, default=sectors)
selected_signal = st.sidebar.multiselect("Final Signal", signals, default=signals)

# 🔍 Apply Filter
filtered_df = df[
    df["Week"].isin(selected_week) &
    df["Sector"].isin(selected_sector) &
    df["Final Signal"].isin(selected_signal)
]

st.title("📈 Dashboard Analisa Saham - Bandarmologi Edition")

# ⭐ Top 25 Stock Picks
st.subheader("⭐ Top 25 Stock Picks (Strong Akumulasi)")
top25_df = df[
    (df["Final Signal"] == "Strong Akumulasi") &
    (df["Volume"] > df["Volume"].median()) &
    (df["Close"] > df["VWAP"])
].sort_values(by=["Volume"], ascending=False).head(25)

st.dataframe(top25_df[["Stock Code", "Company Name", "Sector", "Final Signal", "Volume", "Close", "VWAP", "Foreign Buy", "Foreign Sell"]])

# 🔥 Heatmap Akumulasi
st.subheader("🔥 Heatmap Akumulasi / Distribusi")
pivot = filtered_df.pivot_table(index="Stock Code", columns="Week", values="Final Signal", aggfunc="first", fill_value="-")
st.dataframe(pivot)

# 📈 Grafik per Saham
st.subheader("📉 Grafik VWAP & Harga Penutupan")
selected_code = st.selectbox("Pilih Kode Saham", sorted(filtered_df["Stock Code"].unique()))
stock_df = df[df["Stock Code"] == selected_code].sort_values("Last Trading Date")

fig = px.line(stock_df, x="Last Trading Date", y=["Close", "VWAP"], title=f"{selected_code} - Close vs VWAP")
st.plotly_chart(fig)

# 📊 Data Table Interaktif
st.subheader("📋 Data Lengkap (Filter Aktif)")
st.dataframe(filtered_df)

# 💾 Download tombol
st.download_button("💾 Download Filtered Data", data=filtered_df.to_csv(index=False), file_name="filtered_data.csv")
st.download_button("⭐ Download Top 25 Stock Picks", data=top25_df.to_csv(index=False), file_name="top_25_picks.csv")
