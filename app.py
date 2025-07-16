# 🤖 Streamlit App for Sophisticated DCF Valuation and EPS Projection (Layout Enhanced)
import streamlit as st
import pandas as pd
import openpyxl
import numpy as np
from collections import Counter

st.set_page_config(page_title="Smart Investing App", layout="wide")

st.title("🤖 Smart Investing App to model DCF and EPS")
st.caption("📦 Version: 1.0 Stable")

# Utility functions

def format_column_headers(headers):
    formatted = []
    blank_counter = 1
    for h in headers:
        try:
            h_parsed = pd.to_datetime(h)
            formatted.append(h_parsed.strftime("%b-%Y"))
        except:
            if pd.notnull(h) and str(h).strip():
                formatted.append(str(h))
            else:
                formatted.append(f"Unnamed_{blank_counter}")
                blank_counter += 1
    counts = Counter()
    unique = []
    for h in formatted:
        counts[h] += 1
        unique.append(f"{h}_{counts[h]}" if counts[h] > 1 else h)
    return unique

def extract_table(df, start_label, start_row_offset, col_count=11):
    start_row = df[df.iloc[:, 0] == start_label].index[0]
    header_row = start_row + start_row_offset
    headers_raw = df.iloc[header_row, 0:col_count].tolist()
    headers = format_column_headers(headers_raw)
    column_names = headers
    data_rows = []
    for i in range(start_row+start_row_offset+1, df.shape[0]):
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
    tax = ebit * (tax_rate / 100)
    net_op_pat = ebit - tax
    fcf_data.append(["Year 0", base_revenue, ebit, tax, net_op_pat, depreciation, 0, 0, 0, 0])

    for year in range(1, forecast_years + 1):
        if year <= 2:
            revenue *= (1 + growth_rate_1_2 / 100)
        elif year <= 5:
            revenue *= (1 + growth_rate_3_4_5 / 100)
        else:
            revenue *= (1 + growth_rate_6 / 100)

        ebit = revenue * (ebit_margin / 100)
        depreciation = revenue * (depreciation_pct / 100)
        tax = ebit * (tax_rate / 100)
        net_op_pat = ebit - tax
        capex = revenue * (capex_pct / 100)
        wc_change = revenue * wc_change_pct / 100
        fcf = net_op_pat + depreciation - capex - wc_change
        pv_fcf = fcf / discount_factors[year - 1]
        fcf_data.append([f"Year {year}", revenue, ebit, tax, net_op_pat, depreciation, capex, wc_change, fcf, pv_fcf])

    return fcf_data

# Tabs for entire app
tabs = st.tabs(["\U0001F4E5 Inputs", "\U0001F4B0 DCF Valuation", "\U0001F4C8 EPS Projection", "\U0001F5FE Data Checks"])

