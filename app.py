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

# --- INPUT TAB ---
with tabs[0]:
    st.header("Upload Excel File for EPS Projection")
    uploaded_file = st.file_uploader("Upload Screener Excel file", type=["xlsx"])

    import_btn = st.button("📥 Import Data")
    if import_btn and uploaded_file:
        df_all = pd.read_excel(uploaded_file, sheet_name="Data Sheet", header=None, engine="openpyxl")
        st.session_state["company_name"] = df_all.iloc[0, 1] if pd.notna(df_all.iloc[0, 1]) else "Unknown Company"
        st.session_state["annual_pl"] = extract_table(df_all, "Sales")
        st.session_state["balance_sheet"] = extract_table(df_all, "Equity Share Capital")
        st.session_state["cashflow"] = extract_table(df_all, "Cash from Operating Activity", header_offset=-1)
        st.session_state["quarterly"] = extract_quarterly(df_all)
        st.session_state["data_imported"] = True

    if st.session_state.get("data_imported"):
        st.subheader(f"🏢 Company: {st.session_state['company_name']}")
        st.success("✅ Data Imported Successfully! Please check 'Data Checks' tab for extracted tables.")

    st.header("📥 Projection Assumptions")
    col1, col2 = st.columns(2)

    with col1:
        forecast_years = st.number_input("Forecast Period (Years)", min_value=1, max_value=15, value=5)
        currency = st.selectbox("Currency", ["INR", "USD", "EUR", "GBP"])
        ebit_margin = st.number_input("EBIT Margin (%)", value=20.0)
        depreciation_pct = st.number_input("Depreciation (% of Revenue)", value=5.0)
        interest_pct = st.number_input("WACC (%)", value=10.0)

    with col2:
        tax_rate = st.number_input("Corporate Tax Rate (%)", value=25.0)
        shares_outstanding = st.number_input("Shares Outstanding (in Cr or M)", value=10.0)
        user_growth_rate = st.number_input("Revenue Growth Rate for Projection (%)", value=10.0)

# --- DCF TAB ---
with tabs[1]:
    if st.session_state.get("company_name"):
        st.subheader(f"🏢 Company: {st.session_state['company_name']}")

    st.header("💰 DCF Valuation")

    if st.button("💰 Calculate DCF"):
        if "annual_pl" not in st.session_state:
            st.error("❌ Please upload data first from the Inputs tab.")
        else:
            st.markdown("### Assumptions")
            st.markdown(f"- Forecast Period: **{forecast_years} years**")
            st.markdown(f"- Revenue Growth Rate: **{user_growth_rate}%**")
            st.markdown(f"- EBIT Margin: **{ebit_margin}%**, Depreciation: **{depreciation_pct}%**, WACC: **{interest_pct}%**")
            st.markdown(f"- Tax Rate: **{tax_rate}%**, Shares Outstanding: **{shares_outstanding}**")

            df = st.session_state["annual_pl"].copy()
            df = df.set_index("Report Date")
            revenue_row = df.loc["Sales"].dropna()
            revenue_values = revenue_row.values.astype(float)
            base_revenue = revenue_values[-1]

            revenue = base_revenue
            discount_factors = [(1 + interest_pct / 100) ** year for year in range(forecast_years + 1)]
            fcf_data = []

            for year in range(0, forecast_years + 1):
                if year > 0:
                    revenue *= (1 + user_growth_rate / 100)
                ebit = revenue * (ebit_margin / 100)
                tax = ebit * (tax_rate / 100)
                nopat = ebit - tax
                depreciation = revenue * (depreciation_pct / 100)
                capex = revenue * (depreciation_pct / 100)
                wc_change = revenue * 0.01
                fcf = nopat + depreciation - capex - wc_change
                pv_fcf = fcf / discount_factors[year] if year > 0 else fcf
                fcf_data.append([f"Year {year}", round(revenue, 2), round(nopat, 2), round(depreciation, 2), round(capex, 2), round(wc_change, 2), round(fcf, 2), round(pv_fcf, 2)])

            df_fcf = pd.DataFrame(fcf_data, columns=["Year", "Revenue", "NOPAT", "Depreciation", "CapEx", "Change in WC", "Free Cash Flow", "PV of FCF"])
            st.dataframe(df_fcf)

            st.subheader("📉 Terminal Value Calculation")
            final_fcf = fcf_data[-1][-2]
            if interest_pct > 4:
                terminal_value = (final_fcf * (1 + 4 / 100)) / ((interest_pct - 4) / 100)
                pv_terminal = terminal_value / discount_factors[-1]
            else:
                terminal_value = 0
                pv_terminal = 0
                st.warning("⚠️ WACC should be greater than terminal growth rate (4%) to compute terminal value.")

            st.markdown("**Terminal Value Formula:** Terminal FCF × (1 + g) / (WACC - g)")
            st.markdown(f"**Computed Terminal Value:** {currency} {terminal_value:,.2f}")
            st.markdown(f"**Discounted Terminal Value (PV):** {currency} {pv_terminal:,.2f}")

            st.subheader("🧮 Present Value Summary")
            total_pv_fcf = sum([row[-1] for row in fcf_data[1:]])
            enterprise_value = total_pv_fcf + pv_terminal
            equity_value = enterprise_value
            fair_value_per_share = equity_value / shares_outstanding

            st.markdown(f"**Sum of PV of Free Cash Flows (Years 1-{forecast_years}):** {currency} {total_pv_fcf:,.2f}")
            st.markdown(f"**Enterprise Value (FCF + Terminal):** {currency} {enterprise_value:,.2f}")
            st.markdown(f"**Equity Value (Enterprise - Net Debt):** {currency} {equity_value:,.2f}")
            st.success(f"🎯 Fair Value per Share: {currency} {fair_value_per_share:,.2f}")
