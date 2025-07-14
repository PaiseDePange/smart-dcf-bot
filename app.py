# 🤖 Streamlit App for Sophisticated DCF Valuation
import streamlit as st

st.set_page_config(page_title="AI Investment Assistant", layout="wide")

st.title("🤖 AI-Powered Stock Analysis")

st.markdown("""
Welcome to your advanced DCF valuation model. Please provide the following inputs to generate a fair value estimate.
""")

st.header("📥 DCF Input Assumptions")

col1, col2 = st.columns(2)

with col1:
    forecast_years = st.number_input("Forecast Period (Years)", min_value=1, max_value=15, value=5)
    currency = st.selectbox("Currency", ["INR", "USD", "EUR", "GBP"])
    base_revenue = st.number_input("Base Year Revenue (in Cr or M)", min_value=0.0, value=1000.0)
    revenue_growth = st.slider("Revenue Growth Rate (%)", 0.0, 50.0, value=10.0)
    ebit_margin = st.slider("EBIT Margin (%)", 0.0, 100.0, value=20.0)
    depreciation_pct = st.slider("Depreciation (% of Revenue)", 0.0, 50.0, value=5.0)
    capex_pct = st.slider("CapEx (% of Revenue)", 0.0, 50.0, value=6.0)

with col2:
    wc_change_pct = st.slider("Change in Working Capital (% of Revenue)", -10.0, 10.0, value=1.0)
    tax_rate = st.slider("Corporate Tax Rate (%)", 0.0, 50.0, value=25.0)
    wacc = st.slider("WACC (%)", 0.0, 20.0, value=10.0)
    terminal_growth = st.slider("Terminal Growth Rate (%)", 0.0, 10.0, value=4.0)
    net_debt = st.number_input("Net Debt (Cash - Debt)", value=0.0)
    shares_outstanding = st.number_input("Shares Outstanding (in Cr or M)", value=10.0)

if st.button("💰 Calculate DCF"):
    st.success("✅ DCF calculation button clicked. Computation logic will go here.")
