# 🤖 Streamlit App for Sophisticated DCF Valuation and EPS Projection
import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter

st.set_page_config(page_title="Investment Assistant", layout="wide")

st.title("🤖 Stock Analysis Tool")
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
    st.header("📥 Inputs")
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if uploaded_file and st.button("📥 Import Data"):
        df_all = pd.read_excel(uploaded_file, sheet_name="Data Sheet", header=None, engine="openpyxl")
        st.session_state["company_name"] = df_all.iloc[0, 1] if pd.notna(df_all.iloc[0, 1]) else "Unknown Company"
        st.session_state["annual_pl"] = extract_table(df_all, "Sales")
        st.session_state["balance_sheet"] = extract_table(df_all, "Equity Share Capital")
        st.session_state["cashflow"] = extract_table(df_all, "Cash from Operating Activity", header_offset=-1)
        st.session_state["quarterly"] = extract_quarterly(df_all)
        st.session_state["data_imported"] = True

    if st.session_state.get("data_imported"):
        st.success(f"✅ Data imported for: {st.session_state['company_name']}")
        st.session_state["forecast_years"] = st.number_input("Forecast Period (Years)", 1, 15, 5)

        df = st.session_state["annual_pl"].copy()
        df = df.set_index("Report Date")
        revenue_row = df.loc["Sales"].dropna()
        try:
            ebit_calc_row = (
                df.loc["Sales"]
                - df.loc.get("Raw Material Cost", 0)
                - df.loc.get("Change in Inventory", 0)
                - df.loc.get("Power and Fuel", 0)
                - df.loc.get("Other Mfr. Exp", 0)
                - df.loc.get("Employee Cost", 0)
                - df.loc.get("Selling and admin", 0)
                - df.loc.get("Other Expenses", 0)
            )
            calculated_ebit = ebit_calc_row.dropna().values[-1]
            calculated_ebit_margin = round((calculated_ebit / revenue_row.values[-1]) * 100, 2)
        except:
            calculated_ebit = None
            calculated_ebit_margin = None

        st.session_state["ebit_margin"] = st.number_input("EBIT Margin (%)", value=20.0, help=f"Last actual EBIT margin: {calculated_ebit_margin}%" if calculated_ebit_margin else "EBIT not found in data")

        depreciation_row = df.loc["Depreciation"] if "Depreciation" in df.index else None
        calculated_depr_pct = round((depreciation_row.values[-1] / revenue_row.values[-1]) * 100, 2) if depreciation_row is not None else None
        st.session_state["depreciation_pct"] = st.number_input("Depreciation (% of Revenue)", value=5.0, help=f"Last actual depreciation ratio: {calculated_depr_pct}%" if calculated_depr_pct else "Depreciation not found in data")

        capex_row = df.loc["Capital Expenditures"] if "Capital Expenditures" in df.index else None
        calculated_capex_pct = round((capex_row.values[-1] / revenue_row.values[-1]) * 100, 2) if capex_row is not None else None
        st.session_state["capex_pct"] = st.number_input("CapEx (% of Revenue)", value=6.0, help=f"Last actual CapEx ratio: {calculated_capex_pct}%" if calculated_capex_pct else "CapEx not found in data")

        st.session_state["interest_pct"] = st.number_input("WACC (%)", value=10.0)

        tax_row = df.loc["Tax"] if "Tax" in df.index else None
        calculated_tax_pct = round((tax_row.values[-1] / ebit_row.values[-1]) * 100, 2) if tax_row is not None and ebit_row is not None else None
        st.session_state["tax_rate"] = st.number_input("Corporate Tax Rate (%)", value=25.0, help=f"Last actual tax rate: {calculated_tax_pct}%" if calculated_tax_pct else "Tax not found in data")

        shares_row = st.session_state["balance_sheet"].copy()
        shares_row = shares_row.set_index("Report Date")
        share_cap = shares_row.loc["Equity Share Capital"].dropna().values[-1] if "Equity Share Capital" in shares_row.index else None
        st.session_state["shares_outstanding"] = st.number_input("Shares Outstanding (in Cr or M)", value=10.0, help=f"Last actual equity share capital: {share_cap}" if share_cap else "Equity Share Capital not found")

        st.session_state["user_growth_rate"] = st.number_input("Revenue Growth Rate for Projection (%)", value=10.0)
        st.session_state["terminal_growth"] = st.number_input("Terminal Growth Rate (%)", value=4.0)

