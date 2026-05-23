import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random

st.set_page_config(
    page_title="Binary Signals PRO",
    layout="wide"
)

st.title("📊 Binary Signals PRO")

# Atualização automática
st.markdown("""
<meta http-equiv="refresh" content="5">
""", unsafe_allow_html=True)

# =========================
# MERCADO SIMULADO
# =========================
def get_candles():

    base_price = 105000

    prices = [base_price]

    for _ in range(59):

        move = random.uniform(-300, 300)

        new_price = prices[-1] + move

        prices.append(new_price)

    df = pd.DataFrame({
        "close": prices
    })

    df["open"] = df["close"]

    df["high"] = (
        df["close"] +
        random.uniform(20, 100)
    )

    df["low"] = (
        df["close"] -
        random.uniform(20, 100)
    )

    return df


# =========================
# EMA
# =========================
def ema(data, period):

    alpha = 2 / (period + 1)

    result = data.iloc[0]

    for price in data:

        result = (
            alpha * price
            + (1 - alpha) * result
        )

    return result


# =========================
# RSI
# =========================
def rsi(data):

    gains = []

    losses = []

    for i in range(1, len(data)):

        diff = (
            data[i]
            - data[i - 1]
        )

        if diff > 0:
            gains.append(diff)

        else:
            losses.append(abs(diff))

    avg_gain = (
        np.mean(gains)
        if gains else 0
    )

    avg_loss = (
        np.mean(losses)
        if losses else 0
    )

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss

    return 100 - (
        100 / (1 + rs)
    )


# =========================
# EXECUÇÃO
# =========================
df = get_candles()

closes = df["close"]

ema9 = ema(
    closes[-9:],
    9
)

ema21 = ema(
    closes[-21:],
    21
)

rsi_val = rsi(
    closes.values
)

trend_strength = abs(
    ema9 - ema21
)

# =========================
# SINAIS
# =========================
signal = "⏳ AGUARDANDO"

if ema9 > ema21:
    signal = "📈 CALL"

elif ema9 < ema21:
    signal = "📉 PUT"

# =========================
# MÉTRICAS
# =========================
col1, col2, col3 = st.columns(3)

col1.metric(
    "RSI",
    f"{rsi_val:.2f}"
)

col2.metric(
    "EMA Spread",
    f"{trend_strength:.2f}"
)

col3.metric(
    "Sinal",
    signal
)

# =========================
# GRÁFICO
# =========================
fig = go.Figure()

fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="BTC"
    )
)

fig.update_layout(
    height=650,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.caption(
    f"Última atualização: "
    f"{datetime.now().strftime('%H:%M:%S')}"
)
