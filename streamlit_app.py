import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="CryptoPro Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- MOCK DATA ---
MOCK_COINS = pd.DataFrame([
    {"id": "bitcoin", "name": "BTC", "logo": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png", "amount": 0.25, "price": 58832, "change": -0.69},
    {"id": "ethereum", "name": "ETH", "logo": "https://assets.coingecko.com/coins/images/279/large/ethereum.png", "amount": 2.1, "price": 1578, "change": -0.24},
    {"id": "solana", "name": "SOL", "logo": "https://assets.coingecko.com/coins/images/4128/large/solana.png", "amount": 15, "price": 142, "change": 3.12},
])

TIMEFRAMES = {
    "1H": pd.DataFrame([{"time": "2025-09-05T01:00:00", "open": 58700, "high": 58800, "low": 58600, "close": 58750}]),
    "4H": pd.DataFrame([{"time": "2025-09-05", "open": 58500, "high": 59000, "low": 58400, "close": 58700}]),
    "1D": pd.DataFrame([
        {"time": "2025-09-01", "open": 58000, "high": 59000, "low": 57500, "close": 58832},
        {"time": "2025-09-02", "open": 58832, "high": 59500, "low": 58200, "close": 59200},
        {"time": "2025-09-03", "open": 59200, "high": 60000, "low": 58800, "close": 59450},
        {"time": "2025-09-04", "open": 59450, "high": 59800, "low": 59000, "close": 59100},
        {"time": "2025-09-05", "open": 59100, "high": 59500, "low": 58500, "close": 58700},
    ]),
    "1W": pd.DataFrame([{"time": "2025-09-01", "open": 57500, "high": 60000, "low": 57000, "close": 58700}]),
    "1M": pd.DataFrame([{"time": "2025-09-01", "open": 56000, "high": 60000, "low": 55000, "close": 58700}]),
}

WATCHLIST = MOCK_COINS[MOCK_COINS["name"]!= "SOL"]
RECENT_TX = pd.DataFrame([
    {"type": "Buy", "coin": "BTC", "amount": 0.01, "price": 58500, "time": "2h ago"},
    {"type": "Sell", "coin": "ETH", "amount": 0.5, "price": 1580, "time": "1d ago"},
])

MARKET_STATS = {"marketCap": "$2.31T", "volume24h": "$98.5B", "fearGreed": 62, "btcDominance": "58.2%"}

# --- 1. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("CryptoPro")
    nav = st.radio("Navigate", ["Dashboard", "Markets", "Watchlist", "Portfolio", "Settings"], label_visibility="collapsed")
    if nav!= "Dashboard":
        st.info(f"{nav} coming soon")
        st.stop()

# --- 5. SEARCH + PROFILE TOP BAR ---
col_search, col_bell, col_profile = st.columns([6, 1, 1])
with col_search:
    search = st.text_input("Search coins...", placeholder="Type BTC, ETH...", label_visibility="collapsed")
with col_bell:
    st.button("🔔", help="Notifications coming soon")
with col_profile:
    st.button("👤", help="Profile coming soon")

# --- FILTER COINS ---
filtered_coins = MOCK_COINS[MOCK_COINS["name"].str.contains(search.upper(), na=False)] if search else MOCK_COINS

st.title("CryptoPro Dashboard")

# --- 2. MARKET STATS BAR ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Market Cap", MARKET_STATS["marketCap"])
col2.metric("24h Volume", MARKET_STATS["volume24h"])
col3.metric("Fear & Greed", f'{MARKET_STATS["fearGreed"]} Greed', delta="Greed" if MARKET_STATS["fearGreed"] > 50 else "Fear")
col4.metric("BTC Dominance", MARKET_STATS["btcDominance"])

st.divider()

# --- PORTFOLIO + TOP GAINERS ---
col1, col2 = st.columns(2)
portfolio_value = (MOCK_COINS["amount"] * MOCK_COINS["price"]).sum()
col1.metric("Total Portfolio Value", f"${portfolio_value:,.2f}")
with col2:
    st.subheader("🔥 Top Gainers 24h")
    for _, c in MOCK_COINS.iterrows():
        color = "green" if c["change"] >= 0 else "red"
        st.markdown(f'{c["name"]} :<span style="color:{color}; font-weight:600">{c["change"]:+.2f}%</span>', unsafe_allow_html=True)

# --- COIN CARDS ---
for _, c in filtered_coins.iterrows():
    col_img, col_info, col_btn = st.columns([1, 6, 1])
    with col_img:
        st.image(c["logo"], width=40)
    with col_info:
        st.markdown(f'**{c["name"]}** <span style="color:{"green" if c["change"]>=0 else "red"}">{c["change"]:+.2f}%</span>', unsafe_allow_html=True)
        st.caption(f'${c["price"]:,.0f} · ${(c["amount"] * c["price"]):,.0f}')
    with col_btn:
        if st.button("🔔", key=f'bell_{c["id"]}', help=f"Set alert for {c['name']}"):
            st.toast(f"Price alert set for {c['name']}")

col_chart, col_pie = st.columns(2)

# --- 4. TIMEFRAME CHART ---
with col_chart:
    st.subheader("BTC/USD")
    timeframe = st.selectbox("Timeframe", ["1H", "4H", "1D", "1W", "1M"], label_visibility="collapsed")
    df = TIMEFRAMES[timeframe]
    fig = go.Figure(data=[go.Candlestick(x=df["time"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], increasing_line_color='#4ADE80', decreasing_line_color='#F87171')])
    fig.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# --- PORTFOLIO PIE ---
with col_pie:
    st.subheader("Portfolio Allocation")
    pie_data = MOCK_COINS.copy()
    pie_data["value"] = pie_data["amount"] * pie_data["price"]
    fig_pie = go.Figure(data=[go.Pie(labels=pie_data["name"], values=pie_data["value"], hole=0.3, marker_colors=["#22D3EE", "#A78BFA", "#FBBF24"])])
    fig_pie.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 3. WATCHLIST + TRANSACTIONS ---
col_watch, col_tx = st.columns(2)
with col_watch:
    st.subheader("⭐ Watchlist")
    st.dataframe(WATCHLIST[["name", "price"]].rename(columns={"name": "Coin", "price": "Price"}), hide_index=True, use_container_width=True)
with col_tx:
    st.subheader("📜 Recent Transactions")
    st.dataframe(RECENT_TX, hide_index=True, use_container_width=True)