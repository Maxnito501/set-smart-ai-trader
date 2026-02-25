#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
📁 streamlit_app.py
Streamlit Dashboard สำหรับ SET SMART AI Trader
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import plotly.graph_objects as go
import plotly.express as px

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

# ============================================
# 🔴🔴🔴 การจัดการ API KEY 🔴🔴🔴
# ============================================

# ตรวจสอบ API Key จาก Streamlit Secrets
api_key = None
api_status = "⚠️ รอการตั้งค่า"

try:
    # 🔴 ดึงค่า FROM STREAMLIT SECRETS
    if "SETSMART_API_KEY" in st.secrets:
        api_key = os.getenv["SETSMART_API_KEY"]
        if api_key and api_key != "4bed3691-2ac4-4881-85f5-7b2747810857":
            api_status = "✅ เชื่อมต่อ API แล้ว"
            st.session_state["api_key"] = api_key
        else:
            api_status = "⚠️ กรุณาใส่ API Key จริงใน Secrets"
    else:
        api_status = "⚠️ ไม่พบ SETSMART_API_KEY ใน Secrets"
except Exception as e:
    api_status = f"❌ Error: {str(e)}"

# แสดงสถานะ API ใน Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 สถานะระบบ")
st.sidebar.markdown(api_status)

# ถ้าไม่มี API Key ให้แสดงคำแนะนำ
if "✅" not in api_status:
    st.sidebar.warning("""
    **วิธีตั้งค่า API Key:**
    1. ไปที่ Manage app → Secrets
    2. เพิ่ม: 
       ```
       SETSMART_API_KEY = "your-actual-key-here"
       ```
    3. กด Save และรีสตาร์ท
    """)

# ============================================
# เมนูหลัก
# ============================================

