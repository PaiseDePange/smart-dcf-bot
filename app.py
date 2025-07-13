# 📥 Streamlit App to Fetch Company Filings
import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Company Filings Fetcher", layout="centered")
st.title("📂 Company Filings Dashboard")
st.markdown("Enter an Indian listed company name (e.g. TCS) to fetch its recent filings:")

company_input = st.text_input("Company Name (e.g. TCS, INFY, HDFC Bank)", "TCS")

# Map known company short names to BSE codes (expandable dictionary)
company_map = {
    "TCS": {"bse_code": "532540", "name": "Tata Consultancy Services"},
    "INFY": {"bse_code": "500209", "name": "Infosys Ltd"},
    "RELIANCE": {"bse_code": "500325", "name": "Reliance Industries"},
    "HDFCBANK": {"bse_code": "500180", "name": "HDFC Bank"},
    "ITC": {"bse_code": "500875", "name": "ITC Ltd"},
}

if company_input.upper() in company_map:
    bse_code = company_map[company_input.upper()]["bse_code"]
    company_display = company_map[company_input.upper()]["name"]
    st.subheader(f"📁 Latest Filings for {company_display}")

    # BSE Announcement page
    bse_url = f"https://www.bseindia.com/corporates/ann.aspx?scrip={bse_code}&dur=A"
    response = requests.get(bse_url, headers={"User-Agent": "Mozilla/5.0"})

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all('a', href=True)

        ar_links = []
        call_links = []
        pres_links = []
        qr_links = []

        for link in links:
            text = link.text.strip().lower()
            href = link['href']
            if 'annual report' in text and href.endswith(".pdf"):
                ar_links.append("https://www.bseindia.com" + href)
            elif 'earning call' in text or 'conference call' in text:
                call_links.append("https://www.bseindia.com" + href)
            elif 'investor presentation' in text:
                pres_links.append("https://www.bseindia.com" + href)
            elif 'financial result' in text:
                qr_links.append("https://www.bseindia.com" + href)

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

    else:
        st.error("❌ Could not fetch data from BSE site. Try again later or check the company code.")

else:
    st.warning("⚠️ Company not recognized. Please try TCS, INFY, RELIANCE, HDFCBANK, or ITC for now.")
