# 🗕️ Streamlit App to Fetch Company Filings (Using Screener.in)
import streamlit as st
import requests
from bs4 import BeautifulSoup
import streamlit.components.v1 as components
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import io

st.set_page_config(page_title="AI Investment Assistant", layout="wide")

# Custom CSS to increase tab label font size further
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab"] {
        font-size: 24px;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 AI-Powered Stock Analysis")

# Tabs for Navigation
tabs = st.tabs(["📥 Inputs", "📚 Fundamentals", "📈 Technical", "🧠 Conclusion", "🧪 Data Checks"])

# --- Tab 1: Inputs ---
with tabs[0]:
    st.header("📥 Inputs")
    st.markdown("Provide data to feed the AI for analysis.")

    st.subheader("1️⃣ Last Two Annual Reports")
    annual_links = [
        st.text_input("Annual Report Link 1 (PDF URL)"),
        st.text_input("Annual Report Link 2 (PDF URL)")
    ]

    st.subheader("2️⃣ Last 4 Earnings Call Transcripts")
    earnings_calls = [
        st.text_input("Earnings Call Transcript 1 (PDF URL)"),
        st.text_input("Earnings Call Transcript 2 (PDF URL)"),
        st.text_input("Earnings Call Transcript 3 (PDF URL)"),
        st.text_input("Earnings Call Transcript 4 (PDF URL)")
    ]

    st.subheader("3️⃣ Last 4 Investor Presentations")
    presentations = [
        st.text_input("Investor Presentation 1 (PDF URL)"),
        st.text_input("Investor Presentation 2 (PDF URL)"),
        st.text_input("Investor Presentation 3 (PDF URL)"),
        st.text_input("Investor Presentation 4 (PDF URL)")
    ]

    st.subheader("4️⃣ Screenshots from Screener.in")
    screener_images = {
        "Quarterly Results": st.file_uploader("Quarterly Results Screenshot", type=["png", "jpg", "jpeg"], key="qr"),
        "Annual P&L": st.file_uploader("Annual P&L Screenshot", type=["png", "jpg", "jpeg"], key="pl"),
        "Balance Sheet": st.file_uploader("Balance Sheet Screenshot", type=["png", "jpg", "jpeg"], key="bs"),
        "Cashflows": st.file_uploader("Cashflows Screenshot", type=["png", "jpg", "jpeg"], key="cf"),
        "Shareholding Pattern": st.file_uploader("Shareholding Pattern Screenshot", type=["png", "jpg", "jpeg"], key="shp"),
    }

# --- Tab 2: Fundamentals ---
with tabs[1]:
    st.header("📚 Fundamental Analysis")
    st.markdown("This section will include extracted ratios, growth, and valuation models like DCF.")
    # (Placeholder)

# --- Tab 3: Technical ---
with tabs[2]:
    st.header("📈 Technical Analysis")
    st.markdown("Technical indicators and chart positioning will be shown here.")
    # (Placeholder)

# --- Tab 4: Conclusion ---
with tabs[3]:
    st.header("🧠 Conclusion & Recommendation")
    st.markdown("This section will summarize findings and suggest an investment stance.")
    # (Placeholder)

# --- Tab 5: Data Checks ---
with tabs[4]:
    st.header("🧪 Data Quality Checks")
    st.markdown("Verify if uploaded images are converted correctly and if PDFs have readable text.")

    # Check for OCR text from uploaded images
    for label, uploaded_image in screener_images.items():
        if uploaded_image is not None:
            st.subheader(f"🖼️ OCR Preview: {label}")
            image = Image.open(uploaded_image)
            text = pytesseract.image_to_string(image)
            st.image(image, caption=label)
            st.text_area(f"Extracted Text - {label}", text, height=200)

    # Preview first few lines of each PDF link if accessible
    def preview_pdf_text_from_url(pdf_url):
        try:
            response = requests.get(pdf_url)
            reader = PdfReader(io.BytesIO(response.content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages[:2])
            return text.strip()[:2000]  # limit to 2000 chars
        except Exception as e:
            return f"Error reading PDF: {e}"

    for i, url in enumerate(annual_links + earnings_calls):
        if url:
            st.subheader(f"📄 Preview: PDF Document {i+1}")
            text = preview_pdf_text_from_url(url)
            st.text_area(f"Extracted PDF Text {i+1}", text, height=200)
