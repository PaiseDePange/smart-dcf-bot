# 📥 Streamlit App to Fetch Company Filings (Using NSE)
import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Company Filings Fetcher", layout="centered")
st.title("📂 Company Filings Dashboard")
st.markdown("Enter an Indian listed company name (e.g. TCS) to fetch its recent NSE filings:")

company_input = st.text_input("Company Name (e.g. TCS, INFY, HDFC Bank)", "TCS")

# Map known company short names to NSE symbols (expandable dictionary)
company_map = {
    "TCS": {"symbol": "TCS", "name": "Tata Consultancy Services"},
    "INFY": {"symbol": "INFY", "name": "Infosys Ltd"},
    "RELIANCE": {"symbol": "RELIANCE", "name": "Reliance Industries"},
    "HDFCBANK": {"symbol": "HDFCBANK", "name": "HDFC Bank"},
    "ITC": {"symbol": "ITC", "name": "ITC Ltd"},
}

if company_input.upper() in company_map:
    symbol = company_map[company_input.upper()]["symbol"]
    company_display = company_map[company_input.upper()]["name"]
    st.subheader(f"📁 Latest NSE Filings for {company_display}")

    # NSE Corporate Filings page
    nse_url = f"https://www.nseindia.com/api/corporate-announcements?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": f"https://www.nseindia.com/companytracker/cmtracker.jsp?symbol={symbol}&cName=cmtracker&segmentLink=17"
    }

    try:
        response = requests.get(nse_url, headers=headers, timeout=10)
        data = response.json()
        announcements = data.get("data", [])

        ar_links = []
        call_links = []
        pres_links = []
        qr_links = []

        for item in announcements:
            desc = item.get("headline", "").lower()
            link = item.get("pdfUrl", "")
            if "annual report" in desc:
                ar_links.append(link)
            elif "earnings call" in desc or "conference call" in desc:
                call_links.append(link)
            elif "investor presentation" in desc:
                pres_links.append(link)
            elif "financial result" in desc:
                qr_links.append(link)

        st.markdown("### 📄 Annual Reports")
        for url in ar_links[:2]:
            st.markdown(f"- [Download]({url})")

        st.markdown("### 🗣️ Earnings Call Transcripts")
        for url in call_links[:4]:
            st.markdown(f"- [Download]({url})")

        st.markdown("### 🖼️ Investor Presentations")
        for url in pres_links[:4]:
            st.markdown(f"- [Download]({url})")

        st.markdown("### 📊 Quarterly Financial Results")
        for url in qr_links[:4]:
            st.markdown(f"- [Download]({url})")

    except Exception as e:
        st.error(f"❌ Could not fetch data from NSE site: {str(e)}")

else:
    st.warning("⚠️ Company not recognized. Please try TCS, INFY, RELIANCE, HDFCBANK, or ITC for now.")
