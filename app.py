import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Top 25 Stock Picks Potensial", layout="wide")

@st.cache_data

def load_data():
    url = "https://storage.googleapis.com/stock-csvku/hasil_gabungan.csv"
    df = pd.read_csv(url)
    df['Last Trading Date'] = pd.to_datetime(df['Last Trading Date'])
    return df

def analyze_stock_group(group, last_date):
    recent_30 = group[group['Last Trading Date'] >= last_date - pd.Timedelta(days=30)]
    recent_5 = group[group['Last Trading Date'] >= last_date - pd.Timedelta(days=5)]

    total_days = len(recent_30)
    if total_days == 0:
        return None

    akumulasi_signals = ['Akumulasi', 'Strong Akumulasi']
    akumulasi_ratio = (recent_30['Final Signal'].isin(akumulasi_signals).sum()) / total_days
    unusual_volume_5d = recent_5['Unusual Volume'].sum()
    avg_bid_offer = recent_30['Bid/Offer Imbalance'].mean()
    inflow_ratio = (recent_30['Foreign Flow'] == 'Inflow').sum() / total_days
    price_above_vwap = (recent_5['Close'] > recent_5['VWAP']).sum()

    score = 0
    score += 3 if akumulasi_ratio > 0.6 else 0
    score += 2 if unusual_volume_5d >= 2 else 0
    score += 2 if inflow_ratio > 0.5 else 0
    score += min(3, avg_bid_offer * 10) if avg_bid_offer > 0 else 0
    score += 1 if price_above_vwap >= 2 else 0

    return pd.Series({
        'Stock Code': group['Stock Code'].iloc[0],
        'Company Name': group['Company Name'].iloc[0],
        'Sector': group['Sector'].iloc[0],
        'Akumulasi Ratio (30d)': round(akumulasi_ratio, 2),
        'Inflow Ratio (30d)': round(inflow_ratio, 2),
        'Unusual Volume (5d)': unusual_volume_5d,
        'Avg Bid/Offer Imbalance (30d)': round(avg_bid_offer, 2),
        'Harga > VWAP (5d)': price_above_vwap,
        'Score': round(score, 2)
    })

# Load and process data
df = load_data()
last_date = df['Last Trading Date'].max()
top_stocks_df = df.groupby('Stock Code').apply(analyze_stock_group, last_date=last_date).dropna()
top_25 = top_stocks_df.sort_values(by='Score', ascending=False).head(25).reset_index(drop=True)

# UI Header
st.title("📈 Top 25 Stock Picks Potensial")
st.markdown("Saring saham berdasarkan fase akumulasi dominan dan sinyal volume mencurigakan terbaru.")

# Filter sektor
all_sectors = sorted(top_25['Sector'].dropna().unique())
selected_sector = st.selectbox("Filter berdasarkan sektor:", ["All"] + all_sectors)

if selected_sector != "All":
    filtered_data = top_25[top_25['Sector'] == selected_sector]
else:
    filtered_data = top_25

# Tampilkan data
st.dataframe(filtered_data, use_container_width=True)

# Opsi download
csv = filtered_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Top 25 sebagai CSV",
    data=csv,
    file_name='top25_stock_picks.csv',
    mime='text/csv',
)