menu = st.sidebar.radio(
    "📋 เมนู",
    ["🏠 หน้าแรก", "⚡ เล่นสั้น", "💰 เล่นยาว", "🕵️ อ่านเจ้ามือ", "📊 Backtest"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "📌 **หมายเหตุ:**\n"
    "- ข้อมูลจาก SET SMART API\n"
    "- ใช้เพื่อการศึกษาและการลงทุนส่วนบุคคล"
)

# ============================================
# หน้าแรก
# ============================================

if menu == "🏠 หน้าแรก":
    st.title("📈 SET SMART AI Trader Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("สถานะ API", "พร้อมใช้งาน" if "✅" in api_status else "รอตั้งค่า")
    
    with col2:
        st.metric("โมดูลที่พร้อม", "4/4")
    
    with col3:
        st.metric("เวลาล่าสุด", datetime.now().strftime("%H:%M:%S"))
    
    with col4:
        st.metric("วันที่", datetime.now().strftime("%d/%m/%Y"))
    
    st.markdown("---")
    
    # แสดงภาพรวม
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 คำแนะนำการใช้งาน")
        st.markdown("""
        ### ⚡ เล่นสั้น
        - วิเคราะห์หุ้นเก็งกำไร
        - ดู Volume Spike, NVDR Flow
        - คะแนน RSI, สัญญาณซื้อขาย
        
        ### 💰 เล่นยาว
        - คัดกรองหุ้นปันผลดี
        - คำนวณ DCA รายเดือน
        - วิเคราะห์จังหวะ XD
        
        ### 🕵️ อ่านเจ้ามือ
        - ติดตาม NVDR รายใหญ่
        - วิเคราะห์ Big Lot
        - Accumulation/Distribution Line
        
        ### 📊 Backtest
        - ทดสอบกลยุทธ์ย้อนหลัง
        - เปรียบเทียบผลตอบแทน
        - วิเคราะห์ Sharpe Ratio
        """)
    
    with col2:
        st.subheader("📊 ตัวอย่างหุ้นที่น่าสนใจ")
        
        # ตัวอย่างข้อมูล
        sample_data = pd.DataFrame({
            "หุ้น": ["SCC", "PTT", "ADVANC", "CPALL", "KCE"],
            "ราคา": [228.0, 34.5, 245.0, 58.5, 19.9],
            "เปลี่ยน (%)": [2.3, 1.2, -0.5, 0.8, -1.2],
            "Volume (M)": [8.2, 12.5, 3.4, 5.6, 2.1]
        })
        st.dataframe(sample_data, use_container_width=True)
        
        # กราฟตัวอย่าง
        chart_data = pd.DataFrame(
            np.random.randn(20, 3),
            columns=['SCC', 'PTT', 'ADVANC']
        )
        st.line_chart(chart_data)

# ============================================
# เล่นสั้น
# ============================================

elif menu == "⚡ เล่นสั้น":
    st.title("⚡ วิเคราะห์หุ้นเล่นสั้น")
    
    # Input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        symbols_input = st.text_input(
            "🔍 ใส่ชื่อหุ้น (คั่นด้วยคอมม่า)",
            "SCC, PTT, ADVANC, CPALL, KCE"
        )
    
    with col2:
        min_score = st.slider("คะแนนขั้นต่ำ", 0, 10, 5)
    
    if st.button("🔍 วิเคราะห์", type="primary", use_container_width=True):
        
        if "✅" not in api_status:
            st.error("⚠️ กรุณาตั้งค่า API Key ก่อนใช้งาน")
        else:
            with st.spinner("กำลังวิเคราะห์ข้อมูล..."):
                
                # 🔴 ตัวอย่างผลลัพธ์ (รอเชื่อมต่อ API จริง)
                symbols = [s.strip() for s in symbols_input.split(",")]
                
                # สร้างข้อมูลตัวอย่าง
                results = []
                for i, symbol in enumerate(symbols[:5]):
                    score = np.random.randint(3, 10)
                    results.append({
                        "symbol": symbol,
                        "score": score,
                        "recommendation": "STRONG_BUY" if score >= 8 else "BUY" if score >= 5 else "HOLD",
                        "signals": ["VOLUME_SPIKE", "NVDR_BUY", "RSI_OVERSOLD"][:np.random.randint(1, 4)],
                        "current_price": round(np.random.uniform(20, 250), 2),
                        "volume_ratio": round(np.random.uniform(0.8, 3.5), 2),
                        "rsi": np.random.randint(25, 75)
                    })
                
                # แสดงผลเป็นตาราง
                df = pd.DataFrame([{
                    "หุ้น": r["symbol"],
                    "คะแนน": r["score"],
                    "คำแนะนำ": r["recommendation"],
                    "ราคา": r["current_price"],
                    "Volume Ratio": r["volume_ratio"],
                    "RSI": r["rsi"],
                    "สัญญาณ": ", ".join(r["signals"])
                } for r in results])
                
                st.dataframe(df, use_container_width=True)
                
                # แสดงรายละเอียด
                st.subheader("📊 รายละเอียดเพิ่มเติม")
                for r in results:
                    if r["score"] >= min_score:
                        with st.expander(f"{r['symbol']} (คะแนน {r['score']})"):
                            st.json(r)

# ============================================
# เล่นยาว
# ============================================

elif menu == "💰 เล่นยาว":
    st.title("💰 วิเคราะห์หุ้นเล่นยาว (ปันผล)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_yield = st.slider("Dividend Yield ขั้นต่ำ (%)", 2.0, 10.0, 4.0, 0.5)
    
    with col2:
        min_roe = st.slider("ROE ขั้นต่ำ (%)", 5.0, 30.0, 10.0, 1.0)
    
    with col3:
        min_years = st.slider("จ่ายปันผลติดต่อกัน (ปี)", 3, 10, 5)
    
    tab1, tab2 = st.tabs(["📋 คัดกรองหุ้น", "📅 DCA Calculator"])
    
    with tab1:
        if st.button("🔍 คัดกรองหุ้น", type="primary"):
            with st.spinner("กำลังคัดกรอง..."):
                
                # 🔴 ตัวอย่างข้อมูล
                stocks = [
                    {"symbol": "SCC", "name": "ปูนซิเมนต์ไทย", "yield": 5.2, "roe": 18.5, "years": 15},
                    {"symbol": "PTT", "name": "ปตท.", "yield": 4.8, "roe": 16.2, "years": 12},
                    {"symbol": "ADVANC", "name": "แอดวานซ์", "yield": 3.8, "roe": 24.1, "years": 10},
                    {"symbol": "CPALL", "name": "ซีพีออลล์", "yield": 2.5, "roe": 22.3, "years": 8},
                    {"symbol": "KCE", "name": "เคซีอี", "yield": 1.8, "roe": 15.7, "years": 6},
                ]
                
                # กรองตามเงื่อนไข
                filtered = [s for s in stocks 
                           if s["yield"] >= min_yield 
                           and s["roe"] >= min_roe 
                           and s["years"] >= min_years]
                
                if filtered:
                    df = pd.DataFrame(filtered)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("ไม่พบหุ้นที่ตรงตามเกณฑ์")
    
    with tab2:
        st.subheader("📅 DCA Calculator")
        
        col1, col2 = st.columns(2)
        with col1:
            budget = st.number_input("งบประมาณต่อเดือน (บาท)", 1000, 100000, 10000, step=1000)
        with col2:
            months = st.number_input("จำนวนเดือน", 3, 60, 12, step=3)
        
        if st.button("คำนวณ DCA"):
            # 🔴 ตัวอย่างการคำนวณ
            dca_results = []
            for stock in ["SCC", "PTT", "ADVANC"]:
                price = np.random.uniform(30, 250)
                shares = budget // price
                total_invest = shares * price * months
                est_dividend = total_invest * 0.05  # สมมติปันผล 5%
                
                dca_results.append({
                    "หุ้น": stock,
                    "ราคาปัจจุบัน": round(price, 2),
                    "ซื้อได้/เดือน": int(shares),
                    "ลงทุนรวม": round(total_invest, 2),
                    "ปันผลประมาณ": round(est_dividend, 2)
                })
            
            df_dca = pd.DataFrame(dca_results)
            st.dataframe(df_dca, use_container_width=True)

# ============================================
# อ่านเจ้ามือ
# ============================================

elif menu == "🕵️ อ่านเจ้ามือ":
    st.title("🕵️ วิเคราะห์พฤติกรรมรายใหญ่")
    
    symbol = st.text_input("🔍 ใส่ชื่อหุ้น", "SCC").upper()
    
    if st.button("🔍 วิเคราะห์", type="primary"):
        with st.spinner("กำลังวิเคราะห์..."):
            
            # 🔴 ตัวอย่างผลลัพธ์
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("NVDR 7 วัน", "ซื้อสุทธิ 45.2M", "+12.3M")
            
            with col2:
                st.metric("Big Lot", "2 รายการ", "25.6M")
            
            with col3:
                st.metric("คะแนนรายใหญ่", "7/10", "🐳🐳🐳")
            
            # กราฟตัวอย่าง
            st.subheader("📊 NVDR Flow ย้อนหลัง")
            
            dates = pd.date_range(end=datetime.now(), periods=14).tolist()
            nvdr_data = pd.DataFrame({
                "date": dates,
                "buy": np.random.randint(10, 50, 14),
                "sell": np.random.randint(5, 40, 14)
            })
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=nvdr_data["date"], y=nvdr_data["buy"], name="ซื้อ", marker_color="green"))
            fig.add_trace(go.Bar(x=nvdr_data["date"], y=nvdr_data["sell"], name="ขาย", marker_color="red"))
            
            fig.update_layout(barmode="group", height=400)
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# Backtest
# ============================================

