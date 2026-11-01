import streamlit as st
from PIL import Image, ImageOps
import base64
from io import BytesIO
from openai import OpenAI

st.set_page_config(page_title="SMC Analyzer", page_icon="📊", layout="centered")
st.title("📊 SMC/PA Analyzer")

with st.sidebar:
    st.header("🔑 Setup")
    api_key = st.text_input("Groq API Key", type="password")
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
                # 1. Initialize Groq client
                client = OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=api_key
                )
                
                # 2. Stitch 4 images into a single 2x2 grid
                images = [Image.open(img).convert("RGB") for img in [img_4h, img_1h, img_15m, img_5m]]
                width, height = images[0].size
                
                # Create a blank canvas (2x width, 2x height)
                grid_image = Image.new('RGB', (width * 2, height * 2))
                
                # Paste images into the grid
                grid_image.paste(images[0], (0, 0))           # 4H Top Left
                grid_image.paste(images[1], (width, 0))       # 1H Top Right
                grid_image.paste(images[2], (0, height))      # 15M Bottom Left
                grid_image.paste(images[3], (width, height))  # 5M Bottom Right
                
                # Convert the single stitched image to base64
                buffered = BytesIO()
                grid_image.save(buffered, format="JPEG")
                b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                prompt = """You are an elite Smart Money Concepts (SMC) and Price Action trader. 
                Analyze this single image containing a 2x2 grid of 4 charts:
                - Top Left: 4H Chart
                - Top Right: 1H Chart
                - Bottom Left: 15M Chart
                - Bottom Right: 5M Chart
                
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
                
                content = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
                
                # 3. Call Groq API using Qwen model
                response = client.chat.completions.create(
                    model="qwen/qwen3.8-27b",
                    messages=[{"role": "user", "content": content}],
                    temperature=0.2
                )
                
                st.success("Analysis Complete!")
                st.info(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
