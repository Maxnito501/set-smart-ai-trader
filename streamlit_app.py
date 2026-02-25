#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Streamlit Dashboard สำหรับ SET SMART AI Trader
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# เพิ่ม path ให้หา module เจอ
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzers import ShortTermAnalyzer, LongTermAnalyzer, SmartMoneyAnalyzer
from config.settings import settings

# 🔴 ตั้งค่าหน้า
st.set_page_config(
    page_title="SET SMART AI Trader",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔴 Sidebar
st.sidebar.title("📊 SET SMART AI Trader")
st.sidebar.markdown(f"**วันนี้:** {datetime.now().strftime('%d/%m/%Y')}")

# ตรวจสอบ API Key
api_key = settings.SETSMART_API_KEY
if not api_key or api_key == "YOUR_API_KEY_HERE":
    st.sidebar.error("⚠️ กรุณาใส่ API Key ใน .env")
else:
    st.sidebar.success("✅ เชื่อมต่อ API แล้ว")

# เลือกหน้า
page = st.sidebar.radio(
    "เมนู",
    ["🏠 หน้าแรก", "⚡ เล่นสั้น", "💰 เล่นยาว", "🕵️ อ่านเจ้ามือ", "📊 Backtest"]
)

# 🔴 หน้าแรก
if page == "🏠 หน้าแรก":
    st.title("📈 SET SMART AI Trader Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("สถานะ API", "พร้อมใช้งาน" if api_key else "รอตั้งค่า")
    
    with col2:
        st.metric("โมดูลที่พร้อม", "4/4")
    
    with col3:
        st.metric("เวลาล่าสุด", datetime.now().strftime("%H:%M:%S"))
    
    st.markdown("---")
    
    st.subheader("📋 คำแนะนำการใช้งาน")
    st.markdown("""
    - **⚡ เล่นสั้น**: วิเคราะห์หุ้นเก็งกำไร ดู Volume Spike, NVDR, RSI
    - **💰 เล่นยาว**: คัดกรองหุ้นปันผลดี คำนวณ DCA
    - **🕵️ อ่านเจ้ามือ**: ดูพฤติกรรมรายใหญ่ NVDR, Big Lot
    - **📊 Backtest**: ทดสอบกลยุทธ์ย้อนหลัง
    """)

# 🔴 เล่นสั้น
elif page == "⚡ เล่นสั้น":
    st.title("⚡ วิเคราะห์หุ้นเล่นสั้น")
    
    # เลือกหุ้น
    symbols = st.text_input("ใส่ชื่อหุ้น (คั่นด้วยคอมม่า)", "SCC, PTT, ADVANC")
    symbol_list = [s.strip() for s in symbols.split(",")]
    
    if st.button("วิเคราะห์"):
        with st.spinner("กำลังวิเคราะห์..."):
            try:
                with ShortTermAnalyzer() as analyzer:
                    results = analyzer.scan_watchlist(symbol_list)
                    
                    # สร้าง DataFrame
                    data = []
                    for r in results:
                        data.append({
                            "หุ้น": r["symbol"],
                            "คะแนน": r["score"],
                            "คำแนะนำ": r["recommendation"],
                            "สัญญาณ": ", ".join(r["signals"][:2]) if r["signals"] else "-",
                            "ราคา": r.get("technical", {}).get("current_price", 0)
                        })
                    
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    
                    # แสดงรายละเอียด
                    for r in results:
                        if r["score"] >= 5:
                            with st.expander(f"📈 {r['symbol']} (คะแนน {r['score']})"):
                                st.json(r)
                            
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

# 🔴 เล่นยาว
elif page == "💰 เล่นยาว":
    st.title("💰 วิเคราะห์หุ้นเล่นยาว (ปันผล)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        min_yield = st.slider("Dividend Yield ขั้นต่ำ (%)", 2.0, 10.0, 4.0, 0.5)
    
    with col2:
        min_roe = st.slider("ROE ขั้นต่ำ (%)", 5.0, 30.0, 10.0, 1.0)
    
    if st.button("คัดกรอง"):
        with st.spinner("กำลังคัดกรอง..."):
            try:
                with LongTermAnalyzer() as analyzer:
                    stocks = analyzer.screen_high_dividend(
                        min_yield=min_yield,
                        min_roe=min_roe
                    )
                    
                    if stocks:
                        df = pd.DataFrame(stocks[:20])
                        st.dataframe(df, use_container_width=True)
                        
                        # DCA Calculator
                        st.subheader("📅 DCA Calculator")
                        budget = st.number_input("งบประมาณต่อเดือน (บาท)", 5000, 100000, 10000)
                        
                        dca = analyzer.find_dca_opportunities(budget_per_month=budget)
                        if dca:
                            dca_df = pd.DataFrame(dca)
                            st.dataframe(dca_df, use_container_width=True)
                    else:
                        st.warning("ไม่พบหุ้นที่ตรงตามเกณฑ์")
                        
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

# 🔴 อ่านเจ้ามือ
elif page == "🕵️ อ่านเจ้ามือ":
    st.title("🕵️ วิเคราะห์พฤติกรรมรายใหญ่")
    
    symbol = st.text_input("ใส่ชื่อหุ้น", "SCC")
    
    if st.button("วิเคราะห์"):
        with st.spinner("กำลังวิเคราะห์..."):
            try:
                with SmartMoneyAnalyzer() as analyzer:
                    result = analyzer.analyze_smart_money(symbol)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("คะแนน", f"{result['score']}/10")
                    
                    with col2:
                        st.metric("คำแนะนำ", result.get('recommendation', '-'))
                    
                    with col3:
                        st.metric("สัญญาณ", len(result['signals']))
                    
                    st.markdown("---")
                    
                    # แสดงรายละเอียด
                    tabs = st.tabs(["NVDR", "Big Lot", "A/D Line", "ทั้งหมด"])
                    
                    with tabs[0]:
                        if "nvdr" in result:
                            st.json(result["nvdr"])
                    
                    with tabs[1]:
                        if "big_lot" in result:
                            st.json(result["big_lot"])
                    
                    with tabs[2]:
                        if "ad_line" in result:
                            st.json(result["ad_line"])
                    
                    with tabs[3]:
                        st.json(result)
                        
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

# 🔴 Backtest
elif page == "📊 Backtest":
    st.title("📊 ทดสอบกลยุทธ์ย้อนหลัง")
    
    symbol = st.text_input("หุ้น", "SCC")
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("วันที่เริ่มต้น", datetime(2025, 1, 1))
    
    with col2:
        end_date = st.date_input("วันที่สิ้นสุด", datetime(2025, 12, 31))
    
    strategy = st.selectbox(
        "กลยุทธ์",
        ["MA Crossover", "RSI", "Buy & Hold"]
    )
    
    if st.button("รัน Backtest"):
        st.info("กำลังพัฒนา... (จะ implement ในขั้นตอนถัดไป)")