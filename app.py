import streamlit as st
import yfinance as yf
import numpy as np

st.set_page_config(page_title="Smart DCF Valuation Bot", layout="centered")

st.title("📊 Smart DCF Valuation Bot")
st.markdown("Enter a stock symbol and your DCF assumptions to calculate fair value.")

# User Inputs
ticker = st.text_input("Stock Symbol (e.g., TCS.NS for India, AAPL for US)", "TCS.NS")
growth_rate = st.number_input("Expected Annual FCF Growth Rate (%)", value=10.0) / 100
discount_rate = st.number_input("Discount Rate / WACC (%)", value=9.0) / 100
terminal_growth_rate = st.number_input("Terminal Growth Rate (%)", value=3.0) / 100
years = st.slider("Projection Years", 3, 10, 5)

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