# --- DCF TAB ---
with tabs[1]:
    st.header("💰 DCF Valuation")
    if st.session_state.get("data_imported") and st.button("Calculate DCF"):
        df = st.session_state["annual_pl"].copy()
        df = df.set_index("Report Date")
        revenue_row = df.loc["Sales"].dropna()
        revenue_values = revenue_row.values.astype(float)
        base_revenue = revenue_values[-1]

        revenue = base_revenue
        forecast_years = st.session_state["forecast_years"]
        ebit_margin = st.session_state["ebit_margin"]
        depreciation_pct = st.session_state["depreciation_pct"]
        capex_pct = st.session_state["capex_pct"]
        interest_pct = st.session_state["interest_pct"]
        tax_rate = st.session_state["tax_rate"]
        shares = st.session_state["shares_outstanding"]
        growth_rate = st.session_state["user_growth_rate"]
        terminal_growth = st.session_state["terminal_growth"]

        discount_factors = [(1 + interest_pct / 100) ** year for year in range(1, forecast_years + 1)]
        fcf_data = []
        fcf_data.append(["Year 0", base_revenue, 0, 0, 0, 0, 0, 0])
        for year in range(1, forecast_years + 1):
            revenue *= (1 + growth_rate / 100)
            ebit = revenue * (ebit_margin / 100)
            tax = ebit * (tax_rate / 100)
            nopat = ebit - tax
            depreciation = revenue * (depreciation_pct / 100)
            capex = revenue * (capex_pct / 100)
            wc_change = revenue * 0.01
            fcf = nopat + depreciation - capex - wc_change
            pv_fcf = fcf / discount_factors[year - 1]
            fcf_data.append([f"Year {year}", revenue, nopat, depreciation, capex, wc_change, fcf, pv_fcf])

        df_fcf = pd.DataFrame(fcf_data, columns=["Year", "Revenue", "NOPAT", "Depreciation", "CapEx", "Change in WC", "Free Cash Flow", "PV of FCF"])
        st.dataframe(df_fcf.style.format({
            "Revenue": "{:.2f}", "NOPAT": "{:.2f}", "Depreciation": "{:.2f}", "CapEx": "{:.2f}",
            "Change in WC": "{:.2f}", "Free Cash Flow": "{:.2f}", "PV of FCF": "{:.2f}"
        }))

        final_fcf = fcf_data[-1][-2]
        terminal_value = (final_fcf * (1 + terminal_growth / 100)) / ((interest_pct / 100) - (terminal_growth / 100))
        pv_terminal = terminal_value / ((1 + interest_pct / 100) ** forecast_years)

        total_pv_fcf = sum([row[-1] for row in fcf_data])
        enterprise_value = total_pv_fcf + pv_terminal
        equity_value = enterprise_value
        fair_value_per_share = equity_value / shares if shares else 0

        st.subheader("💡 Valuation Summary")
        st.markdown(f"**Enterprise Value:** {enterprise_value:,.2f} INR")
        st.markdown(f"**Equity Value:** {equity_value:,.2f} INR")
        st.markdown(f"**Fair Value per Share:** {fair_value_per_share:,.2f} INR")

        # Sensitivity Analysis
        st.subheader("📊 Sensitivity Analysis (Growth Rate ±5%)")
        growth_range = [growth_rate + delta for delta in range(-5, 6)]
        sensitivity = []
        for g in growth_range:
            rev = base_revenue
            fcf_vals = []
            for yr in range(1, forecast_years + 1):
                rev *= (1 + g / 100)
                ebit = rev * (ebit_margin / 100)
                tax = ebit * (tax_rate / 100)
                nopat = ebit - tax
                dep = rev * (depreciation_pct / 100)
                capex = rev * (capex_pct / 100)
                wc = rev * 0.01
                fcf = nopat + dep - capex - wc
                fcf_vals.append(fcf / ((1 + interest_pct / 100) ** yr))
            term_fcf = fcf_vals[-1] * ((1 + terminal_growth / 100) / ((interest_pct / 100) - (terminal_growth / 100)))
            pv_term = term_fcf / ((1 + interest_pct / 100) ** forecast_years)
            total_pv = sum(fcf_vals) + pv_term
            fair_val = total_pv / shares if shares else 0
            sensitivity.append({"Growth Rate (%)": g, "Fair Value/Share": round(fair_val, 2)})
        st.dataframe(pd.DataFrame(sensitivity))

