# 🗕️ Streamlit App to Fetch Company Filings (Using Screener.in)
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Company Filings Fetcher", layout="centered")
st.title("📂 Company Filings Dashboard")
st.markdown("Select an Indian listed company to fetch its filings from Screener.in:")

# Map known short names to Screener URLs (expandable dictionary)
company_map = {
    "TCS": {"symbol": "TCS", "name": "Tata Consultancy Services"},
    "INFY": {"symbol": "INFY", "name": "Infosys Ltd"},
    "RELIANCE": {"symbol": "RELIANCE", "name": "Reliance Industries"},
    "HDFCBANK": {"symbol": "HDFCBANK", "name": "HDFC Bank"},
    "ITC": {"symbol": "ITC", "name": "ITC Ltd"},
}

company_options = list(company_map.keys())
selected_company = st.selectbox("Choose a company:", company_options, index=0)

if st.button("🔍 Fetch Filings"):
    if selected_company in company_map:
        symbol = company_map[selected_company]["symbol"]
        company_display = company_map[selected_company]["name"]
        st.subheader(f"📁 Latest Documents from Screener.in for {company_display}")

        screener_url = f"https://www.screener.in/company/{symbol}/consolidated/"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(screener_url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")

            all_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.pdf')]
            pdf_urls = [(url.split("/")[-1], "https://www.screener.in" + url if url.startswith("/") else url) for url in all_links]

            ar_links = []
            call_links = []
            pres_links = []
            qr_links = []
            other_links = []

            for text, url in pdf_urls:
                text_lower = text.lower()

                if "annual" in text_lower and "report" in text_lower:
                    ar_links.append((text, url))
                elif "call" in text_lower or "conference" in text_lower:
                    call_links.append((text, url))
                elif "presentation" in text_lower:
                    pres_links.append((text, url))
                elif "result" in text_lower:
                    qr_links.append((text, url))
                else:
                    other_links.append((text, url))

            def render_section(title, links):
                if links:
                    st.markdown(f"### {title}")
                    for text, url in links:
                        st.markdown(f"- 🔗 [{text}]({url})")

            render_section("📄 Annual Reports", ar_links)
            render_section("🔣 Earnings Call Transcripts", call_links)
            render_section("🖼️ Investor Presentations", pres_links)
            render_section("📈 Quarterly Financial Results", qr_links)
            render_section("📌 Other Documents", other_links)

        except Exception as e:
            st.error(f"❌ Failed to fetch data from Screener.in: {str(e)}")

    else:
        st.warning("⚠️ Company not recognized. Please try a supported company.")
