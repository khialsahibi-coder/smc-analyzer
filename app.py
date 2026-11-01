import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Sahibi Trade Analyzer", page_icon="📊", layout="centered")
st.title("📊 SMC/PA Sahibi Trade Analyzer")

with st.sidebar:
    st.header("🔑 Setup")
    api_key = st.text_input("Gemini API Key", type="password")
    st.markdown("[Get a free API Key](https://aistudio.google.com/apikey)")

col1, col2 = st.columns(2)
with col1:
    img_4h = st.file_uploader("4H Chart", type=["png", "jpg", "jpeg"])
with col2:
    img_1h = st.file_uploader("1H Chart", type=["png", "jpg", "jpeg"])
    
col3, col4 = st.columns(2)
with col3:
    img_15m = st.file_uploader("15M Chart", type=["png", "jpg", "jpeg"])
with col4:
    img_5m = st.file_uploader("5M Chart", type=["png", "jpg", "jpeg"])

if st.button("🚀 ANALYZE CHARTS", use_container_width=True, type="primary"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif not all([img_4h, img_1h, img_15m, img_5m]):
        st.warning("Please upload all 4 timeframes.")
    else:
        with st.spinner("Analyzing market structure..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                prompt = """You are an elite Smart Money Concepts (SMC) and Price Action trader. Analyze these 4 charts (4H, 1H, 15M, 5M).
                1. 4H: Determine trend (HH/HL or LH/LL).
                2. 1H: Identify the Order Block (OB) or Fair Value Gap (FVG).
                3. 15M: Identify the Liquidity Sweep.
                4. 5M: Confirm the CHoCH/MSS entry trigger.
                
                If setup is invalid, output NO TRADE.
                If valid, provide:
                DIRECTION: (BUY/SELL)
                ENTRY: (Price)
                STOP LOSS: (Price - beyond the sweep)
                TAKE PROFIT 1: (Price)
                TAKE PROFIT 2: (Price)
                R:R: (e.g., 1:2)
                REASONING: (Briefly explain)"""
                
                images = [Image.open(img) for img in [img_4h, img_1h, img_15m, img_5m]]
                response = model.generate_content([prompt] + images)
                
                st.success("Analysis Complete!")
                st.info(response.text)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
