import streamlit as st
from PIL import Image
import base64
from openai import OpenAI

st.set_page_config(page_title="Sahibi SMC Trade Analyzer", page_icon="📊", layout="centered")
st.title("📊 SMC/PA Sahibi Analyzer")

with st.sidebar:
    st.header("🔑 Setup")
    # Using Groq's API key input
    api_key = st.text_input("Groq API Key", type="password", help="Get a free key at console.groq.com")
    st.markdown("[Get a free API Key here](https://console.groq.com/keys)")

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
        st.error("Please enter your Groq API Key in the sidebar.")
    elif not all([img_4h, img_1h, img_15m, img_5m]):
        st.warning("Please upload all 4 timeframes.")
    else:
        with st.spinner("Analyzing market structure..."):
            try:
                # Initialize Groq client
                client = OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=api_key
                )
                
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
                
                # Prepare images for Groq
                content = [{"type": "text", "text": prompt}]
                for img in [img_4h, img_1h, img_15m, img_5m]:
                    b64 = base64.b64encode(img.getvalue()).decode('utf-8')
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                    })
                
                # Call Groq API (using Llama 4 Scout)
                response = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[{"role": "user", "content": content}],
                    temperature=0.2
                )
                
                st.success("Analysis Complete!")
                st.info(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