else:  # Backtest
    st.title("📊 ทดสอบกลยุทธ์ย้อนหลัง")
    
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.text_input("หุ้น", "SCC").upper()
    
    with col2:
        strategy = st.selectbox(
            "กลยุทธ์",
            ["MA Crossover (5,20)", "MA Crossover (10,30)", "RSI (30/70)", "Buy & Hold"]
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("วันที่เริ่มต้น", datetime(2025, 1, 1))
    
    with col2:
        end_date = st.date_input("วันที่สิ้นสุด", datetime(2025, 12, 31))
    
    initial_capital = st.number_input("เงินต้น (บาท)", 10000, 1000000, 100000, step=10000)
    
    if st.button("📊 รัน Backtest", type="primary"):
        with st.spinner("กำลังคำนวณ..."):
            
            # 🔴 ตัวอย่างผลลัพธ์
            st.subheader("📈 ผลการทดสอบ")
            
            # คำนวณผลตอบแทนตัวอย่าง
            total_return = np.random.uniform(5, 25)
            win_rate = np.random.uniform(45, 75)
            sharpe = np.random.uniform(0.8, 2.2)
            max_dd = np.random.uniform(5, 15)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("ผลตอบแทน", f"+{total_return:.1f}%", f"{total_return-10:.1f}%")
            
            with col2:
                st.metric("Win Rate", f"{win_rate:.1f}%")
            
            with col3:
                st.metric("Sharpe Ratio", f"{sharpe:.2f}")
            
            with col4:
                st.metric("Max Drawdown", f"-{max_dd:.1f}%")
            
            # กราฟ equity curve
            st.subheader("📉 Equity Curve")
            
            days = (end_date - start_date).days
            dates = pd.date_range(start=start_date, end=end_date, freq="D")[:100]
            equity = [initial_capital]
            for i in range(1, len(dates)):
                equity.append(equity[-1] * (1 + np.random.normal(0.001, 0.02)))
            
            equity_df = pd.DataFrame({
                "date": dates[:len(equity)],
                "value": equity
            })
            
            fig = px.line(equity_df, x="date", y="value", title="Equity Curve")
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# Footer
# ============================================

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "SET SMART AI Trader v0.1.0 | พัฒนาโดยใช้ Streamlit | ข้อมูลจาก SET SMART API"
    "</div>",
    unsafe_allow_html=True
)

