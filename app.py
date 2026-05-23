import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random
import time

st.set_page_config(
    page_title="Binary Signals PRO",
    layout="wide"
)

st.title("📊 Binary Signals PRO")

placeholder = st.empty()


# =========================
# MERCADO SIMULADO
# =========================
def get_candles():

    base_price = 105000

    prices = [base_price]

    # movimento mais forte
    for _ in range(59):

        move = random.uniform(-600, 600)

        new_price = (
            prices[-1] + move
        )

        prices.append(
            new_price
        )

    df = pd.DataFrame({
        "close": prices
    })

    # corpo maior
    body_size = np.random.uniform(
        80, 250, len(df)
    )

    direction = np.random.choice(
        [-1, 1],
        len(df)
    )

    df["open"] = (
        df["close"]
        + (body_size * direction)
    )

    # pavios maiores
    wick_top = np.random.uniform(
        80, 180, len(df)
    )

    wick_bottom = np.random.uniform(
        80, 180, len(df)
    )

    df["high"] = np.maximum(
        df["open"],
        df["close"]
    ) + wick_top

    df["low"] = np.minimum(
        df["open"],
        df["close"]
    ) - wick_bottom

    return df


# =========================
# EMA
# =========================
def ema(data, period):

    alpha = (
        2 / (period + 1)
    )

    result = data.iloc[0]

    for price in data:

        result = (
            alpha * price
            + (1 - alpha)
            * result
        )

    return result


# =========================
# RSI
# =========================
def rsi(data):

    gains = []
    losses = []

    for i in range(
        1,
        len(data)
    ):

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

    rs = (
        avg_gain /
        avg_loss
    )

    return (
        100
        - (100 / (1 + rs))
    )


# =========================
# LOOP SEM PISCAR
# =========================
while True:

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

    signal = "⏳ AGUARDANDO"

    if ema9 > ema21:
        signal = "📈 CALL"

    elif ema9 < ema21:
        signal = "📉 PUT"

    with placeholder.container():

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
            height=700,
            bargap=0.01,
            xaxis_rangeslider_visible=False
        )

        # mostrar só 20 velas
        fig.update_xaxes(
            range=[
                len(df) - 20,
                len(df)
            ]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            f"Última atualização: "
            f"{datetime.now().strftime('%H:%M:%S')}"
        )

    time.sleep(5)
