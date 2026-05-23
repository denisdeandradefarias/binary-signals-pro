import streamlit as st
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Binary Signals PRO",
    layout="wide"
)

st.title("📊 Binary Signals PRO - BTC M1 REAL")

placeholder = st.empty()

# =========================
# PREÇO REAL BTC (COINBASE)
# =========================
def get_price():

    url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"

    r = requests.get(url, timeout=5)
    data = r.json()

    return float(data["data"]["amount"])


# =========================
# INICIALIZA VELAS
# =========================
if "candles" not in st.session_state:

    price = get_price()

    st.session_state.candles = []

    for _ in range(20):

        st.session_state.candles.append({
            "open": price,
            "high": price,
            "low": price,
            "close": price
        })


if "current_candle" not in st.session_state:

    price = get_price()

    st.session_state.current_candle = {
        "open": price,
        "high": price,
        "low": price,
        "close": price,
        "start_time": time.time()
    }


# =========================
# EMA
# =========================
def ema(data, period):

    alpha = 2 / (period + 1)

    result = data[0]

    for price in data:

        result = alpha * price + (1 - alpha) * result

    return result


# =========================
# RSI
# =========================
def rsi(data):

    gains = []
    losses = []

    for i in range(1, len(data)):

        diff = data[i] - data[i - 1]

        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = np.mean(gains) if gains else 0
    avg_loss = np.mean(losses) if losses else 0

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


# =========================
# LOOP
# =========================
while True:

    price = get_price()

    candle = st.session_state.current_candle

    # atualizar candle atual
    candle["close"] = price
    candle["high"] = max(candle["high"], price)
    candle["low"] = min(candle["low"], price)

    # se passou 60s, fecha vela
    if time.time() - candle["start_time"] >= 60:

        st.session_state.candles.append({
            "open": candle["open"],
            "high": candle["high"],
            "low": candle["low"],
            "close": candle["close"]
        })

        st.session_state.candles = st.session_state.candles[-20:]

        st.session_state.current_candle = {
            "open": price,
            "high": price,
            "low": price,
            "close": price,
            "start_time": time.time()
        }

    # dataframe final
    df = pd.DataFrame(st.session_state.candles + [candle])

    closes = df["close"].values

    ema9 = ema(closes[-9:], 9)
    ema21 = ema(closes[-21:], 21)

    rsi_val = rsi(closes)

    # sinal
    if ema9 > ema21:
        signal = "📈 CALL"
        color = "#22C55E"
    else:
        signal = "📉 PUT"
        color = "#EF4444"

    with placeholder.container():

        col1, col2, col3 = st.columns(3)

        col1.metric("Preço BTC", f"${price:,.2f}")
        col2.metric("RSI", f"{rsi_val:.2f}")
        col3.metric("Sinal", signal)

        st.markdown(f"""
        <div style="
            background:{color};
            padding:20px;
            border-radius:15px;
            text-align:center;
            font-size:40px;
            font-weight:bold;
            color:white;
            margin-bottom:15px;
        ">
        {signal}
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"]
        ))

        fig.update_layout(
            height=700,
            xaxis_rangeslider_visible=False,
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font=dict(color="white")
        )

        # 20 velas estilo IQ
        fig.update_xaxes(range=[len(df)-20, len(df)])

        st.plotly_chart(fig, use_container_width=True)

        st.caption(f"Atualizado: {datetime.now().strftime('%H:%M:%S')}")

    time.sleep(2)
