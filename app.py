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
    # Make column names unique
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

# --- INPUT TAB ---
with tabs[0]:
    st.header("Upload Excel File for EPS Projection")
    uploaded_file = st.file_uploader("Upload Screener Excel file", type=["xlsx"])

    import_btn = st.button("📥 Import Data")
    if import_btn and uploaded_file:
        df_all = pd.read_excel(uploaded_file, sheet_name="Data Sheet", header=None, engine="openpyxl")
        st.session_state["annual_pl"] = extract_table(df_all, "Sales")
        st.session_state["balance_sheet"] = extract_table(df_all, "Equity Share Capital")
        st.session_state["cashflow"] = extract_table(df_all, "Cash from Operating Activity", header_offset=-1)
        st.session_state["quarterly"] = extract_quarterly(df_all)
        st.session_state["data_imported"] = True

    if "data_imported" in st.session_state:
        st.success("✅ Data Imported Successfully! Please check 'Data Checks' tab for extracted tables.")

    st.header("📥 DCF & EPS Input Assumptions")
    col1, col2 = st.columns(2)

    with col1:
        forecast_years = st.number_input("Forecast Period (Years)", min_value=1, max_value=15, value=5)
        currency = st.selectbox("Currency", ["INR", "USD", "EUR", "GBP"])
        base_revenue = st.number_input("Base Year Revenue (in Cr or M)", min_value=0.0, value=1000.0)
        revenue_growth = st.number_input("Revenue Growth Rate (%)", value=10.0)
        ebit_margin = st.number_input("EBIT Margin (%)", value=20.0)
        depreciation_pct = st.number_input("Depreciation (% of Revenue)", value=5.0)
        interest_pct = st.number_input("Interest Expense (% of Revenue)", value=1.0)
        eps_base = st.number_input("Base Year EPS", value=50.0)

    with col2:
        tax_rate = st.number_input("Corporate Tax Rate (%)", value=25.0)
        shares_outstanding = st.number_input("Shares Outstanding (in Cr or M)", value=10.0)

# --- EPS TAB ---
with tabs[2]:
    st.header("📈 Sophisticated EPS Projection")

    if st.button("📊 Calculate EPS Projection"):
        eps_projection = []
        revenue = base_revenue
        shares = shares_outstanding

        for year in range(1, forecast_years + 1):
            revenue *= (1 + revenue_growth / 100)
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
        st.markdown("**Methodology:**\n- Revenue is projected using the provided growth rate.\n- EBIT is calculated from projected revenue and EBIT margin.\n- Depreciation and interest are estimated as % of revenue.\n- PBT and PAT are derived from EBIT and applied tax.\n- EPS = PAT / Shares Outstanding. Assumes no dilution.")

# --- DATA CHECK TAB ---
with tabs[3]:
    st.header("🧾 Extracted Data Checks")

    if all(key in st.session_state for key in ["annual_pl", "balance_sheet", "cashflow", "quarterly"]):
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
