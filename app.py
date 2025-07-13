# 📥 Streamlit App to Fetch Company Filings (Using Screener.in)
import streamlit as st
import requests
from bs4 import BeautifulSoup

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

if selected_company in company_map:
    symbol = company_map[selected_company]["symbol"]
    company_display = company_map[selected_company]["name"]
    st.subheader(f"📁 Latest Documents from Screener.in for {company_display}")

    screener_url = f"https://www.screener.in/company/{symbol}/consolidated/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(screener_url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        doc_section = soup.find("section", {"id": "documents"})
        if doc_section:
            links = doc_section.find_all("a", href=True)

            ar_links = []
            call_links = []
            pres_links = []
            qr_links = []

            for link in links:
                raw_text = link.text.strip()
                href = link["href"]
                full_url = f"https://www.screener.in{href}" if href.startswith("/") else href

                if ".pdf" not in href.lower():
                    continue  # Skip non-PDF or dynamic links

                # If text is empty or too short, use filename as fallback
                if not raw_text or len(raw_text) < 4:
                    fallback_text = full_url.split("/")[-1].split("?")[0]
                    text = fallback_text
                else:
                    text = raw_text

                text_lower = text.lower()
                if "annual report" in text_lower:
                    ar_links.append((text, full_url))
                elif "conference call" in text_lower or "earnings call" in text_lower:
                    call_links.append((text, full_url))
                elif "investor presentation" in text_lower:
                    pres_links.append((text, full_url))
                elif "result" in text_lower:
                    qr_links.append((text, full_url))

            st.markdown("### 📄 Annual Reports")
            for text, url in ar_links[:2]:
                st.markdown(f"- [{text}]({url})")

            st.markdown("### 🗣️ Earnings Call Transcripts")
            for text, url in call_links[:4]:
                st.markdown(f"- [{text}]({url})")

            st.markdown("### 🖼️ Investor Presentations")
            for text, url in pres_links[:4]:
                st.markdown(f"- [{text}]({url})")

            st.markdown("### 📊 Quarterly Financial Results")
            for text, url in qr_links[:4]:
                st.markdown(f"- [{text}]({url})")

        else:
            st.warning("⚠️ Could not find documents section on Screener.in.")

    except Exception as e:
        st.error(f"❌ Failed to fetch data from Screener.in: {str(e)}")

else:
    st.warning("⚠️ Company not recognized. Please try a supported company.")
