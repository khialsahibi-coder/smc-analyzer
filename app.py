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
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# --- CUSTOM DARK GREEN CSS + AWESOME TITLE ---
custom_css = """
<style>
/* Main app background */
.stApp {
    background-color: #0b2a1c; /* Dark Green */
    color: #ffffff; /* White text */
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #051c11; /* Even darker green */
}

/* Awesome Glowing Title */
.main-title {
    font-size: 2.5rem;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg, #a3e6c4, #2ca36b, #a3e6c4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0px 4px 15px rgba(44, 163, 107, 0.4);
    margin-bottom: 0px;
    padding-bottom: 0px;
}

/* Subtitle with name */
.sub-title {
    text-align: center;
    font-size: 1.1rem;
    color: #a3e6c4;
    margin-top: 5px;
    margin-bottom: 25px;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* Make headers a light green for contrast */
h2, h3, h4, h5, h6 {
    color: #a3e6c4 !important;
}

/* Upload box styling */
[data-testid="stFileUploader"] {
    background-color: #154a31;
    border-radius: 10px;
    padding: 10px;
}

/* Primary Button styling */
.stButton>button {
    background-color: #1f7a4d;
    color: white;
    border: 1px solid #2ca36b;
    font-weight: bold;
    letter-spacing: 1px;
}
.stButton>button:hover {
    background-color: #2ca36b;
    color: white;
    box-shadow: 0px 0px 10px rgba(44, 163, 107, 0.6);
}

/* Selectbox styling */
div[data-baseweb="select"] > div {
    background-color: #154a31;
    color: white;
    border: 1px solid #2ca36b;
}

/* HIDE THE TOP HEADER (GitHub logo, Manage App, etc) */
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}

/* HIDE THE FOOTER AND HAMBURGER MENU */
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- CUSTOM TITLE HTML ---
st.markdown("""
    <div class="main-title">📊 SMC ELITE PREDICTOR</div>
    <div class="sub-title">Custom AI Trading Assistant by Khial Sahibi</div>
""", unsafe_allow_html=True)

# --- SECURE API KEY LOADING ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    with st.sidebar:
        st.header("🔑 Setup")
        api_key = st.text_input("Groq API Key", type="password")
        st.markdown("[Get a free API Key](https://console.groq.com/keys)")

# --- 1 CHART UPLOAD & TIMEFRAME SELECTOR ---
timeframe = st.selectbox("Select Chart Timeframe:", ["1 Minute", "5 Minutes", "15 Minutes", "30 Minutes", "1 Hour", "4 Hour", "Daily"])

img_chart = st.file_uploader(f"Upload your {timeframe} Chart", type=["png", "jpg", "jpeg"])

if st.button("🚀 ANALYZE CHART", use_container_width=True, type="primary"):
    if not api_key:
        st.error("API Key missing. Please check Streamlit Secrets.")
    elif not img_chart:
        st.warning("Please upload a chart image first.")
    else:
        with st.spinner(f"Analyzing {timeframe} structure..."):
            try:
                client = OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=api_key
                )
                
                # Process the single image
                image = Image.open(img_chart).convert("RGB")
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                prompt = f"""You are an elite Smart Money Concepts (SMC) and Price Action trader. 
                Analyze this single {timeframe} chart.
                
                1. STRUCTURE: Identify the current trend (Bullish, Bearish, or Ranging) based on HH/HL or LH/LL.
                2. ZONES: Identify the nearest Order Block (OB) or Fair Value Gap (FVG).
                3. LIQUIDITY: Note any recent Liquidity Sweeps (stop hunts).
                4. PREDICTION: Based on this timeframe alone, where is price most likely to go next?
                
                If the chart is messy, consolidating, or lacks a clear setup, output NO TRADE.
                If there is a clear setup, provide:
                PREDICTION: (Bullish / Bearish / Ranging)
                DIRECTION: (BUY / SELL / WAIT)
                ENTRY ZONE: (Price or Zone)
                STOP LOSS: (Price - beyond invalidation)
                TAKE PROFIT 1: (Price)
                TAKE PROFIT 2: (Price)
                REASONING: (Explain the SMC logic based on the {timeframe} chart)"""
                
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
                st.markdown(f"### 📝 Trade Plan\n{response.choices[0].message.content}")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
