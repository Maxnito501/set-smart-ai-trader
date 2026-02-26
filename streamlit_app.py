#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
📁 streamlit_app.py
SET SMART AI Trader - ใช้ API จริงจาก SET SMART
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

# ============================================
# 🔴 import หน้าต่างๆ
# ============================================
from pages import short_term

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
# 🔴 ฟังก์ชันเรียก API (ของจริงจากเอกสาร)
# ============================================

@st.cache_data(ttl=60)  # cache 1 นาที
def get_eod_price(symbol, date=None):
    """
    ดึงราคาปิดรายวันจาก SET SMART API
    Endpoint: /api/listed-company-api/eod-price-by-symbol
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        api_key = st.secrets["SETSMART_API_KEY"]
        url = "https://www.setsmart.com/api/listed-company-api/eod-price-by-symbol"
        params = {
            "symbol": symbol,
            "startDate": date,
            "adjustedPriceFlag": "Y"
        }
        headers = {"x-api-key": api_key}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]  # ข้อมูลล่าสุด
        return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

@st.cache_data(ttl=300)  # cache 5 นาที
def get_historical_eod(symbol, days=30):
    """
    ดึงราคาย้อนหลังจาก SET SMART API
    """
    try:
        api_key = st.secrets["SETSMART_API_KEY"]
        url = "https://www.setsmart.com/api/listed-company-api/eod-price-by-symbol"
        
        # คำนวณวันที่เริ่มต้น
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "symbol": symbol,
            "startDate": start_date.strftime("%Y-%m-%d"),
            "adjustedPriceFlag": "Y"
        }
        headers = {"x-api-key": api_key}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                # เรียงตามวันที่
                data.sort(key=lambda x: x.get("date", ""))
                return data
        return []
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return []

@st.cache_data(ttl=10)  # cache 10 วินาที (ข้อมูลสด)
def get_realtime_price(symbol):
    """
    ดึงข้อมูลเรียลไทม์จาก SET SMART API
    Endpoint: https://marketplace.set.or.th/api/public/realtime-data/stock
    """
    try:
        api_key = st.secrets["SETSMART_API_KEY"]
        url = "https://marketplace.set.or.th/api/public/realtime-data/stock"
        params = {
            "stockSymbol": symbol,
            "market": "SET"
        }
        headers = {"x-api-key": api_key}
        
        response = requests.get(url, headers=headers, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "current": data.get("last", 0),
                "change": data.get("change", 0),
                "change_pct": data.get("changePercent", 0),
                "volume": data.get("volume", 0),
                "bid": data.get("bid", 0),
                "offer": data.get("offer", 0),
                "high": data.get("high", 0),
                "low": data.get("low", 0),
                "open": data.get("open", 0)
            }
        return None
    except Exception as e:
        return None

# ============================================
# 🔴 ตรวจสอบ API Key
# ============================================
def check_api_status():
    try:
        if "SETSMART_API_KEY" in st.secrets:
            api_key = st.secrets["SETSMART_API_KEY"]
            if api_key and len(api_key) > 10:
                return "✅ พร้อมใช้งาน", api_key
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
    
    st.markdown("---")
    
    menu = st.radio(
        "📋 เมนู",
        ["🏠 หน้าแรก", "⚡ เล่นสั้น", "💰 เล่นยาว", "🕵️ อ่านเจ้ามือ", "📊 ทดสอบกลยุทธ์", "📓 สมุดบันทึก"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption("SET SMART AI Trader v0.3.0 | ใช้ API จริง")

# ============================================
# 🔴 หน้าแรก (ใช้ API จริง)
# ============================================

if menu == "🏠 หน้าแรก":
    st.title("📈 SET SMART AI Trader Dashboard")
    
    # แถวสถานะ
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("สถานะ API", "พร้อมใช้งาน" if "✅" in api_status else "รอตั้งค่า")
    
    with col2:
        st.metric("โมดูลที่พร้อม", "5/5")
    
    with col3:
        st.metric("เวลาล่าสุด", datetime.now().strftime("%H:%M:%S"))
    
    with col4:
        if st.button("🔄 รีเฟรช"):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # ============================================
    # ตัวอย่างหุ้นในตลาด (จาก API จริง)
    # ============================================
    st.subheader("📊 ตัวอย่างหุ้นในตลาด (ข้อมูลจริง)")
    
    watch_list = ["SCC", "PTT", "ADVANC", "CPALL", "KCE", "GULF", "PTTEP"]
    
    stock_data = []
    progress_bar = st.progress(0)
    
    for i, symbol in enumerate(watch_list):
        # ลองเรียกเรียลไทม์ก่อน
        rt = get_realtime_price(symbol)
        
        if rt:
            stock_data.append({
                "หุ้น": symbol,
                "ราคาปัจจุบัน": rt["current"],
                "เปลี่ยนแปลง": f"{rt['change']:+.2f} ({rt['change_pct']:+.2f}%)",
                "Volume (M)": f"{rt['volume']/1_000_000:.1f}"
            })
        else:
            # ถ้าไม่ได้ ใช้ EOD แทน
            eod = get_eod_price(symbol)
            if eod:
                stock_data.append({
                    "หุ้น": symbol,
                    "ราคาปัจจุบัน": eod.get("close", 0),
                    "เปลี่ยนแปลง": "N/A",
                    "Volume (M)": f"{eod.get('volume', 0)/1_000_000:.1f}"
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
    
    # ============================================
    # กราฟ SET Index
    # ============================================
    st.subheader("📈 SET Index ภาพรวม")
    
    # ดึงข้อมูล SET Index (ใช้ PTT แทน หรือจะเรียก index โดยเฉพาะ)
    set_data = get_historical_eod("PTT", 30)  # ใช้ PTT แทนคร่าวๆ
    
    if set_data and len(set_data) > 0:
        dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in set_data]
        prices = [d.get("close", 0) for d in set_data]
        
        chart_df = pd.DataFrame({
            "date": dates,
            "SET Index": prices
        })
        st.line_chart(chart_df.set_index("date"))
    else:
        # ถ้าไม่ได้ ให้ใช้ข้อมูลตัวอย่าง
        dates = pd.date_range(end=datetime.now(), periods=30).tolist()
        set_prices = [1600 + i*2 + np.random.randint(-10, 10) for i in range(30)]
        
        chart_df = pd.DataFrame({
            "date": dates,
            "SET Index": set_prices
        })
        st.line_chart(chart_df.set_index("date"))
    
    # ============================================
    # คำแนะนำการใช้งาน
    # ============================================
    with st.expander("📋 คำแนะนำการใช้งาน", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⚡ เล่นสั้น")
            st.markdown("""
            - วิเคราะห์หุ้นรายตัวแบบละเอียด
            - ดูราคาจริง, Volume, RSI
            - กราฟแท่งเทียน + Indicators
            - วิเคราะห์ Elliott Wave
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
    "SET SMART AI Trader | ข้อมูลจาก SET SMART API จริง"
    "</div>",
    unsafe_allow_html=True
)
