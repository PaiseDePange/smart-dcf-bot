# 🤖 Streamlit App for Sophisticated DCF Valuation and EPS Projection
import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter

st.set_page_config(page_title="AI Investment Assistant", layout="wide")

st.title("🤖 AI-Powered Stock Analysis")

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

def extract_table(df, start_label, header_offset=-1, col_count=11):
    start_row = df[df.iloc[:, 0] == start_label].index[0]
    header_row = start_row + header_offset
    headers_raw = df.iloc[header_row, 1:col_count].tolist()
    headers = format_column_headers(headers_raw)
    column_names = ["Report Date"] + headers
    data_rows = []
    for i in range(start_row, df.shape[0]):
        row = df.iloc[i, 0:col_count]
        if row.isnull().all():
            break
        data_rows.append(row.tolist())
    return pd.DataFrame(data_rows, columns=column_names)

def extract_quarterly(df):
    quarters_row = df[df.iloc[:, 0] == "Quarters"].index[0]
    report_date_row = quarters_row + 1
    date_headers_raw = df.iloc[report_date_row, 1:11].tolist()
    date_headers = format_column_headers(date_headers_raw)
    column_headers = ["Report Date"] + date_headers
    data_rows = []
    for i in range(report_date_row + 1, df.shape[0]):
        row = df.iloc[i, 0:11]
        if row.isnull().all():
            break
        data_rows.append(row.tolist())
    return pd.DataFrame(data_rows, columns=column_headers)

# Tabs for entire app
tabs = st.tabs(["📥 Inputs", "💰 DCF Valuation", "📈 EPS Projection", "🧾 Data Checks"])

# --- EPS TAB ---
with tabs[2]:
    if st.session_state.get("company_name"):
        st.subheader(f"🏢 Company: {st.session_state['company_name']}")
    st.header("📈 EPS Projection")

    if st.session_state.get("data_imported"):
        if st.button("📊 Calculate EPS Projection"):
            df = st.session_state["annual_pl"].copy()
            df = df.set_index("Report Date")
            revenue_row = df.loc["Sales"].dropna()
            revenue_values = revenue_row.values.astype(float)
            base_revenue = revenue_values[-1]

            eps_projection = []
            revenue = base_revenue
            shares = st.session_state.get("shares_outstanding", 10.0)
            ebit_margin = st.session_state.get("ebit_margin", 20.0)
            depreciation_pct = st.session_state.get("depreciation_pct", 5.0)
            interest_pct = st.session_state.get("interest_pct", 10.0)
            tax_rate = st.session_state.get("tax_rate", 25.0)
            forecast_years = st.session_state.get("forecast_years", 5)
            growth_rate = st.session_state.get("user_growth_rate", 10.0)

            for year in range(1, forecast_years + 1):
                revenue *= (1 + growth_rate / 100)
                ebit = revenue * (ebit_margin / 100)
                depreciation = revenue * (depreciation_pct / 100)
                interest = revenue * (interest_pct / 100)
                pbt = ebit - interest
                tax = pbt * (tax_rate / 100)
                pat = pbt - tax
                eps = pat / shares if shares else 0
                eps_projection.append({
                    "Year": f"Year {year}",
                    "Revenue": round(revenue, 2),
                    "EBIT": round(ebit, 2),
                    "Depreciation": round(depreciation, 2),
                    "Interest": round(interest, 2),
                    "PBT": round(pbt, 2),
                    "Tax": round(tax, 2),
                    "PAT": round(pat, 2),
                    "EPS": round(eps, 2)
                })

            eps_df = pd.DataFrame(eps_projection)
            st.subheader("📋 Year-wise EPS Projection Table")
            st.dataframe(eps_df)

            st.markdown("---")
            st.markdown("**Methodology:**\n- Revenue is projected using user-defined growth rate.\n- EBIT is calculated from revenue and EBIT margin.\n- Depreciation and interest as % of revenue.\n- EPS = PAT / Shares Outstanding.")

# --- DATA CHECK TAB ---
with tabs[3]:
    if st.session_state.get("company_name"):
        st.subheader(f"🏢 Company: {st.session_state['company_name']}")
    st.header("🧾 Extracted Data Checks")

    if all(k in st.session_state for k in ["annual_pl", "balance_sheet", "cashflow", "quarterly"]):
        st.subheader("📊 Annual P&L")
        st.dataframe(st.session_state["annual_pl"])

        st.subheader("📋 Balance Sheet")
        st.dataframe(st.session_state["balance_sheet"])

        st.subheader("💸 Cash Flow")
        st.dataframe(st.session_state["cashflow"])

        st.subheader("📆 Quarterly P&L")
        st.dataframe(st.session_state["quarterly"])
    else:
        st.info("Please import a valid Excel file in the Inputs tab and click 'Import Data' to load tables.")
