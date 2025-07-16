# 🤖 Streamlit App for Sophisticated DCF Valuation and EPS Projection
import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter

st.set_page_config(page_title="Investment Assistant", layout="wide")
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
    
    # Remove columns where first row is blank
    df_temp = pd.DataFrame(data_rows, columns=column_names)
    df_temp = df_temp.loc[:, df_temp.iloc[0].notna()]
    df_temp.fillna(0, inplace=True)
    return df_temp

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
        st.session_state["annual_pl"] = extract_table(df_all, "PROFIT & LOSS")
        st.session_state["balance_sheet"] = extract_table(df_all, "BALANCE SHEET")
        st.session_state["cashflow"] = extract_table(df_all, "CASH FLOW:" )
        st.session_state["quarterly"] = extract_table(df_all, "Quarters" )
        #st.session_state["quarterly"] = extract_quarterly(df_all)
        st.session_state["data_imported"] = True

    if st.session_state.get("data_imported"):
        st.success(f"✅ Data imported for: {st.session_state['company_name']}")
        st.session_state["forecast_years"] = st.number_input("Forecast Period (Years)", 1, 15, 5)
        
        df = st.session_state["annual_pl"].copy()
        df = df.set_index("Report Date")
        revenue_row = df.loc["Sales"].dropna()
        raw_material_cost = df.loc["Raw Material Cost"].dropna()
        inventory_cost = df.loc["Change in Inventory"].dropna()
        power_and_fule_cost = df.loc["Power and Fuel"].dropna()
        other_mfr_exp_cost = df.loc["Other Mfr. Exp"].dropna()
        emp_cost = df.loc["Employee Cost"].dropna()
        selling_and_admin_cost = df.loc["Selling and admin"].dropna()
        other_expenses_cost = df.loc["Other Expenses"].dropna()
         
        try:
            calculated_ebit = (revenue_row[-1] 
                                - raw_material_cost[-1]
                                - inventory_cost[-1]
                                - power_and_fule_cost[-1]
                                - other_mfr_exp_cost[-1]
                                - emp_cost[-1]
                                - selling_and_admin_cost[-1]
                                - other_expenses_cost[-1])
            latest_revenue = revenue_row[-1]
            calculated_ebit_margin = round((calculated_ebit / latest_revenue) * 100, 2)
        except:
            calculated_ebit = 0
            calculated_ebit_margin = 0

       # st.markdown(f"**Latest Calculated EBIT:** {calculated_ebit:,.2f} INR" if calculated_ebit is not None else "**Latest Calculated EBIT:** Not available")
       # st.markdown(f"**Latest Calculated EBIT Margin:** {calculated_ebit_margin}%" if calculated_ebit_margin is not None else "**Latest Calculated EBIT Margin:** Not available")

        st.session_state["ebit_margin"] = st.number_input("EBIT Margin (%)", value=calculated_ebit_margin, help=f"Last actual EBIT margin: {calculated_ebit_margin}%" if calculated_ebit_margin else "EBIT not found in data")

        depreciation_row = df.loc["Depreciation"] if "Depreciation" in df.index else None
        calculated_depr_pct = round((depreciation_row.values[-1] / revenue_row.values[-1]) * 100, 2) if depreciation_row is not None else 0
        st.session_state["depreciation_pct"] = st.number_input("Depreciation (% of Revenue)", value=calculated_depr_pct, help=f"Last actual depreciation ratio: {calculated_depr_pct}%" if calculated_depr_pct else "Depreciation not found in data")

        #capex_row = df.loc["Capital Expenditures"] if "Capital Expenditures" in df.index else None
        #calculated_capex_pct = round((capex_row.values[-1] / revenue_row.values[-1]) * 100, 2) if capex_row is not None else None
        st.session_state["capex_pct"] = st.number_input("CapEx (% of Revenue)", value=4.0, help=f"user need to update this")

        st.session_state["interest_pct"] = st.number_input("WACC (%)", value=10.0, help=f"user need to update this")
        st.session_state["wc_change_pct"] = st.number_input("Working Capital Changes as % of Revenue", value=2.0, help=f"user need to update this")

        tax_row = df.loc["Tax"] if "Tax" in df.index else None
        calculated_tax_pct = round((tax_row.values[-1] / calculated_ebit) * 100, 2) if tax_row is not None and calculated_ebit is not None else 0
        st.session_state["tax_rate"] = st.number_input("Corporate Tax Rate (%)", value= calculated_tax_pct , help=f"Last actual tax rate: {calculated_tax_pct}%" if calculated_tax_pct else "Tax not found in data")

        shares_row = st.session_state["balance_sheet"].copy()
        shares_row = shares_row.set_index("Report Date")
        share_cap = shares_row.loc["No. of Equity Shares"].dropna().values[-1]/10000000 if "No. of Equity Shares" in shares_row.index else 0
        st.session_state["shares_outstanding"] = st.number_input("Shares Outstanding (in Cr)", value=share_cap, help=f"Last actual equity share capital: {share_cap}" if share_cap else "Equity Share Capital not found")

        st.session_state["user_growth_rate_yr_1_2"] = st.number_input("Revenue Growth Rate for Projection for year 1 and 2 (%)", value=10.0)
        st.session_state["user_growth_rate_yr_3_4_5"] = st.number_input("Revenue Growth Rate for Projection for year 3, 4 and 5 and  (%)", value=10.0)
        st.session_state["user_growth_rate_yr_6_onwards"] = st.number_input("Revenue Growth Rate from year 6 onwards - terminal growth rate -  (%)", value= 4.0)

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
        wc_change_pct = st.session_state["wc_change_pct"]
        tax_rate = st.session_state["tax_rate"]
        shares = st.session_state["shares_outstanding"]
        growth_rate_1_2 = st.session_state["user_growth_rate_yr_1_2"]
        growth_rate_3_4_5 = st.session_state["user_growth_rate_yr_3_4_5"]
        growth_rate_6 =  st.session_state["user_growth_rate_yr_6_onwards"]
        terminal_growth = st.session_state["user_growth_rate_yr_6_onwards"]

        discount_factors = [(1 + interest_pct / 100) ** year for year in range(1, forecast_years + 1)]
        fcf_data = []
        ebit = base_revenue * (ebit_margin / 100)
        depreciation = base_revenue * (depreciation_pct / 100)
        tax = (ebit -depreciation)* (tax_rate / 100)
        nopat = ebit - tax
        fcf_data.append(["Year 0", base_revenue, nopat, depreciation, 0, 0, 0, 0])
        for year in range(1, forecast_years + 1):
            if year <=2 :
                revenue = revenue * (1 + growth_rate_1_2 / 100)
            elif year>2 and year <=5 :
                revenue = revenue * (1 + growth_rate_3_4_5 / 100)
            else :
                revenue = revenue * (1 + growth_rate_6 / 100)
            
            ebit = revenue * (ebit_margin / 100)
            
            depreciation = revenue * (depreciation_pct / 100)
            tax = (ebit -depreciation)* (tax_rate / 100)
            
            nopat = ebit - tax
            
            capex = revenue * (capex_pct / 100)
            wc_change = revenue * wc_change_pct/100
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
        growth_rate  = growth_rate_3_4_5
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

st.title("🤖 Stock Analysis Tool")
st.caption("📦 Version: 1.0 Stable")

