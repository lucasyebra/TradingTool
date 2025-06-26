import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import numpy as np

API_KEY = "d1c2k5pr01qre5aj9rd0d1c2k5pr01qre5aj9rdg"

def buscar_empresa(nombre):
    nombre_limpio = nombre.lower()
    url = f"https://finnhub.io/api/v1/search?q={nombre_limpio}&token={API_KEY}"
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        resultados = respuesta.json().get("result", [])
        return [r for r in resultados if r["type"] == "Common Stock"]
    else:
        return []

def obtener_historial_yf(ticker, periodo):
    try:
        ticker_yf = yf.Ticker(ticker)
        df = ticker_yf.history(period=periodo)
        df.reset_index(inplace=True)
        return df
    except Exception as e:
        st.error(f"Error trying to get the information: {e}")
        return pd.DataFrame()

def calcular_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def seleccionar_rango(opciones_rango, valor_default):
    if "rango_seleccionado" not in st.session_state:
        st.session_state.rango_seleccionado = valor_default

    st.markdown("""
    <style>
        .stButton>button {
            background-color: #ffe6cc;
            color: black;
            border: none;
            border-radius: 10px;
            padding: 10px 0;
            margin: 0 4px;
            min-width: 110px;
            font-weight: normal;
            text-align: center;
            transition: all 0.2s ease;
            user-select:none;
        }
        .stButton>button:hover {
            background-color: #f4a261;
            color: white;
        }
        .selected-button {
            background-color: #f4a261 !important;
            color: white !important;
            font-weight: bold !important;
        }
        /* Centrar contenedor de botones */
        div[data-testid="stHorizontalBlock"] {
            justify-content: center !important;
        }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(opciones_rango))
    for i, (label, periodo) in enumerate(opciones_rango.items()):
        is_selected = (st.session_state.rango_seleccionado == periodo)
        btn = cols[i].button(label, key=f"rango_{periodo}")
        # Añadir clase CSS con JS para el botón seleccionado
        if is_selected:
            st.markdown(f"""
            <script>
                const btns = window.parent.document.querySelectorAll('button[kind="secondary"]');
                if(btns.length > {i}) {{
                    btns[{i}].classList.add("selected-button");
                }}
            </script>
            """, unsafe_allow_html=True)
        if btn:
            st.session_state.rango_seleccionado = periodo

    return st.session_state.rango_seleccionado

def run_app():
    st.title("📊 Financial Analyst App")

    nombre_empresa = st.text_input("🔍 Company")
    ticker = None
    resultados = []

    if nombre_empresa:
        resultados = buscar_empresa(nombre_empresa)

    if resultados:
        opciones = {f"{r['description']} ({r['symbol']})": r['symbol'] for r in resultados}
        seleccion = st.selectbox("Confirm Company:", list(opciones.keys()))
        ticker = opciones[seleccion]
        st.markdown(f"✅ Ticker selected: **{ticker}**")
    else:
        if nombre_empresa:
            st.warning("I could not find results. Try writing in another way")

    if ticker:
        opciones_rango = {
            "Year-To-Date": "ytd",
            "Último mes": "1mo",
            "Último trimestre": "3mo",
            "Último año": "1y",
            "Últimos 5 años": "5y",
            "Máximo": "max"
        }

        st.subheader("⏳ Seleccioná rango deseado")
        rango_seleccionado = seleccionar_rango(opciones_rango, "ytd")

        df_precio = obtener_historial_yf(ticker, rango_seleccionado)

        if not df_precio.empty:
            precio_inicio = df_precio["Close"].iloc[0]
            precio_fin = df_precio["Close"].iloc[-1]
            rendimiento = ((precio_fin - precio_inicio) / precio_inicio) * 100
            rendimiento_str = f"{rendimiento:.2f}%"
            color_rend = "green" if rendimiento > 0 else "red"

            # Opciones gráficas
            st.subheader("Chart configuration")
            mostrar_volumen = st.checkbox("Show Volume", value=True)
            mostrar_sma_20 = st.checkbox("Show SMA20", value=True)
            mostrar_sma_50 = st.checkbox("Show SMA50", value=False)
            mostrar_rsi = st.checkbox("Show RSI", value=False)
            tipo_grafico = st.selectbox("Kind of chart", ["Lines", "Candles"])

            fig = go.Figure()

            if tipo_grafico == "Lines":
                fig.add_trace(go.Scatter(
                    x=df_precio["Date"], y=df_precio["Close"],
                    mode='lines', name="Close Price",
                    line=dict(color='orange')
                ))
            else:  # Velas
                fig = go.Figure(data=[go.Candlestick(
                    x=df_precio["Date"],
                    open=df_precio["Open"],
                    high=df_precio["High"],
                    low=df_precio["Low"],
                    close=df_precio["Close"],
                    name="Candles"
                )])

            # Medias móviles
            if mostrar_sma_20:
                df_precio["SMA20"] = df_precio["Close"].rolling(window=20).mean()
                sma20_valid = df_precio.dropna(subset=["SMA20"])
                fig.add_trace(go.Scatter(
                    x=sma20_valid["Date"], y=sma20_valid["SMA20"],
                    mode='lines', name="SMA 20",
                    line=dict(dash='dash', color='blue')
                ))

            if mostrar_sma_50:
                df_precio["SMA50"] = df_precio["Close"].rolling(window=50).mean()
                sma50_valid = df_precio.dropna(subset=["SMA50"])
                fig.add_trace(go.Scatter(
                    x=sma50_valid["Date"], y=sma50_valid["SMA50"],
                    mode='lines', name="SMA 50",
                    line=dict(dash='dash', color='green')
                ))

            # Volumen
            if mostrar_volumen:
                fig.add_trace(go.Bar(
                    x=df_precio["Date"], y=df_precio["Volume"],
                    name="Volumen",
                    yaxis="y2",
                    marker_color='lightgray',
                    marker_line_color = 'gray',
                    marker_line_width = 1,
                    opacity=0.3
                ))

            # RSI
            if mostrar_rsi:
                df_precio["RSI"] = calcular_rsi(df_precio["Close"])
                fig.add_trace(go.Scatter(
                    x=df_precio["Date"], y=df_precio["RSI"],
                    mode='lines', name="RSI (14 días)",
                    yaxis="y3",
                    line=dict(color='purple')
                ))

            # Layout con 2 o 3 ejes Y según opciones
            layout = dict(
                title={
                    "text": f"📈 Closing Price - {ticker} ({rango_seleccionado.upper()})<br><span style='font-size:16px; color:{color_rend};'> Cumulative return: {rendimiento_str}</span>",
                    "x": 0.5,
                    "xanchor": "center"
                },
                yaxis=dict(domain=[0.4, 1], title="Price (USD)"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=100, b=50),
                hovermode="x unified"
            )

            if mostrar_volumen:
                layout["yaxis2"] = dict(
                    domain=[0.20, 0.40], anchor="x", title="Volumen", showgrid=False, zeroline=False
                )
            if mostrar_rsi:
                layout["yaxis3"] = dict(
                    domain=[0, 0.19], anchor="x", title="RSI", range=[0, 100]
                )

            fig.update_layout(layout)

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No se encontró información de precio histórico.")

        # Ratios financieros mejorados
        st.subheader("📊 Financial data and ratios")

        try:
            ticker_yf = yf.Ticker(ticker)
            info = ticker_yf.info
        except Exception as e:
            info = {}
            st.error(f"Error al obtener información financiera: {e}")

        ratios_a_mostrar = {
            "trailingPE": (
                "P/E (Price to earnings)",
                "This indicator shows how many times the stock price is paid relative to its earnings per share (EPS). "
                "A low P/E ratio may suggest that the stock is undervalued or that the company is facing issues. "
                "A high P/E ratio may indicate growth expectations, but also potential overvaluation."
            ),
            "returnOnEquity": (
                "ROE (Return on Equity)",
                "It measures the profitability a company generates with the money invested by its shareholders. "
                "A high ROE indicates that the company is efficiently using its equity to generate profits."
            ),
            "debtToEquity": (
                "Debt to Equity",
                "It measures the level of debt relative to equity. A high value means the company has significant debt, "
                "which can be risky if not properly managed."
            ),
            "profitMargins": (
                "Profit Margins",
                "It represents the percentage of net income over total revenue. A high margin indicates strong profitability and good cost control."
            ),
            "currentRatio": (
                "Current Ratio",
                "Ratio between current assets and current liabilities. It indicates the company’s ability to pay its short-term debts. "
                "A value greater than 1 is generally considered healthy."
            ),
            "priceToBook": (
                "P/B (Price to Book)",
                "This ratio compares the market price of a stock to its book value. A high P/B may signal overvaluation, while a low P/B could indicate a buying opportunity."
            ),
        }

        if info:
            cols = st.columns(3)
            idx = 0
            for key, (nombre, descripcion) in ratios_a_mostrar.items():
                valor = info.get(key)
                if valor is not None:
                    interpretacion = ""
                    if key == "trailingPE":
                        if valor < 10:
                            interpretacion = "✅  Possible undervaluation"
                        elif valor < 20:
                            interpretacion = "⚠️  Reasonable"
                        else:
                            interpretacion = "❌  Possible overvaluation"
                    elif key == "returnOnEquity":
                        if valor > 15:
                            interpretacion = "✅  Good use of capital"
                        elif valor > 5:
                            interpretacion = "⚠️  Acceptable"
                        else:
                            interpretacion = "❌  Low profitability"
                    elif key == "debtToEquity":
                        if valor < 0.5:
                            interpretacion = "✅  Low debt"
                        elif valor < 1.5:
                            interpretacion = "⚠️  Moderate"
                        else:
                            interpretacion = "❌  Financial risk"
                    elif key == "profitMargins":
                        if valor > 0.2:
                            interpretacion = "✅  High profitability"
                        elif valor > 0.1:
                            interpretacion = "⚠️  Acceptable"
                        else:
                            interpretacion = "❌  Low profitability"
                    elif key == "currentRatio":
                        if valor >= 1.5:
                            interpretacion = "✅  Good Liquidity"
                        elif valor >= 1.0:
                            interpretacion = "⚠️  Acceptable"
                        else:
                            interpretacion = "❌  Potential liquidity problems"
                    elif key == "priceToBook":
                        if valor < 1:
                            interpretacion = "✅  Potential undervaluation"
                        elif valor < 3:
                            interpretacion = "⚠️  Reasonable"
                        else:
                            interpretacion = "❌  Potential overvaluation"
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div style="
                            background-color: #fff3e0;
                            border-radius: 12px;
                            padding: 15px;
                            margin-bottom: 15px;
                            box-shadow: 2px 2px 6px rgba(244, 162, 97, 0.3);
                            user-select: none;
                            cursor: pointer;
                        ">
                            <strong style="font-size:18px; color:#e07a00;">{nombre}</strong><br>
                            <span style="font-size:24px; color:#f4a261;">{round(valor, 2)}</span>
                            <div style="font-size:13px; color:#555; margin-top:6px;">
                                {interpretacion}
                            </div>
                            <details style="margin-top: 10px; text-align: justify; font-size: 14px; color: #333;">
                                <summary style="cursor: pointer; font-weight: bold; color: #f4a261;">
                                    ¿Qué significa esto?
                                </summary>
                                <div style="padding: 8px 0 0 8px;">
                                    {descripcion}
                                </div>
                            </details>
                        </div>
                        """, unsafe_allow_html=True)
                idx += 1
    else:
        st.info("No se pudo obtener información financiera para este ticker.")

    # Reducir espacio extra abajo
    st.markdown("<style>footer {visibility: hidden;} .block-container {padding-bottom: 10px;}</style>", unsafe_allow_html=True)

if __name__ == "__main__":
    run_app()


