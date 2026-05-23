import streamlit as st
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Binary Signals PRO", layout="wide")

st.title("📊 Binary Signals PRO - Backtest Visual")

# Atualização automática a cada 5 segundos
st.markdown(
    """
    <meta http-equiv="refresh" content="5">
    """,
    unsafe_allow_html=True
)

# ==========================
# PEGAR CANDLES BINANCE
# ==========================
def get_candles():

    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=60"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            st.error(f"Erro Binance: {response.status_code}")
            return None

        data = response.json()

        df = pd.DataFrame(data, columns=[
            "time", "open", "high", "low", "close", "volume",
            "c1", "c2", "c3", "c4", "c5", "c6"
        ])

        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)

        return df

    except Exception as e:
        st.error(f"Erro ao conectar com Binance API: {e}")
        return None


# ==========================
# EMA
# ==========================
def ema(data, period):

    alpha = 2 / (period + 1)
    result = data.iloc[0]

    for price in data:
        result = alpha * price + (1 - alpha) * result

    return result


# ==========================
# RSI
# ==========================
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


# ==========================
# EXECUÇÃO
# ==========================
df = get_candles()

if df is not None:

    closes = df["close"]

    ema9 = ema(closes[-9:], 9)
    ema21 = ema(closes[-21:], 21)
    rsi_val = rsi(closes.values)

    trend_strength = abs(ema9 - ema21)

    signal = "NONE"

    if trend_strength > 20:

        if ema9 > ema21 and rsi_val > 55:
            signal = "CALL"

        elif ema9 < ema21 and rsi_val < 45:
            signal = "PUT"

    # ==========================
    # BACKTEST
    # ==========================
    win_points = []
    loss_points = []

    for i in range(21, len(closes) - 1):

        current = closes.iloc[:i]

        ema9_bt = ema(current[-9:], 9)
        ema21_bt = ema(current[-21:], 21)
        rsi_bt = rsi(current.values)

        entry = closes.iloc[i]
        future = closes.iloc[i + 1]

        if ema9_bt > ema21_bt and rsi_bt > 55:

            if future > entry:
                win_points.append(i)
            else:
                loss_points.append(i)

        elif ema9_bt < ema21_bt and rsi_bt < 45:

            if future < entry:
                win_points.append(i)
            else:
                loss_points.append(i)

    total_ops = len(win_points) + len(loss_points)

    winrate = (
        len(win_points) / total_ops * 100
        if total_ops > 0 else 0
    )

    # ==========================
    # MÉTRICAS
    # ==========================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("RSI", f"{rsi_val:.2f}")
    col2.metric("EMA Spread", f"{trend_strength:.2f}")
    col3.metric("Sinal", signal)
    col4.metric("Winrate", f"{winrate:.1f}%")

    # ==========================
    # GRÁFICO
    # ==========================
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="BTCUSDT"
    ))

    # WIN
    fig.add_trace(go.Scatter(
        x=win_points,
        y=[closes.iloc[i] for i in win_points],
        mode="markers",
        marker=dict(color="green", size=10),
        name="WIN"
    ))

    # LOSS
    fig.add_trace(go.Scatter(
        x=loss_points,
        y=[closes.iloc[i] for i in loss_points],
        mode="markers",
        marker=dict(color="red", size=10),
        name="LOSS"
    ))

    fig.update_layout(
        height=650,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        f"Última atualização: "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )
