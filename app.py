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
    st.header("📈 EPS Projection")
    if st.session_state.get("data_imported"):
        df = st.session_state["annual_pl"].copy()
        df = df.set_index("Report Date")
        revenue_row = df.loc["Sales"].dropna()
        capex_row = df.loc["Capital Expenditures"].dropna() if "Capital Expenditures" in df.index else None
        revenue_values = revenue_row.values.astype(float)
        base_revenue = revenue_values[-1]
        capex_values = capex_row.values.astype(float) if capex_row is not None else np.zeros_like(revenue_values)
        avg_capex_pct = round(np.mean(capex_values / revenue_values * 100), 2) if revenue_values.size == capex_values.size and revenue_values.all() else 6.0

        if "capex_pct" not in st.session_state:
            st.session_state["capex_pct"] = avg_capex_pct

        st.markdown("### Assumptions")
        st.markdown(f"- Forecast Years: **{st.session_state['forecast_years']}**")
        st.markdown(f"- Revenue Growth Rate: **{st.session_state['user_growth_rate']}%**")
        st.markdown(f"- EBIT Margin: **{st.session_state['ebit_margin']}%**")
        st.markdown(f"- Depreciation: **{st.session_state['depreciation_pct']}% of Revenue**")
        st.markdown(f"- CapEx: **{st.session_state['capex_pct']}% of Revenue**  _(Based on past avg: {avg_capex_pct}%)_")
        st.markdown(f"- WACC (used as Interest Proxy): **{st.session_state['interest_pct']}%**")
        st.markdown(f"- Tax Rate: **{st.session_state['tax_rate']}%**")
        st.markdown(f"- Shares Outstanding: **{st.session_state['shares_outstanding']}**")

        st.session_state["capex_pct"] = st.number_input("CapEx (% of Revenue)", value=st.session_state["capex_pct"], key="capex_input")

        if st.button("📊 Calculate EPS Projection"):
            forecast_years = st.session_state["forecast_years"]
            ebit_margin = st.session_state["ebit_margin"]
            depreciation_pct = st.session_state["depreciation_pct"]
            capex_pct = st.session_state["capex_pct"]
            interest_pct = st.session_state["interest_pct"]
            tax_rate = st.session_state["tax_rate"]
            shares = st.session_state["shares_outstanding"]
            growth_rate = st.session_state["user_growth_rate"]

            eps_projection = []
            revenue = base_revenue

            for year in range(1, forecast_years + 1):
                revenue *= (1 + growth_rate / 100)
                ebit = revenue * (ebit_margin / 100)
                depreciation = revenue * (depreciation_pct / 100)
                capex = revenue * (capex_pct / 100)
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
                    "CapEx": round(capex, 2),
                    "Interest (approx)": round(interest, 2),
                    "PBT": round(pbt, 2),
                    "Tax": round(tax, 2),
                    "PAT": round(pat, 2),
                    "EPS": round(eps, 2)
                })

            eps_df = pd.DataFrame(eps_projection)
            st.subheader("📋 Year-wise EPS Projection Table")
            st.dataframe(eps_df)
            st.markdown("---")
            st.markdown("**Methodology:**\n- Revenue is projected using user-defined growth rate.\n- EBIT is calculated from projected revenue and EBIT margin.\n- Depreciation, CapEx, and interest are estimated as % of revenue.\n- PBT and PAT are derived from EBIT and applied tax.\n- EPS = PAT / Shares Outstanding. Assumes no dilution.")
    else:
        st.warning("Please upload data in the Inputs tab to enable EPS projection.")
