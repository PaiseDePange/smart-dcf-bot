# 🤖 Streamlit App for Sophisticated DCF Valuation and EPS Projection

import streamlit as st
import pandas as pd
import numpy as np 
from collections import Counter

st.set_page_config(page_title="AI Investment Assistant", layout="wide")

st.title("🤖 AI-Powered Stock Analysis")

# Utility functions

def format_column_headers(headers): formatted = [] for h in headers: try: h_parsed = pd.to_datetime(h) formatted.append(h_parsed.strftime("%b-%Y")) except: formatted.append(str(h) if pd.notnull(h) else "") counts = Counter() unique = [] for h in formatted: counts[h] += 1 unique.append(f"{h}_{counts[h]}" if counts[h] > 1 else h) return unique

def extract_table(df, start_label, header_offset=-1, col_count=11): start_row = df[df.iloc[:, 0] == start_label].index[0] header_row = start_row + header_offset headers_raw = df.iloc[header_row, 1:col_count].tolist() headers = format_column_headers(headers_raw) column_names = ["Report Date"] + headers data_rows = [] for i in range(start_row, df.shape[0]): row = df.iloc[i, 0:col_count] if row.isnull().all(): break data_rows.append(row.tolist()) return pd.DataFrame(data_rows, columns=column_names)

def extract_quarterly(df): quarters_row = df[df.iloc[:, 0] == "Quarters"].index[0] report_date_row = quarters_row + 1 date_headers_raw = df.iloc[report_date_row, 1:11].tolist() date_headers = format_column_headers(date_headers_raw) column_headers = ["Report Date"] + date_headers data_rows = [] for i in range(report_date_row + 1, df.shape[0]): row = df.iloc[i, 0:11] if row.isnull().all(): break data_rows.append(row.tolist()) return pd.DataFrame(data_rows, columns=column_headers)

Tabs for entire app

tabs = st.tabs(["📥 Inputs", "💰 DCF Valuation", "📈 EPS Projection", "🧾 Data Checks"])

--- INPUT TAB ---

with tabs[0]: st.header("📥 Inputs") uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file and st.button("📥 Import Data"):
    df_all = pd.read_excel(uploaded_file, sheet_name="Data Sheet", header=None, engine="openpyxl")
    st.session_state["company_name"] = df_all.iloc[0, 1] if pd.notna(df_all.iloc[0, 1]) else "Unknown Company"
    st.session_state["annual_pl"] = extract_table(df_all, "Sales")
    st.session_state["balance_sheet"] = extract_table(df_all, "Equity Share Capital")
    st.session_state["cashflow"] = extract_table(df_all, "Cash from Operating Activity", header_offset=-1)
    st.session_state["quarterly"] = extract_quarterly(df_all)
    st.session_state["data_imported"] = True

if st.session_state.get("data_imported"):
    st.success("✅ Data Imported Successfully")
    st.session_state["forecast_years"] = st.number_input("Forecast Period (Years)", 1, 15, 5)
    st.session_state["currency"] = st.selectbox("Currency", ["INR", "USD", "EUR", "GBP"])
    st.session_state["ebit_margin"] = st.number_input("EBIT Margin (%)", value=20.0)
    st.session_state["depreciation_pct"] = st.number_input("Depreciation (% of Revenue)", value=5.0)
    st.session_state["interest_pct"] = st.number_input("WACC (%)", value=10.0)
    st.session_state["tax_rate"] = st.number_input("Corporate Tax Rate (%)", value=25.0)
    st.session_state["shares_outstanding"] = st.number_input("Shares Outstanding (in Cr or M)", value=10.0)
    st.session_state["user_growth_rate"] = st.number_input("Revenue Growth Rate for Projection (%)", value=10.0)

--- EPS TAB ---

with tabs[2]: st.header("📈 EPS Projection") if st.session_state.get("data_imported"): if st.button("📊 Calculate EPS Projection"): df = st.session_state["annual_pl"].copy() df = df.set_index("Report Date") revenue_row = df.loc["Sales"].dropna() revenue_values = revenue_row.values.astype(float) base_revenue = revenue_values[-1] forecast_years = st.session_state["forecast_years"] ebit_margin = st.session_state["ebit_margin"] depreciation_pct = st.session_state["depreciation_pct"] interest_pct = st.session_state["interest_pct"] tax_rate = st.session_state["tax_rate"] shares = st.session_state["shares_outstanding"] growth_rate = st.session_state["user_growth_rate"]

eps_projection = []
        revenue = base_revenue

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
        st.markdown("**Methodology:**\n- Revenue projected using defined growth.\n- EBIT from EBIT margin.\n- EPS from PAT / Shares Outstanding.")
else:
    st.warning("Please upload data in the Inputs tab to enable EPS projection.")