# --- INPUT TAB ---
with tabs[0]:
    st.header("📥 Inputs")
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    if uploaded_file and st.button("📥 Import Data"):
        uploaded_file.seek(0)  # Reset pointer for pandas
    try:
        uploaded_file.seek(0)  # Ensure pointer is reset
        wb = openpyxl.load_workbook(uploaded_file, data_only=True)
        sheet = wb["Data Sheet"]
        data = list(sheet.values)
        df_all = pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Error reading Excel file: {e}")
        st.stop()

    if df_all.isna().sum().sum() > 50:
        st.warning("⚠️ Many empty cells found. If your sheet uses formulas, please ensure it was saved after calculation in Excel.")

    st.session_state["company_name"] = df_all.iloc[0, 1] if pd.notna(df_all.iloc[0, 1]) else "Unknown Company"
    st.session_state["annual_pl"] = extract_table(df_all, "PROFIT & LOSS", 1, 11)
    st.session_state["balance_sheet"] = extract_table(df_all, "BALANCE SHEET", 1, 11)
    st.session_state["cashflow"] = extract_table(df_all, "CASH FLOW:", 1, 11)
    st.session_state["quarterly"] = extract_table(df_all, "Quarters", 1, 11)
    st.session_state["meta"] = extract_table(df_all, "META", 0, 2)
    st.session_state["data_imported"] = True
    
    if st.session_state.get("data_imported"):
        st.markdown("""
        <div style='border: 1px solid #ddd; padding: 1rem; border-radius: 8px; background-color: #f9f9f9;'>
        💡 <strong>Note on Assumptions:</strong><br>
        Some of the input assumptions below are automatically calculated from the financial data you've uploaded. Others require your judgment.<br>
        If you're unsure about what values to use, you can ask <strong>ChatGPT</strong> for help! Just provide the <strong>company name</strong> along with supporting documents like <em>annual reports, earnings transcripts, or investor presentations</em>, and it can guide you toward reasonable and safe assumptions.
        </div>
        """, unsafe_allow_html=True)
        st.success(f"✅ Data imported for: {st.session_state['company_name']}")
        
        df = st.session_state["meta"].copy()
        df.columns = ["Label", "Value"]
        df = df.set_index("Label")
        current_price = float(df.loc["Current Price", "Value"])
        market_cap = float(df.loc["Market Capitalization", "Value"])
      
        df = st.session_state["balance_sheet"].copy().set_index("Report Date")
        share_outstanding_row = df.loc["No. of Equity Shares"].dropna()
        
        df = st.session_state["annual_pl"].copy().set_index("Report Date")
        revenue_row = df.loc["Sales"].dropna()
        tax_row = df.loc["Tax"].dropna()
        depreciation_row = df.loc["Depreciation"].dropna()
        try:
            calculated_ebit = revenue_row[-1] - sum(df.loc[row].dropna()[-1] for row in [
                "Raw Material Cost", "Change in Inventory", "Power and Fuel",
                "Other Mfr. Exp", "Employee Cost", "Selling and admin", "Other Expenses"] if row in df.index)
            latest_revenue = revenue_row[-1]
            calculated_ebit_margin = round((calculated_ebit / latest_revenue) * 100, 1)
            calculated_tax_rate = round((tax_row[-1]/calculated_ebit)*100,1)
            calculated_depreciation_rate = round((depreciation_row[-1]/latest_revenue)*100,1)
        except:
            calculated_ebit = 0
            calculated_ebit_margin = 0
            calculated_tax_rate = 0
        
        try:
              outstanding_shares = round(share_outstanding_row[-1]/10000000,2)
        except:
              outstanding_shares = 0
          
        with st.expander("🚀 Revenue Growth Assumptions"):
            st.markdown("""
                <div style='border: 1px solid #ddd; padding: 1rem; border-radius: 8px; background-color: #f9f9f9;'>
                💡 <strong>Please enter these assumptions based on your judgement:</strong><br>    
                </div>
                """, unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.session_state["user_growth_rate_yr_1_2"] = st.number_input("Growth Y1 & Y2 (%)", value=10.0, step=0.1, format="%.1f", help="Expected revenue growth for years 1 and 2")
            with col2:
                st.session_state["user_growth_rate_yr_3_4_5"] = st.number_input("Growth Y3 to Y5 (%)", value=10.0, step=0.1,help="Expected revenue growth for years 3 to 5")
            with col3:
                st.session_state["user_growth_rate_yr_6_onwards"] = st.number_input("Terminal Growth Rate (%)", value=4.0, step=0.1, help="Growth rate after forecast period")


        with st.expander("📊 Revenue & Cost Assumptions"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div style='border: 1px solid #ddd; padding: 1rem; border-radius: 8px; background-color: #f9f9f9;'>
                💡 <strong>These assumptions are calculated based on uploaded data, but you can change them if you want to!:<strong><br>    
                </div>
                """, unsafe_allow_html=True)
            
                st.session_state["ebit_margin"] = st.number_input("EBIT Margin (%)", value=calculated_ebit_margin, step=0.1, help=f"Last actual EBIT margin: {calculated_ebit_margin}%" if calculated_ebit_margin else "EBIT not found in data")
                st.session_state["depreciation_pct"] = st.number_input("Depreciation (% of Revenue)", value=calculated_depreciation_rate, step=0.1, help=f"Last actual depreciation ratio : {calculated_depreciation_rate}% or enter your assumption")
                st.session_state["tax_rate"] = st.number_input("Tax Rate (%) of EBIT", value = calculated_tax_rate, step=0.1, help=f"Last actual Tax rate % of EBIT :{calculated_tax_rate}%")
                st.session_state["shares_outstanding"] = st.number_input("Shares Outstanding (in Cr)", value=outstanding_shares, step=0.1, help=f"Last actual total number of outstanding equity shares : {outstanding_shares} ")                       

                
            with col2:
                st.markdown("""
                <div style='border: 1px solid #ddd; padding: 1rem; border-radius: 8px; background-color: #f9f9f9;'>
                💡 <strong>Update these assumptions based on your judgement:<strong><br>    
                </div>
                """, unsafe_allow_html=True)
            
                st.session_state["forecast_years"] = st.number_input("Forecast Period (Years)", 1, 15, 5, step=1,help="Projection time horizon for future FCF")
                st.session_state["interest_pct"] = st.number_input("WACC (%)", value=10.0, step=0.1, help="Weighted Average Cost of Capital to discount future cashflows")
                st.session_state["wc_change_pct"] = st.number_input("Working Capital Changes (% of Revenue)", value=2.0, step=0.1, help="Assumed working capital requirement as % of revenue")
                st.session_state["capex_pct"] = st.number_input("CapEx (% of Revenue)", value=2.0, step=0.1, help="User needs to update based on future CapEx plans")

# --- DCF TAB ---
with tabs[1]:
    st.header("\U0001F4B0 DCF Valuation")
    if st.session_state.get("data_imported") and st.button("Calculate DCF"):
        df = st.session_state["annual_pl"].copy().set_index("Report Date")
        revenue_row = df.loc["Sales"].dropna()
        base_revenue = revenue_row.values[-1]

        with st.expander("📋 Assumptions Used in DCF Calculation"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Base Revenue:** {base_revenue:,.2f}")
                st.write(f"**EBIT Margin (%):** {st.session_state['ebit_margin']}")
                st.write(f"**Tax Rate (% of EBIT):** {st.session_state['tax_rate']}")
                st.write(f"**No of Equity Shares :** {st.session_state['shares_outstanding']}")
            with col2:
                st.write(f"**Depreciation (% of Revenue):** {st.session_state['depreciation_pct']}")
                st.write(f"**CapEx (% of Revenue):** {st.session_state['capex_pct']}")
                st.write(f"**Change in WC (% of Revenue):** {st.session_state['wc_change_pct']}")
                st.write(f"**WACC (%):** {st.session_state['interest_pct']}")
                
            with col3:
                st.write(f"**Forecast Years:** {st.session_state['forecast_years']}")
                st.write(f"**Growth Rate for Year 1 and 2 (%):** {st.session_state['user_growth_rate_yr_1_2']}")
                st.write(f"**Growth Rate for Year 3, 4 and 5 (%):** {st.session_state['user_growth_rate_yr_3_4_5']}")
                st.write(f"**Growth Rate from year 6 onwards (%):** {st.session_state['user_growth_rate_yr_6_onwards']}")
        
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

        df_fcf = pd.DataFrame(fcf_data, columns=["Year", "Revenue", "EBIT", "Tax", "Net Operating PAT", "Depreciation", "CapEx", "Change in WC", "Free Cash Flow", "PV of FCF"])
        st.dataframe(df_fcf.style.format({
    "Revenue": "{:.2f}", "EBIT": "{:.2f}", "Tax": "{:.2f}", "Net Operating PAT": "{:.2f}", "Depreciation": "{:.2f}",
    "CapEx": "{:.2f}", "Change in WC": "{:.2f}", "Free Cash Flow": "{:.2f}", "PV of FCF": "{:.2f}"
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

        with st.expander("📘 Terminal Value Calculation Explained"):
            st.markdown(f"""
            **Formula:**

            \[
            	ext{{Terminal Value}} = rac{{FCF_{{final}} 	imes (1 + g)}}{{r - g}}
            \]

            **Where:**  
            - FCF_final = {final_fcf:,.2f}  
            - g (Terminal Growth Rate) = {terminal_growth}%  
            - r (WACC) = {interest_pct}%  

            **Terminal Value =** ₹ {terminal_value:,.2f}  
            **Present Value of Terminal Value =** ₹ {pv_terminal:,.2f}
            """)

        col1, col2, col3 = st.columns(3)
        col1.metric("Enterprise Value (INR)", f"{enterprise_value:,.2f}")
        col2.metric("Equity Value (INR)", f"{equity_value:,.2f}")
        col3.metric("Fair Value/Share", f"{fair_value_per_share:,.2f}")

        with st.expander("📊 Valuation Verdict Based on DCF", expanded=True):
  
          try:
              df_meta = st.session_state["meta"].copy()
              if df_meta.shape[1] == 2:
                  df_meta.columns = ["Label", "Value"]
                  df_meta = df_meta.set_index("Label")
                  current_price = float(df_meta.loc["Current Price", "Value"])
      
                  diff_pct = ((fair_value_per_share - current_price) / current_price) * 100
          
                  if diff_pct > 10:
                      st.markdown(f"""
                      <div style='background-color:#e6ffed;border-left:5px solid #2ecc71;padding:1em;border-radius:6px'>
                      ✅ <strong>The stock appears undervalued by {diff_pct:.1f}%</strong><br>
                      Current Price = ₹{current_price:.2f} <br>
                      DCF Fair Value = ₹{fair_value_per_share:.2f}
                      </div>
                      """, unsafe_allow_html=True)
                  elif diff_pct < -10:
                      st.markdown(f"""
                      <div style='background-color:#ffe6e6;border-left:5px solid #e74c3c;padding:1em;border-radius:6px'>
                      ❌ <strong>The stock appears overvalued by {abs(diff_pct):.1f}%</strong><br>
                      Current Price = ₹{current_price:.2f} <br>
                      DCF Fair Value = ₹{fair_value_per_share:.2f}
                      </div>
                      """, unsafe_allow_html=True)
                  else:
                      st.markdown(f"""
                      <div style='background-color:#f0f0f0;border-left:5px solid #7f8c8d;padding:1em;border-radius:6px'>
                      ⚖️ <strong>The stock appears fairly valued (±10%)</strong><br>
                      Current Price = ₹{current_price:.2f} <br>
                      DCF Fair Value = ₹{fair_value_per_share:.2f}
                      </div>
                      """, unsafe_allow_html=True)
              else:
                  st.warning("⚠️ Could not determine verdict. META sheet should have exactly 2 columns.")
          except Exception as e:
              st.warning(f"⚠️ Verdict unavailable. Error: {e}")
          
        def calculate_terminal_value(fcf, g, r, n):
            tv = (fcf * (1 + g / 100)) / ((r / 100) - (g / 100))
            return tv / ((1 + r / 100) ** n), tv
            
        def dcf_fair_value(base_revenue, forecast_years, ebit_margin, depreciation_pct, capex_pct, wc_change_pct,
            tax_rate, interest_pct, shares, growth_1_5, growth_6, terminal_growth):
            revenue = base_revenue    
            total_pv_fcf = 0
            for year in range(1, forecast_years + 1):
                revenue *= (1 + growth_1_5 / 100)
                ebit = revenue * (ebit_margin / 100)
                tax = ebit * (tax_rate / 100)
                dep = revenue * (depreciation_pct / 100)
                capex = revenue * (capex_pct / 100)
                wc = revenue * (wc_change_pct / 100)
                fcf = ebit - tax + dep - capex - wc
                pv_fcf = fcf / ((1 + interest_pct / 100) ** year)
                total_pv_fcf += pv_fcf
        
            final_fcf = fcf
            pv_terminal, terminal_val = calculate_terminal_value(final_fcf, terminal_growth, interest_pct, forecast_years)
            ev = total_pv_fcf + pv_terminal    
            fv_per_share = ev / shares if shares else 0
            terminal_weight = terminal_val / ev * 100 if ev else 0
            return fv_per_share, terminal_weight


            # ---- Sensitivity Tables ----
            st.subheader("📈 Sensitivity Analysis")
        
            base_revenue = revenue_row.values[-1]
            forecast_years = st.session_state["forecast_years"]
            shares = st.session_state["shares_outstanding"]
            tax_rate = st.session_state["tax_rate"]
            depreciation_pct = st.session_state["depreciation_pct"]
            capex_pct = st.session_state["capex_pct"]
            wc_change_pct = st.session_state["wc_change_pct"]
            ebit_margin = st.session_state["ebit_margin"]
            terminal_growth = st.session_state["user_growth_rate_yr_6_onwards"]
            wacc = st.session_state["interest_pct"]
        
            def style_fair(val):
                diff_pct = ((val - base_value) / base_value) * 100
                if diff_pct > 10:
                    return 'background-color:#e6ffed'  # green
                elif diff_pct < -10:
                    return 'background-color:#ffe6e6'  # red
                else:
                    return 'background-color:#f0f0f0'  # gray
        
            # 1️⃣ Table: Fair Value vs 5-Year Growth
            st.markdown("### 📊 Scenario 1: 5-Year Revenue Growth Rate Sensitivity")
            growth_scenarios = [5, 10, 14, 16, 25]
            data1 = []
            base_value, base_tv_weight = dcf_fair_value(base_revenue, forecast_years, ebit_margin, depreciation_pct,
                                        capex_pct, wc_change_pct, tax_rate, wacc, shares, 10, terminal_growth)
        
            for g in growth_scenarios:
                val, tv_pct = dcf_fair_value(base_revenue, forecast_years, ebit_margin, depreciation_pct,
                                        capex_pct, wc_change_pct, tax_rate, wacc, shares, g, terminal_growth)
                data1.append({"5Y Growth Rate": f"{g}%", "Fair Value (₹)": val, "Terminal % of EV": f"{tv_pct:.1f}%"})
        
            df1 = pd.DataFrame(data1)
            st.dataframe(df1.style.applymap(style_fair, subset=["Fair Value (₹)"]).format({"Fair Value (₹)": "₹{:.2f}"}))
        
            # 2️⃣ Table: WACC vs Terminal Growth
            st.markdown("### 📊 Scenario 2: WACC vs Terminal Growth")
            waccs = [7, 9, 11, 13]
            terminal_gs = [4, 7, 10, 12]
            matrix2 = []
            for w in waccs:
                row = []
                for tg in terminal_gs:
                    val, _ = dcf_fair_value(base_revenue, forecast_years, ebit_margin, depreciation_pct, capex_pct,
                                            wc_change_pct, tax_rate, w, shares, 10, tg)
                    row.append(val)
                matrix2.append(row)
        
            df2 = pd.DataFrame(matrix2, index=[f"{w}%" for w in waccs], columns=[f"{g}%" for g in terminal_gs])
            st.dataframe(df2.style.applymap(style_fair).format("₹{:.2f}"))
        
            # 3️⃣ Table: EBIT vs Terminal Growth
            st.markdown("### 📊 Scenario 3: EBIT Margin vs Terminal Growth")
            ebit_margins = [8, 12, 16, 20, 25]
            tg_values = [4, 7, 10, 12]
            matrix3 = []
            for em in ebit_margins:
                row = []
                for tg in tg_values:
                    val, _ = dcf_fair_value(base_revenue, forecast_years, em, depreciation_pct, capex_pct,
                                            wc_change_pct, tax_rate, wacc, shares, 10, tg)
                    row.append(val)
                matrix3.append(row)
        
            df3 = pd.DataFrame(matrix3, index=[f"{e}%" for e in ebit_margins], columns=[f"{g}%" for g in tg_values])
            st.dataframe(df3.style.applymap(style_fair).format("₹{:.2f}"))


# --- DATA CHECK TAB ---
with tabs[3]:
    st.header("🧾 Data Checks")
    if st.session_state.get("data_imported"):
        st.subheader("📌 Company Meta Info")
        st.dataframe(st.session_state["meta"])

        st.subheader("📊 Annual Profit & Loss")
        st.dataframe(st.session_state["annual_pl"])

        st.subheader("📆 Quarterly Results")
        st.dataframe(st.session_state["quarterly"])

        st.subheader("📋 Balance Sheet")
        st.dataframe(st.session_state["balance_sheet"])

        st.subheader("💸 Cash Flow Statement")
        st.dataframe(st.session_state["cashflow"])
    else:
        st.info("Please upload a file from the Inputs tab and click 'Import Data'.")

st.markdown("---")
st.caption("Made with ❤️ by Paise De Pange for Smart Investing.")
