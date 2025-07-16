# 🤖 Streamlit App for Sophisticated DCF Valuation and EPS Projection (Layout Enhanced)
import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter

st.set_page_config(page_title="Smart Investing App", layout="wide")

st.title("🤖 Smart Investing App to model DCF and EPS")
st.caption("📦 Version: 1.0 Stable")

# Utility functions

def format_column_headers(headers):
    formatted = []
    for h in headers:
        try:
            h_parsed = pd.to_datetime(h)
            formatted.append(h_parsed.strftime("%b-%Y"))
        except:
            formatted.append(str(h) if pd.notnull(h) else "")
    counts = Counter()
    unique = []
    for h in formatted:
        counts[h] += 1
        unique.append(f"{h}_{counts[h]}" if counts[h] > 1 else h)
    return unique

def extract_table(df, start_label, col_count=11):
    start_row = df[df.iloc[:, 0] == start_label].index[0]
    header_row = start_row + 1
    headers_raw = df.iloc[header_row, 0:col_count].tolist()
    headers = format_column_headers(headers_raw)
    column_names = headers
    data_rows = []
    for i in range(start_row+2, df.shape[0]):
        row = df.iloc[i, 0:col_count]
        if row.isnull().all():
            break
        data_rows.append(row.tolist())

    df_temp = pd.DataFrame(data_rows, columns=column_names)
    df_temp = df_temp.loc[:, df_temp.iloc[0].notna()]
    df_temp.fillna(0, inplace=True)
    return df_temp

# Modularized DCF Calculation
def calculate_dcf(base_revenue, forecast_years, ebit_margin, depreciation_pct, capex_pct,
                  interest_pct, wc_change_pct, tax_rate, shares, growth_rate_1_2,
                  growth_rate_3_4_5, growth_rate_6):

    discount_factors = [(1 + interest_pct / 100) ** year for year in range(1, forecast_years + 1)]
    fcf_data = []
    revenue = base_revenue
    ebit = base_revenue * (ebit_margin / 100)
    depreciation = base_revenue * (depreciation_pct / 100)
    tax = (ebit - depreciation) * (tax_rate / 100)
    nopat = ebit - tax
    fcf_data.append(["Year 0", base_revenue, nopat, depreciation, 0, 0, 0, 0])

    for year in range(1, forecast_years + 1):
        if year <= 2:
            revenue *= (1 + growth_rate_1_2 / 100)
        elif year <= 5:
            revenue *= (1 + growth_rate_3_4_5 / 100)
        else:
            revenue *= (1 + growth_rate_6 / 100)

        ebit = revenue * (ebit_margin / 100)
        depreciation = revenue * (depreciation_pct / 100)
        tax = (ebit - depreciation) * (tax_rate / 100)
        nopat = ebit - tax
        capex = revenue * (capex_pct / 100)
        wc_change = revenue * wc_change_pct / 100
        fcf = nopat + depreciation - capex - wc_change
        pv_fcf = fcf / discount_factors[year - 1]
        fcf_data.append([f"Year {year}", revenue, nopat, depreciation, capex, wc_change, fcf, pv_fcf])

    return fcf_data

# Tabs for entire app
tabs = st.tabs(["\U0001F4E5 Inputs", "\U0001F4B0 DCF Valuation", "\U0001F4C8 EPS Projection", "\U0001F5FE Data Checks"])

# --- INPUT TAB ---
# [Unchanged code omitted for brevity]

# --- DCF TAB ---
with tabs[1]:
    st.header("\U0001F4B0 DCF Valuation")
    if st.session_state.get("data_imported") and st.button("Calculate DCF"):
        df = st.session_state["annual_pl"].copy().set_index("Report Date")
        revenue_row = df.loc["Sales"].dropna()
        base_revenue = revenue_row.values[-1]

        fcf_data = calculate_dcf(
            base_revenue=base_revenue,
            forecast_years=st.session_state["forecast_years"],
            ebit_margin=st.session_state["ebit_margin"],
            depreciation_pct=st.session_state["depreciation_pct"],
            capex_pct=st.session_state["capex_pct"],
            interest_pct=st.session_state["interest_pct"],
            wc_change_pct=st.session_state["wc_change_pct"],
            tax_rate=st.session_state["tax_rate"],
            shares=st.session_state["shares_outstanding"],
            growth_rate_1_2=st.session_state["user_growth_rate_yr_1_2"],
            growth_rate_3_4_5=st.session_state["user_growth_rate_yr_3_4_5"],
            growth_rate_6=st.session_state["user_growth_rate_yr_6_onwards"]
        )

        df_fcf = pd.DataFrame(fcf_data, columns=["Year", "Revenue", "NOPAT", "Depreciation", "CapEx", "Change in WC", "Free Cash Flow", "PV of FCF"])
        st.dataframe(df_fcf.style.format({
            "Revenue": "{:.2f}", "NOPAT": "{:.2f}", "Depreciation": "{:.2f}", "CapEx": "{:.2f}",
            "Change in WC": "{:.2f}", "Free Cash Flow": "{:.2f}", "PV of FCF": "{:.2f}"
        }))

        final_fcf = fcf_data[-1][-2]
        terminal_growth = st.session_state["user_growth_rate_yr_6_onwards"]
        interest_pct = st.session_state["interest_pct"]
        forecast_years = st.session_state["forecast_years"]
        shares = st.session_state["shares_outstanding"]

        terminal_value = (final_fcf * (1 + terminal_growth / 100)) / ((interest_pct / 100) - (terminal_growth / 100))
        pv_terminal = terminal_value / ((1 + interest_pct / 100) ** forecast_years)
        total_pv_fcf = sum(row[-1] for row in fcf_data[1:])
        enterprise_value = total_pv_fcf + pv_terminal
        equity_value = enterprise_value
        fair_value_per_share = equity_value / shares if shares else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Enterprise Value (INR)", f"{enterprise_value:,.2f}")
        col2.metric("Equity Value (INR)", f"{equity_value:,.2f}")
        col3.metric("Fair Value/Share", f"{fair_value_per_share:,.2f}")

# --- DATA CHECK TAB ---
# [Unchanged code omitted for brevity]

st.markdown("---")
st.caption("Made with ❤️ for smart investing.")
