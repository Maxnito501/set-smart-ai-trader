"""
📁 streamlit_app.py
SET SMART AI Trader - ใช้ Yahoo Finance
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf

st.set_page_config(page_title="SET SMART AI Trader", layout="wide")

# ============================================
# Yahoo Client
# ============================================
class YahooClient:
    def get_price(self, symbol):
        try:
            ticker = yf.Ticker(f"{symbol}.BK")
            hist = ticker.history(period="2d")
            if hist.empty:
                return None
            return {
                "current": round(hist['Close'].iloc[-1], 2),
                "change": round(hist['Close'].iloc[-1] - hist['Close'].iloc[-2], 2),
                "volume": hist['Volume'].iloc[-1]
            }
        except:
            return None

# ============================================
# Sidebar
# ============================================
with st.sidebar:
    st.title("📊 SET SMART AI Trader")
    st.markdown(f"**วันนี้:** {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown("---")
    st.markdown("### 🔌 สถานะ")
    st.markdown("✅ ใช้ Yahoo Finance")
    
    menu = st.radio("📋 เมนู",
        ["🏠 หน้าแรก", "⚡ เล่นสั้น", "💰 เล่นยาว", "🕵️ อ่านเจ้ามือ", "📊 ทดสอบกลยุทธ์"],
        label_visibility="collapsed"
    )

# ============================================
# หน้าแรก
# ============================================
if menu == "🏠 หน้าแรก":
    st.title("📈 SET SMART AI Trader")
    
    yahoo = YahooClient()
    watch_list = ["SCC", "PTT", "ADVANC", "CPALL", "KCE"]
    
    data = []
    for sym in watch_list:
        price = yahoo.get_price(sym)
        if price:
            data.append({
                "หุ้น": sym,
                "ราคา": price['current'],
                "เปลี่ยนแปลง": f"{price['change']:+.2f}",
                "Volume": f"{price['volume']/1_000_000:.1f}M"
            })
    
    st.dataframe(pd.DataFrame(data), use_container_width=True)

# ============================================
# หน้าที่เหลือ
# ============================================
elif menu == "⚡ เล่นสั้น":
    st.title("⚡ เล่นสั้น")
    st.info("📝 กำลังโหลด... (ใช้ Yahoo Finance)")
    
elif menu == "💰 เล่นยาว":
    st.title("💰 เล่นยาว")
    st.info("📝 รอข้อมูล SETSMART")
    
elif menu == "🕵️ อ่านเจ้ามือ":
    st.title("🕵️ อ่านเจ้ามือ")
    st.info("📝 รอข้อมูล SETSMART")
    
else:
    st.title("📊 ทดสอบกลยุทธ์")
    st.info("📝 กำลังพัฒนา")