# --- EPS TAB ---
with tabs[2]:
    st.header("📈 EPS Projection")
    if st.session_state.get("data_imported") and st.button("📊 Calculate EPS Projection"):
        df = st.session_state["annual_pl"].copy()
        df = df.set_index("Report Date")
        revenue_row = df.loc["Sales"].dropna()
        revenue_values = revenue_row.values.astype(float)
        base_revenue = revenue_values[-1]
        forecast_years = st.session_state["forecast_years"]
        ebit_margin = st.session_state["ebit_margin"]
        depreciation_pct = st.session_state["depreciation_pct"]
        capex_pct = st.session_state["capex_pct"]
        interest_pct = st.session_state["interest_pct"]
        tax_rate = st.session_state["tax_rate"]
        shares = st.session_state["shares_outstanding"]
        growth_rate = st.session_state["user_growth_rate"]

        eps_projection = []
        ebit_0 = base_revenue * (ebit_margin / 100)
        dep_0 = base_revenue * (depreciation_pct / 100)
        capex_0 = base_revenue * (capex_pct / 100)
        interest_0 = base_revenue * (interest_pct / 100)
        pbt_0 = ebit_0 - interest_0
        tax_0 = pbt_0 * (tax_rate / 100)
        pat_0 = pbt_0 - tax_0
        eps_0 = pat_0 / shares if shares else 0
        eps_projection.append(["Year 0", base_revenue, ebit_0, dep_0, capex_0, interest_0, pbt_0, tax_0, pat_0, eps_0])
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
            eps_projection.append([f"Year {year}", revenue, ebit, depreciation, capex, interest, pbt, tax, pat, eps])

        eps_df = pd.DataFrame(eps_projection, columns=["Year", "Revenue", "EBIT", "Depreciation", "CapEx", "Interest", "PBT", "Tax", "PAT", "EPS"])
        st.dataframe(eps_df.style.format({
            "Revenue": "{:.2f}", "EBIT": "{:.2f}", "Depreciation": "{:.2f}", "CapEx": "{:.2f}",
            "Interest": "{:.2f}", "PBT": "{:.2f}", "Tax": "{:.2f}", "PAT": "{:.2f}", "EPS": "{:.2f}"
        }))

# --- DATA CHECK TAB ---
with tabs[3]:
    st.header("🧾 Data Checks")
    if st.session_state.get("data_imported"):
        st.subheader("📊 Annual P&L")
        st.dataframe(st.session_state["annual_pl"])

        st.subheader("📋 Balance Sheet")
        st.dataframe(st.session_state["balance_sheet"])

        st.subheader("💸 Cash Flow")
        st.dataframe(st.session_state["cashflow"])

        st.subheader("📆 Quarterly Results")
        st.dataframe(st.session_state["quarterly"])
    else:
        st.info("Please upload a file from the Inputs tab and click 'Import Data'.")
