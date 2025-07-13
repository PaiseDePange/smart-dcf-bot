import streamlit as st
import yfinance as yf
import numpy as np

st.set_page_config(page_title="Smart DCF Valuation Bot", layout="centered")
st.title("📊 Smart DCF Valuation Bot")
st.markdown("Select a stock from the NSE 500 list and enter your DCF assumptions.")

# Sample NSE 500 dropdown list (extend this to full 500)
nse_500_list = [
    {"label": "Tata Consultancy Services (TCS.NS)", "ticker": "TCS.NS"},
    {"label": "Infosys Ltd (INFY.NS)", "ticker": "INFY.NS"},
    {"label": "Reliance Industries (RELIANCE.NS)", "ticker": "RELIANCE.NS"},
    {"label": "HDFC Bank Ltd (HDFCBANK.NS)", "ticker": "HDFCBANK.NS"},
    {"label": "ICICI Bank Ltd (ICICIBANK.NS)", "ticker": "ICICIBANK.NS"},
    {"label": "ITC Ltd (ITC.NS)", "ticker": "ITC.NS"},
    {"label": "Larsen & Toubro (LT.NS)", "ticker": "LT.NS"},
    {"label": "Axis Bank Ltd (AXISBANK.NS)", "ticker": "AXISBANK.NS"},
    {"label": "State Bank of India (SBIN.NS)", "ticker": "SBIN.NS"},
    {"label": "Hindustan Unilever (HINDUNILVR.NS)", "ticker": "HINDUNILVR.NS"},
]

# Dropdown UI
selected_label = st.selectbox("Select a company:", options=[x["label"] for x in nse_500_list])
ticker = next(x["ticker"] for x in nse_500_list if x["label"] == selected_label)

# Assumptions input
growth_rate = st.number_input("Expected Annual FCF Growth Rate (%)", value=10.0) / 100
discount_rate = st.number_input("Discount Rate / WACC (%)", value=9.0) / 100
terminal_growth_rate = st.number_input("Terminal Growth Rate (%)", value=3.0) / 100
years = st.slider("Projection Years", 3, 10, 5)

# Run DCF
if st.button("Calculate DCF"):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get("currentPrice", None)
        net_income = info.get("netIncomeToCommon", None)
        shares_outstanding = info.get("sharesOutstanding", None)

        if not all([current_price, net_income, shares_outstanding]):
            st.error("❌ Could not fetch sufficient data for this stock.")
        else:
            fcf_base = net_income * 0.8
            fcf_projections = [fcf_base * ((1 + growth_rate) ** year) for year in range(1, years + 1)]
            terminal_value = fcf_projections[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)

            discounted_fcf = [fcf / ((1 + discount_rate) ** i) for i, fcf in enumerate(fcf_projections, 1)]
            discounted_terminal_value = terminal_value / ((1 + discount_rate) ** years)
            dcf_value = sum(discounted_fcf) + discounted_terminal_value
            fair_value = dcf_value / shares_outstanding

            upside = ((fair_value - current_price) / current_price) * 100
            verdict = "🟢 Undervalued" if upside > 0 else "🔴 Overvalued"

            st.success("✅ DCF Valuation Complete!")
            st.metric("Current Price (INR)", f"₹{current_price:.2f}")
            st.metric("Fair Value (INR)", f"₹{fair_value:.2f}")
            st.metric("Upside Potential", f"{upside:.2f}% {verdict}")

    except Exception as e:
        st.error(f"❌ Error occurred: {str(e)}")
