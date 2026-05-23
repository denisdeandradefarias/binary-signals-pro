import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random
import time

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Binary Signals PRO",
    layout="wide"
)

# CSS estilo IQ Option
st.markdown("""
<style>

.stApp{
    background-color:#111827;
    color:white;
}

div[data-testid="metric-container"]{
    background:#1F2937;
    border-radius:15px;
    padding:15px;
    border:1px solid #2D3748;
}

h1{
    color:white !important;
    text-align:center;
}

</style>
""", unsafe_allow_html=True)

st.title("📈 Binary Signals PRO")

placeholder = st.empty()


# =========================
# MERCADO SIMULADO
# =========================
def get_candles():

    base_price = 105000

    candles = []

    current_price = base_price

    for _ in range(60):

        open_price = current_price

        move = random.uniform(
            -500,
            500
        )

        close_price = (
            open_price + move
        )

        high_price = max(
            open_price,
            close_price
        ) + random.uniform(
            50,
            200
        )

        low_price = min(
            open_price,
            close_price
        ) - random.uniform(
            50,
            200
        )

        candles.append({
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price
        })

        current_price = close_price

    return pd.DataFrame(candles)


# =========================
# EMA
# =========================
def ema(data, period):

    alpha = (
        2 /
        (period + 1)
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
        - (
            100 /
            (1 + rs)
        )
    )


# =========================
# LOOP
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

    signal = "⏳ AGUARDANDO"

    signal_color = "#FACC15"

    if ema9 > ema21:
        signal = "📈 CALL"
        signal_color = "#22C55E"

    elif ema9 < ema21:
        signal = "📉 PUT"
        signal_color = "#EF4444"

    with placeholder.container():

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "RSI",
            f"{rsi_val:.2f}"
        )

        col2.metric(
            "EMA 9/21",
            f"{abs(ema9-ema21):.2f}"
        )

        st.markdown(
            f"""
            <div style="
                background:{signal_color};
                padding:20px;
                border-radius:20px;
                text-align:center;
                font-size:38px;
                font-weight:bold;
                color:white;
                margin-top:10px;
                margin-bottom:20px;
            ">
            {signal}
            </div>
            """,
            unsafe_allow_html=True
        )

        fig = go.Figure()

        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],

                increasing=dict(
                    line=dict(
                        color="#22C55E",
                        width=2
                    ),
                    fillcolor="#22C55E"
                ),

                decreasing=dict(
                    line=dict(
                        color="#EF4444",
                        width=2
                    ),
                    fillcolor="#EF4444"
                )
            )
        )

        fig.update_layout(
            height=700,

            paper_bgcolor="#111827",
            plot_bgcolor="#111827",

            font=dict(
                color="white"
            ),

            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10
            ),

            xaxis_rangeslider_visible=False,

            xaxis=dict(
                showgrid=True,
                gridcolor="#1F2937"
            ),

            yaxis=dict(
                side="right",
                showgrid=True,
                gridcolor="#1F2937"
            )
        )

        # Mostrar só 20 velas
        fig.update_xaxes(
            range=[
                len(df)-20,
                len(df)
            ]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            f"Atualizado: "
            f"{datetime.now().strftime('%H:%M:%S')}"
        )

    time.sleep(5)
