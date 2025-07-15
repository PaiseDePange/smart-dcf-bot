# 🤖 Streamlit App for Sophisticated DCF Valuation and EPS Projection
import streamlit as st
import pandas as pd
import numpy as np

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
            formatted.append(h)
    return formatted

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

    st.header("📥 DCF Input Assumptions")
    col1, col2 = st.columns(2)

    with col1:
        forecast_years = st.number_input("Forecast Period (Years)", min_value=1, max_value=15, value=5)
        currency = st.selectbox("Currency", ["INR", "USD", "EUR", "GBP"])
        base_revenue = st.number_input("Base Year Revenue (in Cr or M)", min_value=0.0, value=1000.0)
        revenue_growth = st.number_input("Revenue Growth Rate (%)", value=10.0)
        ebit_margin = st.number_input("EBIT Margin (%)", value=20.0)
        depreciation_pct = st.number_input("Depreciation (% of Revenue)", value=5.0)
        capex_pct = st.number_input("CapEx (% of Revenue)", value=6.0)

    with col2:
        wc_change_pct = st.number_input("Change in Working Capital (% of Revenue)", value=1.0)
        tax_rate = st.number_input("Corporate Tax Rate (%)", value=25.0)
        wacc = st.number_input("WACC (%)", value=10.0)
        terminal_growth = st.number_input("Terminal Growth Rate (%)", value=4.0)
        net_debt = st.number_input("Net Debt (Cash - Debt)", value=0.0)
        shares_outstanding = st.number_input("Shares Outstanding (in Cr or M)", value=10.0)

    if uploaded_file:
        df_all = pd.read_excel(uploaded_file, sheet_name="Data Sheet", header=None)
        st.session_state["annual_pl"] = extract_table(df_all, "Sales")
        st.session_state["balance_sheet"] = extract_table(df_all, "Equity Share Capital")
        st.session_state["cashflow"] = extract_table(df_all, "Cash from Operating Activity", header_offset=-1)
        st.session_state["quarterly"] = extract_quarterly(df_all)
        st.success("✅ Data Imported Successfully! Please check 'Data Checks' tab for extracted tables.")

# --- DCF TAB ---
with tabs[1]:
    st.header("💰 DCF Valuation")

    if st.button("💰 Calculate DCF"):
        st.subheader("📊 Projected Free Cash Flows")

        revenue = base_revenue
        data = []
        discount_factors = [(1 + wacc / 100) ** year for year in range(1, forecast_years + 1)]
        for year in range(1, forecast_years + 1):
            revenue *= (1 + revenue_growth / 100)
            ebit = revenue * (ebit_margin / 100)
            tax = ebit * (tax_rate / 100)
            nopat = ebit - tax
            depreciation = revenue * (depreciation_pct / 100)
            capex = revenue * (capex_pct / 100)
            wc_change = revenue * (wc_change_pct / 100)
            fcf = nopat + depreciation - capex - wc_change
            pv_fcf = fcf / discount_factors[year - 1]
            data.append([f"Year {year}", round(revenue, 2), round(nopat, 2), round(depreciation, 2), round(capex, 2), round(wc_change, 2), round(fcf, 2), round(pv_fcf, 2)])

        df = pd.DataFrame(data, columns=["Year", "Revenue", "NOPAT", "Depreciation", "CapEx", "Change in WC", "Free Cash Flow", "PV of FCF"])
        st.dataframe(df)

        st.subheader("📉 Terminal Value Calculation")
        final_fcf = data[-1][-2]
        terminal_value = (final_fcf * (1 + terminal_growth / 100)) / (wacc / 100 - terminal_growth / 100)
        pv_terminal = terminal_value / discount_factors[-1]
        st.markdown(f"**Terminal Value Formula:** Terminal FCF × (1 + g) / (WACC - g)")
        st.markdown(f"**Computed Terminal Value:** {currency} {terminal_value:,.2f}")
        st.markdown(f"**Discounted Terminal Value (PV):** {currency} {pv_terminal:,.2f}")

        st.subheader("🧮 Present Value Summary")
        total_pv_fcf = sum([row[-1] for row in data])
        enterprise_value = total_pv_fcf + pv_terminal
        equity_value = enterprise_value - net_debt
        fair_value_per_share = equity_value / shares_outstanding

        st.markdown(f"**Sum of PV of Free Cash Flows (Years 1-{forecast_years}):** {currency} {total_pv_fcf:,.2f}")
        st.markdown(f"**Enterprise Value (FCF + Terminal):** {currency} {enterprise_value:,.2f}")
        st.markdown(f"**Equity Value (Enterprise - Net Debt):** {currency} {equity_value:,.2f}")
        st.success(f"🎯 Fair Value per Share: {currency} {fair_value_per_share:,.2f}")

        st.subheader("📊 Sensitivity Analysis")
        wacc_range = np.arange(wacc - 2, wacc + 3, 1)
        growth_range = np.arange(terminal_growth - 1, terminal_growth + 2, 0.5)
        sensitivity_data = []

        for g in growth_range:
            row = []
            for w in wacc_range:
                try:
                    term_val = (final_fcf * (1 + g / 100)) / ((w / 100) - (g / 100))
                    term_pv = term_val / ((1 + w / 100) ** forecast_years)
                    total_pv = total_pv_fcf + term_pv
                    equity_val = total_pv - net_debt
                    fair_val = equity_val / shares_outstanding
                    row.append(round(fair_val, 2))
                except:
                    row.append("-")
            sensitivity_data.append(row)

        sensitivity_df = pd.DataFrame(sensitivity_data, columns=[f"WACC {w:.1f}%" for w in wacc_range], index=[f"g {g:.1f}%" for g in growth_range])
        st.dataframe(sensitivity_df.style.format("{:.2f}"))

# --- EPS TAB ---
with tabs[2]:
    st.header("📈 EPS Projection Model")

    base_eps = st.number_input("Base Year EPS", value=50.0)
    eps_growth = st.number_input("EPS Growth Rate (%)", value=12.0)
    years = st.number_input("Projection Years", min_value=1, max_value=15, value=5)

    eps_data = []
    for year in range(1, years + 1):
        base_eps *= (1 + eps_growth / 100)
        eps_data.append((f"Year {year}", round(base_eps, 2)))

    eps_df = pd.DataFrame(eps_data, columns=["Year", "Projected EPS"])
    st.dataframe(eps_df)

# --- DATA CHECK TAB ---
with tabs[3]:
    st.header("🧾 Extracted Data Checks")

    if "annual_pl" in st.session_state:
        st.subheader("📊 Annual P&L")
        st.dataframe(st.session_state["annual_pl"])

        st.subheader("📋 Balance Sheet")
        st.dataframe(st.session_state["balance_sheet"])

        st.subheader("💸 Cash Flow")
        st.dataframe(st.session_state["cashflow"])

        st.subheader("📆 Quarterly P&L")
        st.dataframe(st.session_state["quarterly"])
    else:
        st.info("Please upload a valid Excel file in the Inputs tab to load data.")
