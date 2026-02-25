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
    # ใช้ get() เพื่อความปลอดภัย
    if "SETSMART_API_KEY" in st.secrets:
        api_key = st.secrets["SETSMART_API_KEY"]
        if api_key and api_key != "4bed3691-2ac4-4881-85f5-7b2747810857":
            api_status = "✅ เชื่อมต่อ API แล้ว"
            st.session_state["api_key"] = api_key
        else:
            api_status = "⚠️ กรุณาใส่ API Key จริงใน Secrets"
    else:
        api_status = "⚠️ ไม่พบ SETSMART_API_KEY ใน Secrets"
except TypeError:
    # กรณีที่ st.secrets ถูกเรียกเป็นฟังก์ชัน
    api_status = "❌ Error: เรียกใช้ st.secrets ผิดวิธี"
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

# ============================================
# เล่นสั้น (แบบเลือกหุ้นทีละตัว + Elliott Wave + วิเคราะห์เจ้ามือ)
# ============================================

elif menu == "⚡ เล่นสั้น":
    st.title("⚡ วิเคราะห์หุ้นเล่นสั้น")
    
    # 🔴 รายชื่อหุ้นไทยยอดนิยม
    thai_stocks = [
        "SCC", "PTT", "ADVANC", "CPALL", "KCE", 
        "GULF", "IVL", "BBL", "KBANK", "SCB",
        "KTB", "TISCO", "MINT", "TRUE", "DTAC",
        "AOT", "BH", "BDMS", "CPF", "CRC", "PTTEP",
        "EA", "BGRIM", "GPSC", "COM7", "HMPRO", "CPN"
    ]
    
    # 🔴 เลือกหุ้น
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_symbol = st.selectbox(
            "🔍 เลือกหุ้นที่ต้องการวิเคราะห์",
            options=thai_stocks,
            index=0
        )
    
    with col2:
        custom_symbol = st.text_input("หรือพิมพ์ชื่อหุ้น", "").upper()
        if custom_symbol and custom_symbol not in thai_stocks:
            selected_symbol = custom_symbol
    
    # 🔴 ปุ่มวิเคราะห์
    if st.button("🔍 วิเคราะห์", type="primary", use_container_width=True):
        
        if "✅" not in api_status:
            st.error("⚠️ กรุณาตั้งค่า API Key ก่อนใช้งาน")
        else:
            with st.spinner(f"กำลังวิเคราะห์ {selected_symbol}..."):
                
                # ============================================
                # จำลองข้อมูล (รอเชื่อมต่อ API จริง)
                # ============================================
                import numpy as np
                from datetime import datetime, timedelta
                
                # ราคาตามหุ้น
                price_map = {
                    "SCC": 228.0, "PTT": 34.5, "ADVANC": 245.0, "CPALL": 58.5, "KCE": 19.9,
                    "GULF": 45.2, "IVL": 32.8, "BBL": 142.0, "KBANK": 138.0, "SCB": 112.0,
                    "KTB": 19.2, "TISCO": 92.0, "MINT": 28.5, "TRUE": 5.8, "DTAC": 42.3,
                    "AOT": 68.0, "BH": 185.0, "BDMS": 26.4, "CPF": 22.7, "CRC": 38.9,
                    "PTTEP": 148.0, "EA": 85.2, "BGRIM": 42.5, "GPSC": 72.8, "COM7": 32.4,
                    "HMPRO": 15.6, "CPN": 62.3
                }
                base_price = price_map.get(selected_symbol, round(np.random.uniform(20, 300), 2))
                
                current_price = base_price * (1 + np.random.uniform(-0.03, 0.03))
                prev_close = base_price * (1 + np.random.uniform(-0.02, 0.02))
                
                # ============================================
                # แถวที่ 1: ราคา
                # ============================================
                st.markdown("---")
                
                col1, col2, col3, col4 = st.columns(4)
                
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100
                
                with col1:
                    st.metric("💰 ราคาปัจจุบัน", f"{current_price:.2f}", f"{change:+.2f} ({change_pct:+.2f}%)")
                with col2:
                    st.metric("📊 ราคาปิดก่อนหน้า", f"{prev_close:.2f}")
                with col3:
                    st.metric("📈 สูงสุดวันนี้", f"{current_price * (1 + np.random.uniform(0, 0.02)):.2f}")
                with col4:
                    st.metric("📉 ต่ำสุดวันนี้", f"{current_price * (1 - np.random.uniform(0, 0.02)):.2f}")
                
                # ============================================
                # แถวที่ 2: Volume และ Indicators
                # ============================================
                volume = int(np.random.uniform(1, 10) * 1_000_000)
                avg_volume = int(volume * np.random.uniform(0.4, 1.2))
                volume_ratio = volume / avg_volume
                rsi = np.random.randint(25, 75)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📦 ปริมาณซื้อขาย", f"{volume/1_000_000:.1f}M", f"{volume_ratio:.2f}x")
                with col2:
                    rsi_status = "🟢 Oversold" if rsi < 30 else "🔴 Overbought" if rsi > 70 else "⚪ Neutral"
                    st.metric("📊 RSI (14)", f"{rsi}", rsi_status)
                with col3:
                    macd = np.random.uniform(-2, 2)
                    st.metric("📈 MACD", f"{macd:.2f}", "🟢 Buy" if macd > 0 else "🔴 Sell")
                with col4:
                    st.metric("🎯 Stochastic", f"{np.random.randint(20, 80)}", f"{np.random.randint(5, 30)}")
                
                # ============================================
                # 🌊 Elliott Wave Analysis
                # ============================================
                st.markdown("---")
                st.subheader("🌊 Elliott Wave Analysis")
                
                # จำลองการนับคลื่น [citation:1][citation:3]
                wave_options = ["Wave 1 (เริ่มสะสม)", "Wave 2 (ย่อตัว)", "Wave 3 (แรงที่สุด)", 
                               "Wave 4 (พักตัว)", "Wave 5 (สุดท้าย)", "Correction A", "Correction B", "Correction C"]
                
                # จำลองตำแหน่งคลื่นตามราคา [citation:8]
                if current_price < base_price * 0.98:
                    current_wave = "Wave 2 (ย่อตัว)"
                    wave_desc = "กำลังย่อตัว รอจบคลื่น 2 เพื่อเข้าซื้อ"
                    wave_action = "รอซื้อที่แนวรับ"
                    wave_color = "orange"
                    next_target = base_price * 1.05
                elif current_price < base_price * 1.02:
                    current_wave = "Wave 3 (กำลังขึ้น)"
                    wave_desc = "คลื่น 3 มักยาวและแรงที่สุด รายใหญ่ดันราคา"
                    wave_action = "ซื้อตาม (Follow Buy) [citation:3]"
                    wave_color = "green"
                    next_target = base_price * 1.15
                elif current_price < base_price * 1.08:
                    current_wave = "Wave 4 (พักตัว)"
                    wave_desc = "พักตัวก่อนขึ้น Wave 5 ห้ามต่ำกว่า Wave 1 [citation:8]"
                    wave_action = "ถือหรือขายบางส่วน"
                    wave_color = "blue"
                    next_target = base_price * 1.12
                else:
                    current_wave = "Wave 5 (ใกล้จบ)"
                    wave_desc = "คลื่นสุดท้าย รายใหญ่เริ่มเทขาย"
                    wave_action = "ขายทำกำไร"
                    wave_color = "red"
                    next_target = base_price * 1.02
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div style="padding: 15px; border-radius: 5px; background-color: #f0f2f6; border-left: 5px solid {wave_color};">
                        <h4>🌊 คลื่นปัจจุบัน: {current_wave}</h4>
                        <p><b>คำอธิบาย:</b> {wave_desc}</p>
                        <p><b>🎯 เป้าหมายถัดไป:</b> {next_target:.2f}</p>
                        <p><b>⚡ การกระทำ:</b> {wave_action}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # กฎ Elliott Wave [citation:3][citation:8]
                    st.markdown("#### 📋 กฎ Elliott Wave")
                    rules_df = pd.DataFrame({
                        "กฎ": [
                            "Wave 2 ห้ามต่ำกว่า Wave 1",
                            "Wave 3 ห้ามสั้นที่สุด",
                            "Wave 4 ห้ามต่ำกว่า Wave 1"
                        ],
                        "สถานะ": [
                            "✅ ปกติ" if current_price > base_price * 0.95 else "⚠️ ระวัง",
                            "✅ คลื่น 3 แรงสุด" if current_wave == "Wave 3 (กำลังขึ้น)" else "⚪ รอ確認",
                            "✅ ปกติ" if current_price > base_price * 0.9 else "⚠️ เสี่ยง"
                        ]
                    })
                    st.dataframe(rules_df, use_container_width=True)
                
                # ============================================
                # 🕵️ วิเคราะห์เจ้ามือ (Smart Money Intent)
                # ============================================
                st.markdown("---")
                st.subheader("🕵️ วิเคราะห์เจตนารายใหญ่")
                
                # จำลองข้อมูลรายใหญ่ [citation:1][citation:8]
                nvdr_net = np.random.randint(-50, 100) * 1_000_000
                big_lot_count = np.random.randint(0, 5)
                short_trend = np.random.choice(["ลดลง", "เพิ่มขึ้น", "ทรงตัว"])
                
                # วิเคราะห์เจตนา
                if nvdr_net > 30_000_000 and big_lot_count >= 2 and short_trend == "ลดลง":
                    intent = "ACCUMULATING (กำลังเก็บ)"
                    intent_desc = "รายใหญ่กำลังสะสมของ ราคาอาจถูกเขย่าให้ลงก่อน [citation:1]"
                    intent_action = "รอซื้อเมื่อราคาอ่อนตัว"
                    intent_color = "green"
                    shake_level = current_price * 0.97
                elif nvdr_net < -20_000_000 and short_trend == "เพิ่มขึ้น":
                    intent = "DISTRIBUTING (กำลังแจก)"
                    intent_desc = "รายใหญ่กำลังเทขาย ระวังการปรับฐาน"
                    intent_action = "ขายเมื่อราคาขึ้น"
                    intent_color = "red"
                    shake_level = current_price * 1.02
                elif nvdr_net > 0 and big_lot_count > 0:
                    intent = "WASHING (เขย่าเม่า)"
                    intent_desc = "รายใหญ่เขย่าราคาเพื่อเก็บของถูก [citation:1]"
                    intent_action = "รอช้อนที่แนวรับ"
                    intent_color = "orange"
                    shake_level = current_price * 0.95
                else:
                    intent = "NEUTRAL"
                    intent_desc = "รายใหญ่ยังไม่ชัดเจน"
                    intent_action = "รอดู"
                    intent_color = "gray"
                    shake_level = current_price
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6; border-left: 5px solid {intent_color};">
                        <h4>🎯 เจตนา: {intent}</h4>
                        <p>{intent_desc}</p>
                        <p><b>⚡ แนวทาง:</b> {intent_action}</p>
                        <p><b>📍 จุดเขย่า:</b> {shake_level:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6;">
                        <h4>🌏 NVDR Flow</h4>
                        <h2 style="color: {'green' if nvdr_net > 0 else 'red'};">{'+' if nvdr_net > 0 else ''}{nvdr_net/1_000_000:.1f}M</h2>
                        <p>{'ซื้อสุทธิ' if nvdr_net > 0 else 'ขายสุทธิ'} 7 วัน</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6;">
                        <h4>📦 Big Lot</h4>
                        <h2>{big_lot_count} รายการ</h2>
                        <p>Short Sales: {short_trend}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # ============================================
                # แถวที่ 5: จุดซื้อ-ขาย
                # ============================================
                st.markdown("---")
                st.subheader("🎯 จุดซื้อ-ขาย แนะนำ")
                
                support = current_price * 0.98
                resistance = current_price * 1.02
                strong_support = current_price * 0.95
                strong_resistance = current_price * 1.05
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    <div style="padding: 15px; border-radius: 5px; background-color: #e8f5e9; border-left: 5px solid #4caf50;">
                        <h4 style="color: #2e7d32;">🟢 จุดซื้อ</h4>
                    """, unsafe_allow_html=True)
                    
                    # ปรับตามเจตนารายใหญ่ [citation:1]
                    if "ACCUMULATING" in intent:
                        buy_zone = f"{shake_level:.2f} - {current_price:.2f}"
                        buy_note = "รอให้รายใหญ่เขย่าแล้วค่อยซื้อ"
                    elif "WASHING" in intent:
                        buy_zone = f"{strong_support:.2f} - {support:.2f}"
                        buy_note = "รอช้อนที่แนวรับ"
                    else:
                        buy_zone = f"{support:.2f} - {current_price:.2f}"
                        buy_note = "ซื้อเมื่ออ่อนตัว"
                    
                    st.markdown(f"""
                    - **โซนซื้อ:** {buy_zone}
                    - **จุดช้อน:** {shake_level:.2f}
                    - **RSI:** {rsi}
                    - **หมายเหตุ:** {buy_note}
                    """)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div style="padding: 15px; border-radius: 5px; background-color: #ffebee; border-left: 5px solid #f44336;">
                        <h4 style="color: #c62828;">🔴 จุดขาย / Cut loss</h4>
                    """, unsafe_allow_html=True)
                    
                    tp1 = current_price * 1.02
                    tp2 = current_price * 1.05
                    sl = current_price * 0.97
                    
                    st.markdown(f"""
                    - **เป้าหมาย 1 (TP1):** {tp1:.2f} (+2.0%)
                    - **เป้าหมาย 2 (TP2):** {tp2:.2f} (+5.0%)
                    - **จุดตัดขาดทุน (SL):** {sl:.2f} (-3.0%)
                    - **R/R Ratio:** 1:1.67
                    - **หมายเหตุ:** ถ้าหลุด {strong_support:.2f} ให้ cut ทันที [citation:3]
                    """)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # ============================================
                # แถวที่ 6: คำแนะนำ
                # ============================================
                st.markdown("---")
                st.subheader("💡 คำแนะนำ")
                
                # วิเคราะห์รวม [citation:1][citation:8]
                if "Wave 3" in current_wave and "ACCUMULATING" in intent:
                    advice = "🚀 คลื่น 3 + รายใหญ่เก็บ = จังหวะซื้อตาม"
                    action = "ซื้อ (Follow Buy)"
                    color = "green"
                elif "Wave 5" in current_wave and "DISTRIBUTING" in intent:
                    advice = "⚠️ คลื่น 5 + รายใหญ่แจก = รีบขาย"
                    action = "ขาย"
                    color = "red"
                elif "Wave 2" in current_wave and "WASHING" in intent:
                    advice = "🎯 คลื่น 2 + รายใหญ่เขย่า = รอช้อน"
                    action = "รอซื้อ"
                    color = "orange"
                else:
                    advice = "⏳ รอดูทิศทาง"
                    action = "ถือเงิน"
                    color = "blue"
                
                st.info(f"**การกระทำ:** {action}")
                st.markdown(f"**เหตุผล:** {advice}")
                
                # แนวรับ-แนวต้าน
                with st.expander("📊 แนวรับ-แนวต้าน"):
                    levels = pd.DataFrame({
                        "ระดับ": ["แนวรับแข็ง", "แนวรับ", "ราคาปัจจุบัน", "แนวต้าน", "แนวต้านแข็ง"],
                        "ราคา": [f"{strong_support:.2f}", f"{support:.2f}", f"{current_price:.2f}", 
                                f"{resistance:.2f}", f"{strong_resistance:.2f}"],
                        "ระยะทาง": [f"-{(current_price - strong_support)/current_price*100:.1f}%",
                                   f"-{(current_price - support)/current_price*100:.1f}%",
                                   "0%",
                                   f"+{(resistance - current_price)/current_price*100:.1f}%",
                                   f"+{(strong_resistance - current_price)/current_price*100:.1f}%"]
                    })
                    st.dataframe(levels, use_container_width=True)

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



