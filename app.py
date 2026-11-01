import streamlit as st
from PIL import Image
import base64
from io import BytesIO
from openai import OpenAI

st.set_page_config(page_title="Sahibi SMC Trade Analyzer", page_icon="📊", layout="centered")
st.title("📊 sahibi SMC/PA Analyzer (3-Chart)")

# --- SECURE API KEY LOADING ---
try:
    api_key = st.secrets["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"]
except Exception:
    with st.sidebar:
        st.header("🔑 Setup")
        api_key = st.text_input("Groq API Key", type="password")
        st.markdown("[Get a free API Key](https://console.groq.com/keys)")

# --- 3 CHART UPLOADERS ---
col1, col2, col3 = st.columns(3)

with col1:
    img_htf = st.file_uploader("HTF (1H / 30M)", type=["png", "jpg", "jpeg"])
with col2:
    img_mtf = st.file_uploader("MTF (15M)", type=["png", "jpg", "jpeg"])
with col3:
    img_ltf = st.file_uploader("LTF (5M)", type=["png", "jpg", "jpeg"])

if st.button("🚀 ANALYZE CHARTS", use_container_width=True, type="primary"):
    if not api_key:
        st.error("API Key missing. Please check Streamlit Secrets.")
    elif not all([img_htf, img_mtf, img_ltf]):
        st.warning("Please upload all 3 timeframes.")
    else:
        with st.spinner("Analyzing market structure..."):
            try:
                client = OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=api_key
                )
                
                # Stitch 3 images side-by-side
                images = [Image.open(img).convert("RGB") for img in [img_htf, img_mtf, img_ltf]]
                width, height = images[0].size
                
                # Create a blank canvas (3x width, 1x height)
                grid_image = Image.new('RGB', (width * 3, height))
                
                # Paste images in order
                grid_image.paste(images[0], (0, 0))           # HTF
                grid_image.paste(images[1], (width, 0))       # MTF
                grid_image.paste(images[2], (width * 2, 0))   # LTF
                
                buffered = BytesIO()
                grid_image.save(buffered, format="JPEG")
                b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                prompt = """You are an elite Smart Money Concepts (SMC) and Price Action trader. 
                Analyze this single image containing 3 charts side-by-side:
                - Left Image: Higher Timeframe (HTF - 1H or 30M)
                - Middle Image: Mid Timeframe (MTF - 15M)
                - Right Image: Lower Timeframe (LTF - 5M)
                
                1. HTF (Left): Determine trend (HH/HL or LH/LL) and major liquidity pools.
                2. MTF (Middle): Identify the Order Block (OB) or Fair Value Gap (FVG) in the direction of the HTF trend.
                3. LTF (Right): Identify the Liquidity Sweep and confirm the CHoCH/MSS entry trigger.
                
                If setup is invalid, output NO TRADE.
                If valid, provide:
                DIRECTION: (BUY/SELL)
                ENTRY: (Price)
                STOP LOSS: (Price - beyond the sweep)
                TAKE PROFIT 1: (Price)
                TAKE PROFIT 2: (Price)
                R:R: (e.g., 1:2)
                REASONING: (Briefly explain how all 3 timeframes align)"""
                
                content = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
                
                response = client.chat.completions.create(
                    model="qwen/qwen3.8-27b",
                    messages=[{"role": "user", "content": content}],
                    temperature=0.2
                )
                
                st.success("Analysis Complete!")
                st.info(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
