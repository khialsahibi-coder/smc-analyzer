import streamlit as st
from PIL import Image
import base64
from io import BytesIO
from openai import OpenAI

# --- HIDE STREAMLIT BRANDING & MENUS ---
st.set_page_config(
    page_title="Khial's SMC AI", 
    page_icon="📊", 
    layout="centered",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# --- CUSTOM DARK GREEN CSS + AWESOME TITLE ---
custom_css = """
<style>
.stApp { background-color: #0b2a1c; color: #ffffff; }
[data-testid="stSidebar"] { background-color: #051c11; }
.main-title {
    font-size: 2.5rem; font-weight: 900; text-align: center;
    background: linear-gradient(90deg, #a3e6c4, #2ca36b, #a3e6c4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-shadow: 0px 4px 15px rgba(44, 163, 107, 0.4); margin-bottom: 0px; padding-bottom: 0px;
}
.sub-title {
    text-align: center; font-size: 1.1rem; color: #a3e6c4;
    margin-top: 5px; margin-bottom: 25px; font-weight: 500; letter-spacing: 1px; text-transform: uppercase;
}
h2, h3, h4, h5, h6 { color: #a3e6c4 !important; }
[data-testid="stFileUploader"] { background-color: #154a31; border-radius: 10px; padding: 10px; }
.stButton>button {
    background-color: #1f7a4d; color: white; border: 1px solid #2ca36b;
    font-weight: bold; letter-spacing: 1px;
}
.stButton>button:hover { background-color: #2ca36b; color: white; box-shadow: 0px 0px 10px rgba(44, 163, 107, 0.6); }
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background-color: #154a31; color: white; border: 1px solid #2ca36b; }
header {visibility: hidden;} [data-testid="stToolbar"] {visibility: hidden;} footer {visibility: hidden;} #MainMenu {visibility: hidden;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.markdown("""
    <div class="main-title">📊 SMC ELITE PREDICTOR</div>
    <div class="sub-title">Pro AI Trading Assistant by Khial Sahibi</div>
""", unsafe_allow_html=True)

# --- SECURE API KEY LOADING ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    with st.sidebar:
        st.header("🔑 Setup")
        api_key = st.text_input("Groq API Key", type="password")
        st.markdown("[Get a free API Key](https://console.groq.com/keys)")

# --- INPUTS ---
timeframe = st.selectbox("Select Chart Timeframe:", ["1 Minute", "5 Minutes", "15 Minutes", "30 Minutes", "1 Hour", "4 Hour", "Daily"])
strategy_mode = st.selectbox("Select Strategy Mode:", ["Smart Money Concepts (SMC)", "ICT (Inner Circle Trader)", "Aggressive Scalping", "Classic Price Action"])

# NEW: Current Price Input for exact AI math
current_price = st.text_input("Type the EXACT Current Price on your chart (e.g., 3889.00):")

img_chart = st.file_uploader(f"Upload your {timeframe} Chart", type=["png", "jpg", "jpeg"])

if st.button("🚀 ANALYZE CHART", use_container_width=True, type="primary"):
    if not api_key:
        st.error("API Key missing. Please check Streamlit Secrets.")
    elif not img_chart or not current_price:
        st.warning("Please upload a chart AND type the current price.")
    else:
        with st.spinner(f"Analyzing {timeframe} structure using {strategy_mode}..."):
            try:
                client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
                
                # Process the single image
                image = Image.open(img_chart).convert("RGB")
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                prompt = f"""You are an elite institutional trader using {strategy_mode}.
                Analyze this {timeframe} chart. The user has provided the current market price: {current_price}.
                
                1. STRUCTURE: Identify trend and liquidity sweeps.
                2. ZONES: Identify Order Blocks (OB), Fair Value Gaps (FVG), or S/R.
                3. STRATEGY: Apply {strategy_mode} rules to find a setup.
                
                CRITICAL RISK MANAGEMENT RULE: 
                The Stop Loss (SL) must be tightly placed just beyond the structural invalidation point (e.g., 5-15 pips beyond the recent sweep). 
                The Take Profit (TP) must target the next major liquidity pool. 
                DO NOT offer a Risk:Reward lower than 1:1.5. If the R:R is bad, output WAIT.
                
                If there is a clear setup, provide exactly this format using precise decimal math based on the current price ({current_price}):
                
                PREDICTION: (Bullish / Bearish / Ranging)
                DIRECTION: (BUY / SELL / WAIT)
                ENTRY: (Exact Price)
                STOP LOSS: (Exact Price)
                TAKE PROFIT 1: (Exact Price)
                TAKE PROFIT 2: (Exact Price)
                RISK:REWARD: (Calculate the exact ratio)
                REASONING: (Explain the {strategy_mode} logic for this setup)"""
                
                content = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
                
                response = client.chat.completions.create(
                    model="qwen/qwen3.8-27b",
                    messages=[{"role": "user", "content": content}],
                    temperature=0.1 # Lower temp for more precise math
                )
                
                st.success("Analysis Complete!")
                st.markdown(f"### 📝 Trade Plan\n{response.choices[0].message.content}")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
