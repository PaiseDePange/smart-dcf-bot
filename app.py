# 🤖 Streamlit App for Sophisticated DCF Valuation
import streamlit as st
import pandas as pd

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
    st.subheader("📊 Projected Free Cash Flows")

    revenue = base_revenue
    data = []
    for year in range(1, forecast_years + 1):
        revenue *= (1 + revenue_growth / 100)
        ebit = revenue * (ebit_margin / 100)
        tax = ebit * (tax_rate / 100)
        nopat = ebit - tax
        depreciation = revenue * (depreciation_pct / 100)
        capex = revenue * (capex_pct / 100)
        wc_change = revenue * (wc_change_pct / 100)
        fcf = nopat + depreciation - capex - wc_change
        data.append([f"Year {year}", round(revenue, 2), round(nopat, 2), round(depreciation, 2), round(capex, 2), round(wc_change, 2), round(fcf, 2)])

    df = pd.DataFrame(data, columns=["Year", "Revenue", "NOPAT", "Depreciation", "CapEx", "Change in WC", "Free Cash Flow"])
    st.dataframe(df)

    st.subheader("📉 Terminal Value Calculation")
    final_fcf = data[-1][-1]
    terminal_value = (final_fcf * (1 + terminal_growth / 100)) / (wacc / 100 - terminal_growth / 100)
    st.write(f"**Terminal Value:** {currency} {terminal_value:,.2f}")

    st.subheader("🧮 Present Value of Cash Flows")
    discount_factors = [(1 + wacc / 100) ** year for year in range(1, forecast_years + 1)]
    pv_fcfs = [data[i][-1] / discount_factors[i] for i in range(forecast_years)]
    pv_terminal = terminal_value / discount_factors[-1]
    total_value = sum(pv_fcfs) + pv_terminal
    equity_value = total_value - net_debt
    fair_value_per_share = equity_value / shares_outstanding

    st.write(f"**Enterprise Value:** {currency} {total_value:,.2f}")
    st.write(f"**Equity Value:** {currency} {equity_value:,.2f}")
    st.success(f"🎯 Fair Value per Share: {currency} {fair_value_per_share:,.2f}")
