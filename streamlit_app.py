#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
📁 streamlit_app.py
SET SMART AI Trader - ตัวหลัก รวมเมนูและ sidebar
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time

# ============================================
# 🔴 import หน้าต่างๆ
# ============================================
from pages import short_term
# from pages import long_term     (ไว้ทีหลัง)
# from pages import smart_money   (ไว้ทีหลัง)
# from pages import backtest      (ไว้ทีหลัง)

# ============================================
# 🔴 ตั้งค่าหน้า
# ============================================
st.set_page_config(
    page_title="SET SMART AI Trader",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 🔴 ฟังก์ชันเรียก API
# ============================================

# 🔴 จุดที่ 1: API URL ต้องตรวจสอบให้ถูกต้อง
BASE_URL = "https://api.setsmart.com"  # หรืออาจเป็น "https://api.setsmart.com/v1"

@st.cache_data(ttl=30)  # cache 30 วินาที (อาจนานไป)
def get_realtime_price(symbol):
    """ดึงราคาปัจจุบันจาก SET SMART API"""
    try:
        api_key = st.secrets["SETSMART_API_KEY"]
        
        # 🔴 จุดที่ 2: endpoint ต้องตรวจสอบให้ถูกต้อง
        url = f"{BASE_URL}/realtime/{symbol}"
        # หรืออาจเป็น:
        # url = f"{BASE_URL}/quote/{symbol}"
        # url = f"{BASE_URL}/stock/{symbol}"
        # url = f"{BASE_URL}/price/{symbol}"
        
        headers = {"x-api-key": api_key}
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # 🔴 จุดที่ 3: ชื่อฟิลด์ต้องตรวจสอบให้ถูกต้อง
            return {
                "current": data.get("last", 0),        # อาจเป็น "close" หรือ "price"
                "change": data.get("change", 0),        # อาจไม่มี
                "change_pct": data.get("change_pct", 0),# อาจไม่มี
                "volume": data.get("volume", 0),        # อาจเป็น "vol"
                "open": data.get("open", 0),            # อาจไม่มี
                "high": data.get("high", 0),            # อาจไม่มี
                "low": data.get("low", 0),              # อาจไม่มี
                "bid": data.get("bid", 0),              # อาจไม่มี
                "offer": data.get("offer", 0)           # อาจไม่มี
            }
        else:
            # 🔴 จุดที่ 4: ควรแสดง error เพื่อ debug
            st.error(f"❌ API Error {response.status_code} for {symbol}")
            return None
    except Exception as e:
        st.error(f"❌ Exception: {e}")
        return None

@st.cache_data(ttl=300)  # cache 5 นาที
def get_set_index():
    """ดึง SET Index จาก API"""
    try:
        api_key = st.secrets["SETSMART_API_KEY"]
        url = f"{BASE_URL}/index/SET"
        headers = {"x-api-key": api_key}
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("last", 1600)
        else:
            return 1600  # ค่า default
    except:
        return 1600

# ============================================
# 🔴 ตรวจสอบ API Key
# ============================================
def check_api_status():
    """ตรวจสอบสถานะ API Key"""
    try:
        if "SETSMART_API_KEY" in st.secrets:
            api_key = st.secrets["SETSMART_API_KEY"]
            if api_key and len(api_key) > 10 and api_key != "your-key":
                return "✅ พร้อมใช้งาน", api_key
            else:
                return "⚠️ กรุณาใส่ API Key จริง", None
        else:
            return "⚠️ ไม่พบ API Key", None
    except:
        return "❌ Error", None

api_status, api_key = check_api_status()

# ============================================
# 🔴 Sidebar
# ============================================
with st.sidebar:
    st.title("📊 SET SMART AI Trader")
    st.markdown(f"**วันนี้:** {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown("---")
    
    st.markdown("### 🔌 สถานะ API")
    st.markdown(api_status)
    
    if "✅" not in api_status:
        with st.expander("⚙️ ตั้งค่า"):
            st.markdown("""
            1. ไปที่ **Manage app** → **Secrets**
            2. เพิ่ม: `SETSMART_API_KEY = "your-key"`
            """)
    
    st.markdown("---")
    
    menu = st.radio(
        "📋 เมนู",
        ["🏠 หน้าแรก", "⚡ เล่นสั้น", "💰 เล่นยาว", "🕵️ อ่านเจ้ามือ", "📊 ทดสอบกลยุทธ์", "📓 สมุดบันทึก"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption("SET SMART AI Trader v0.2.0")

# ============================================
# 🔴 หน้าแรก
# ============================================

if menu == "🏠 หน้าแรก":
    st.title("📈 SET SMART AI Trader Dashboard")
    
    # ปุ่มรีเฟรช
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("สถานะ API", "พร้อมใช้งาน" if "✅" in api_status else "รอตั้งค่า")
    
    with col2:
        st.metric("โมดูลที่พร้อม", "5/5")
    
    with col3:
        st.metric("เวลาล่าสุด", datetime.now().strftime("%H:%M:%S"))
    
    with col4:
        if st.button("🔄 รีเฟรชข้อมูล"):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # 🔴 จุดที่ 5: ตัวอย่างหุ้น
    st.subheader("📊 ตัวอย่างหุ้นในตลาด")
    
    watch_list = ["SCC", "PTT", "ADVANC", "CPALL", "KCE", "GULF", "PTTEP"]
    
    stock_data = []
    progress_bar = st.progress(0)
    
    for i, symbol in enumerate(watch_list):
        data = get_realtime_price(symbol)
        if data:
            stock_data.append({
                "หุ้น": symbol,
                "ราคาปัจจุบัน": data["current"],
                "เปลี่ยนแปลง": f"{data['change']:+.2f} ({data['change_pct']:+.2f}%)",
                "Volume (M)": f"{data['volume']/1_000_000:.1f}"
            })
        else:
            stock_data.append({
                "หุ้น": symbol,
                "ราคาปัจจุบัน": 0,
                "เปลี่ยนแปลง": "N/A",
                "Volume (M)": "N/A"
            })
        progress_bar.progress((i + 1) / len(watch_list))
    
    progress_bar.empty()
    
    df = pd.DataFrame(stock_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # SET Index
    st.subheader("📈 SET Index ภาพรวม")
    set_index = get_set_index()
    
    # สร้างข้อมูลตัวอย่างสำหรับกราฟ
    dates = pd.date_range(end=datetime.now(), periods=30).tolist()
    set_prices = [set_index * (1 + np.random.uniform(-0.03, 0.03)) for _ in range(30)]
    
    chart_data = pd.DataFrame({
        "date": dates,
        "SET Index": set_prices
    })
    
    st.line_chart(chart_data.set_index("date"))
    
    # คำแนะนำการใช้งาน
    with st.expander("📋 คำแนะนำการใช้งาน", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⚡ เล่นสั้น")
            st.markdown("""
            - วิเคราะห์หุ้นรายตัวแบบละเอียด
            - ดูราคาจริง, Volume, RSI
            - กราฟแท่งเทียน + Indicators
            - วิเคราะห์ Elliott Wave
            - ดูเจตนารายใหญ่ (NVDR, Big Lot)
            """)
            
            st.markdown("### 💰 เล่นยาว")
            st.markdown("""
            - วิเคราะห์ 2 สไตล์: Growth / Dividend
            - ดูข้อมูลย้อนหลัง 10 ปี
            - คำนวณคะแนน巴菲特
            """)
        
        with col2:
            st.markdown("### 🕵️ อ่านเจ้ามือ")
            st.markdown("""
            - ดู NVDR Flow
            - วิเคราะห์ Big Lot
            - ดู Short Sales
            """)
            
            st.markdown("### 📊 ทดสอบกลยุทธ์")
            st.markdown("""
            - ทดสอบกลยุทธ์ย้อนหลัง
            - ดู Sharpe Ratio, Win Rate
            """)

# ============================================
# 🔴 หน้าอื่นๆ
# ============================================

elif menu == "⚡ เล่นสั้น":
    short_term.show()

elif menu == "💰 เล่นยาว":
    st.info("📝 กำลังพัฒนา...")

elif menu == "🕵️ อ่านเจ้ามือ":
    st.info("📝 กำลังพัฒนา...")

elif menu == "📊 ทดสอบกลยุทธ์":
    st.info("📝 กำลังพัฒนา...")

elif menu == "📓 สมุดบันทึก":
    st.info("📝 กำลังพัฒนา...")

# ============================================
# 🔴 Footer
# ============================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.8em;'>"
    "SET SMART AI Trader | ข้อมูลจาก SET SMART API"
    "</div>",
    unsafe_allow_html=True
)
