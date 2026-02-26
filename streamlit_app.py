#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
📁 streamlit_app.py
SET SMART AI Trader - ตัวหลัก รวมเมนูและ sidebar
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os

# ============================================
# 🔴 import หน้าต่างๆ
# ============================================
from pages import short_term  # เพิ่มแล้ว!
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
# 🔴 ตรวจสอบ API Key
# ============================================
def check_api_status():
    """ตรวจสอบสถานะ API Key"""
    try:
        if "SETSMART_API_KEY" in st.secrets:
            api_key = st.secrets["SETSMART_API_KEY"]
            if api_key and len(api_key) > 10 and api_key != "your-key":
                return "✅ เชื่อมต่อ API แล้ว", api_key
            else:
                return "⚠️ กรุณาใส่ API Key จริง", None
        else:
            return "⚠️ ไม่พบ API Key ใน Secrets", None
    except:
        return "❌ Error ในการอ่าน Secrets", None

# เรียกตรวจสอบ
api_status, api_key = check_api_status()

# ============================================
# 🔴 Sidebar (เมนูหลัก)
# ============================================
with st.sidebar:
    st.title("📊 SET SMART AI Trader")
    st.markdown(f"**วันนี้:** {datetime.now().strftime('%d/%m/%Y')}")
    
    st.markdown("---")
    
    # แสดงสถานะ API
    st.markdown("### 🔌 สถานะระบบ")
    st.markdown(api_status)
    
    # ถ้ายังไม่ได้ตั้งค่า API
    if "✅" not in api_status:
        with st.expander("⚙️ วิธีตั้งค่า API Key"):
            st.markdown("""
            1. ไปที่ **Manage app** → **Secrets**
            2. เพิ่ม:
            ```
            SETSMART_API_KEY = "your-actual-key-here"
            ```
            3. กด **Save** และ **Reboot**
            """)
    
    st.markdown("---")
    
    # เมนูหลัก
    st.markdown("### 📋 เมนู")
    menu = st.radio(
        "เลือกหน้าต้องการ",
        ["🏠 หน้าแรก", 
         "⚡ เล่นสั้น", 
         "💰 เล่นยาว", 
         "🕵️ อ่านเจ้ามือ", 
         "📊 ทดสอบกลยุทธ์",
         "📓 สมุดบันทึกการซื้อขาย"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # แสดงข้อมูลเพิ่มเติม
    st.markdown("**💡 Tips:**")
    st.caption("""
    - เล่นสั้น: วิเคราะห์รายตัว + กราฟ
    - เล่นยาว: ดูปัจจัยพื้นฐาน 10 ปี
    - อ่านเจ้ามือ: NVDR, Big Lot
    - ทดสอบกลยุทธ์: Backtest
    """)
    
    st.markdown("---")
    st.caption("SET SMART AI Trader v0.1.0")

# ============================================
# 🔴 เนื้อหาตามหน้าที่เลือก
# ============================================

# ---------- หน้าแรก ----------
if menu == "🏠 หน้าแรก":
    st.title("📈 SET SMART AI Trader Dashboard")
    
    # แถวแสดงสถานะ
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("สถานะ API", "พร้อมใช้งาน" if "✅" in api_status else "รอตั้งค่า")
    
    with col2:
        st.metric("โมดูลที่พร้อม", "5/5")
    
    with col3:
        st.metric("เวลาล่าสุด", datetime.now().strftime("%H:%M:%S"))
    
    with col4:
        st.metric("วันที่", datetime.now().strftime("%d/%m/%Y"))
    
    st.markdown("---")
    
    # แสดงภาพรวม 2 คอลัมน์
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 คำแนะนำการใช้งาน")
        
        with st.expander("⚡ เล่นสั้น", expanded=True):
            st.markdown("""
            - วิเคราะห์หุ้นรายตัวแบบละเอียด
            - ดูราคาจริง, Volume, RSI
            - กราฟแท่งเทียน + Indicators
            - วิเคราะห์ Elliott Wave เบื้องต้น
            - ดูเจตนารายใหญ่ (NVDR, Big Lot)
            """)
        
        with st.expander("💰 เล่นยาว"):
            st.markdown("""
            - วิเคราะห์ 2 สไตล์: Growth / Dividend
            - ดูข้อมูลย้อนหลัง 10 ปี (EPS, ROE, ปันผล)
            - คำนวณคะแนน巴菲特 (Buffett Score)
            - เปรียบเทียบ P/E กับค่าเฉลี่ย
            - แนะนำ จังหวะซื้อ-ขาย
            """)
        
        with st.expander("🕵️ อ่านเจ้ามือ"):
            st.markdown("""
            - ดู NVDR Flow รายวัน-รายสัปดาห์
            - วิเคราะห์ Big Lot
            - ดู Short Sales
            - ตรวจจับการ Accumulation/Distribution
            """)
        
        with st.expander("📊 ทดสอบกลยุทธ์"):
            st.markdown("""
            - ทดสอบกลยุทธ์ย้อนหลัง
            - ดู Sharpe Ratio, Win Rate
            - เปรียบเทียบหลายกลยุทธ์
            """)
    
    with col2:
        st.subheader("📊 ตัวอย่างหุ้นในตลาด")
        
        # ตัวอย่างข้อมูลหุ้น
        sample_data = pd.DataFrame({
            "หุ้น": ["SCC", "PTT", "ADVANC", "CPALL", "KCE", "GULF", "PTTEP"],
            "ราคาล่าสุด": [228.0, 34.5, 245.0, 58.5, 19.9, 45.2, 148.0],
            "เปลี่ยนแปลง": ["+2.3%", "+1.2%", "-0.5%", "+0.8%", "-1.2%", "+1.5%", "+0.3%"],
            "Volume (M)": [8.2, 12.5, 3.4, 5.6, 2.1, 4.8, 6.3]
        })
        
        st.dataframe(sample_data, use_container_width=True)
        
        # กราฟตัวอย่าง
        st.subheader("📈 SET Index ภาพรวม")
        
        # สร้างข้อมูลตัวอย่าง
        dates = pd.date_range(end=datetime.now(), periods=30).tolist()
        set_prices = [1600 + i*2 + np.random.randint(-10, 10) for i in range(30)]
        
        chart_data = pd.DataFrame({
            "date": dates,
            "SET Index": set_prices
        })
        
        st.line_chart(chart_data.set_index("date"))

# ---------- เล่นสั้น (อัปเดทแล้ว!) ----------
elif menu == "⚡ เล่นสั้น":
    short_term.show()  # เรียกใช้จาก pages/short_term.py

# ---------- เล่นยาว ----------
elif menu == "💰 เล่นยาว":
    st.title("💰 ลงทุนระยะยาวสไตล์巴菲特")
    st.info("📝 กำลังพัฒนา... (จะมาเร็วๆ นี้)")

# ---------- อ่านเจ้ามือ ----------
elif menu == "🕵️ อ่านเจ้ามือ":
    st.title("🕵️ วิเคราะห์พฤติกรรมรายใหญ่")
    st.info("📝 กำลังพัฒนา... (จะมาเร็วๆ นี้)")

# ---------- ทดสอบกลยุทธ์ ----------
elif menu == "📊 ทดสอบกลยุทธ์":
    st.title("📊 ทดสอบกลยุทธ์ย้อนหลัง")
    st.info("📝 กำลังพัฒนา... (จะมาเร็วๆ นี้)")

# ---------- สมุดบันทึกการซื้อขาย ----------
elif menu == "📓 สมุดบันทึกการซื้อขาย":
    st.title("📓 สมุดบันทึกการซื้อขาย (Trading Journal)")
    st.info("📝 กำลังพัฒนา... (จะมาเร็วๆ นี้)")

# ============================================
# 🔴 Footer
# ============================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.8em;'>"
    "SET SMART AI Trader | พัฒนาโดยใช้ Streamlit | ข้อมูลจาก SET SMART API"
    "</div>",
    unsafe_allow_html=True
)
