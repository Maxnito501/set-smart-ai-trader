"""
📁 pages/short_term.py
หน้าเล่นสั้น - สำหรับวางแผนหาตังค์กินข้าว
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests

# ============================================
# เรียกใช้ API functions จาก utils (จะสร้างทีหลัง)
# ============================================
def get_realtime_price(symbol):
    """จำลองข้อมูล (รอเชื่อม API จริง)"""
    # สุ่มราคาตามหุ้น
    price_map = {
        "SCC": 228.0, "PTT": 34.5, "ADVANC": 245.0, "CPALL": 58.5, "KCE": 19.9,
        "GULF": 45.2, "IVL": 32.8, "BBL": 142.0, "KBANK": 138.0, "SCB": 112.0,
        "KTB": 19.2, "TISCO": 92.0, "MINT": 28.5, "TRUE": 5.8, "AOT": 68.0,
        "BH": 185.0, "BDMS": 26.4, "CPF": 22.7, "PTTEP": 148.0, "EA": 85.2
    }
    
    base = price_map.get(symbol, 100.0)
    current = base * (1 + np.random.uniform(-0.03, 0.03))
    change = current - base
    change_pct = (change / base) * 100
    
    return {
        "current": round(current, 2),
        "open": round(base * (1 + np.random.uniform(-0.01, 0.01)), 2),
        "high": round(current * (1 + np.random.uniform(0, 0.02)), 2),
        "low": round(current * (1 - np.random.uniform(0, 0.02)), 2),
        "volume": int(np.random.uniform(1, 15) * 1_000_000),
        "change": round(change, 2),
        "change_pct": round(change_pct, 2),
        "prev_close": round(base, 2)
    }

def get_historical(symbol, days=30):
    """จำลองข้อมูลย้อนหลัง"""
    dates = pd.date_range(end=datetime.now(), periods=days).tolist()
    base = 100.0
    
    # สร้างราคาให้มีแนวโน้ม + ความผันผวน
    trend = np.linspace(0, np.random.uniform(-5, 5), days)
    noise = np.random.normal(0, 2, days)
    prices = base + trend + noise
    
    # ทำให้ราคาเป็นบวก
    prices = [max(p, base * 0.8) for p in prices]
    
    volumes = [int(np.random.uniform(1, 10) * 1_000_000) for _ in range(days)]
    
    return dates, prices, volumes

def calculate_rsi(prices, period=14):
    """คำนวณ RSI"""
    if len(prices) < period + 1:
        return 50
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def calculate_ma(prices, period):
    """คำนวณ Moving Average"""
    if len(prices) < period:
        return prices[-1] if prices else 0
    return sum(prices[-period:]) / period

def elliott_wave(prices):
    """วิเคราะห์ Elliott Wave เบื้องต้น"""
    if len(prices) < 20:
        return "ข้อมูลไม่พอ", "neutral", 0
    
    current = prices[-1]
    recent_high = max(prices[-10:])
    recent_low = min(prices[-10:])
    
    if current > recent_high * 0.98:
        if current > prices[-5]:
            return "🌊 คลื่น 3 (กำลังขึ้นแรง)", "buy", recent_high * 1.05
        else:
            return "🌊 คลื่น 5 (ใกล้จบ)", "sell", current
    elif current < recent_low * 1.02:
        if current < prices[-5]:
            return "🌊 คลื่น C (พักฐาน)", "wait", recent_low * 0.95
        else:
            return "🌊 คลื่น 2 (ย่อตัว)", "accumulate", recent_low
    else:
        return "🌊 คลื่น 4 (พักตัว)", "hold", recent_high

# ============================================
# หน้าเล่นสั้น
# ============================================
def show():
    st.title("⚡ เล่นสั้น - หาตังค์กินข้าว")
    st.caption("วิเคราะห์หุ้นรายตัว ดูกราฟ RSI Elliott Wave พร้อมจุดซื้อ-ขาย")
    
    # ============================================
    # รายชื่อหุ้นยอดนิยม
    # ============================================
    popular_stocks = [
        "SCC", "PTT", "ADVANC", "CPALL", "KCE", 
        "GULF", "IVL", "BBL", "KBANK", "SCB",
        "KTB", "TISCO", "MINT", "TRUE", "AOT",
        "BH", "BDMS", "CPF", "PTTEP", "EA"
    ]
    
    # ============================================
    # เลือกหุ้น
    # ============================================
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected = st.selectbox("🔍 เลือกหุ้น", popular_stocks, index=0)
    
    with col2:
        custom = st.text_input("หรือพิมพ์ชื่อ", "").upper()
        if custom and custom not in popular_stocks:
            selected = custom
    
    with col3:
        refresh = st.button("🔄 รีเฟรช", use_container_width=True)
    
    # ============================================
    # ดึงข้อมูล
    # ============================================
    if "last_symbol" not in st.session_state or refresh:
        st.session_state["last_symbol"] = selected
        
        with st.spinner(f"กำลังดึงข้อมูล {selected}..."):
            
            # ราคาปัจจุบัน
            rt = get_realtime_price(selected)
            
            # ข้อมูลย้อนหลัง
            dates, prices, volumes = get_historical(selected, 45)
            
            # คำนวณ Indicators
            rsi = calculate_rsi(prices)
            ma5 = calculate_ma(prices, 5)
            ma10 = calculate_ma(prices, 10)
            ma20 = calculate_ma(prices, 20)
            
            # Elliott Wave
            wave, wave_signal, wave_target = elliott_wave(prices)
            
            # เก็บใน session
            st.session_state["rt"] = rt
            st.session_state["dates"] = dates
            st.session_state["prices"] = prices
            st.session_state["volumes"] = volumes
            st.session_state["rsi"] = rsi
            st.session_state["ma5"] = ma5
            st.session_state["ma10"] = ma10
            st.session_state["ma20"] = ma20
            st.session_state["wave"] = wave
            st.session_state["wave_signal"] = wave_signal
            st.session_state["wave_target"] = wave_target
    
    # ============================================
    # แสดงผล
    # ============================================
    if "rt" in st.session_state:
        rt = st.session_state["rt"]
        
        # ---- แถวที่ 1: ราคา ----
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            delta_color = "normal" if rt["change"] >= 0 else "inverse"
            st.metric(
                "💰 ราคาปัจจุบัน", 
                f"{rt['current']:.2f}",
                delta=f"{rt['change']:+.2f} ({rt['change_pct']:+.2f}%)",
                delta_color=delta_color
            )
        
        with col2:
            st.metric("📊 ราคาเปิด", f"{rt['open']:.2f}")
        
        with col3:
            st.metric("📈 สูงสุด", f"{rt['high']:.2f}")
        
        with col4:
            st.metric("📉 ต่ำสุด", f"{rt['low']:.2f}")
        
        # ---- แถวที่ 2: Volume + Indicators ----
        col1, col2, col3, col4 = st.columns(4)
        
        avg_vol = sum(st.session_state["volumes"][-20:-1]) / 19 if len(st.session_state["volumes"]) > 20 else rt["volume"]
        vol_ratio = rt["volume"] / avg_vol if avg_vol > 0 else 1
        
        with col1:
            st.metric(
                "📦 ปริมาณ",
                f"{rt['volume']/1_000_000:.1f}M",
                delta=f"{vol_ratio:.2f}x",
                delta_color="off" if vol_ratio < 1.5 else "normal"
            )
        
        with col2:
            rsi = st.session_state["rsi"]
            rsi_color = "🟢" if rsi < 30 else "🔴" if rsi > 70 else "⚪"
            st.metric("📊 RSI (14)", f"{rsi}", delta=f"{rsi_color} { 'oversold' if rsi < 30 else 'overbought' if rsi > 70 else 'neutral'}")
        
        with col3:
            ma20 = st.session_state["ma20"]
            ma_status = "🟢 above" if rt["current"] > ma20 else "🔴 below"
            st.metric("📉 MA20", f"{ma20:.2f}", delta=ma_status)
        
        with col4:
            st.metric("📈 MA5/MA10", f"{st.session_state['ma5']:.2f} / {st.session_state['ma10']:.2f}")
        
        # ---- แถวที่ 3: Elliott Wave ----
        wave = st.session_state["wave"]
        wave_signal = st.session_state["wave_signal"]
        wave_target = st.session_state["wave_target"]
        
        wave_colors = {"buy": "green", "sell": "red", "wait": "orange", "hold": "blue", "accumulate": "green", "neutral": "gray"}
        wave_color = wave_colors.get(wave_signal, "gray")
        
        st.markdown("---")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6; border-left: 5px solid {wave_color};">
                <h4>{wave}</h4>
                <p>🎯 เป้าหมาย: {wave_target:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**สัญญาณ:**")
            if wave_signal == "buy":
                st.success("🟢 ซื้อ")
            elif wave_signal == "sell":
                st.error("🔴 ขาย")
            elif wave_signal == "accumulate":
                st.info("🟡 สะสม")
            else:
                st.info("⚪ รอดู")
        
        # ---- แถวที่ 4: กราฟ 2 คอลัมน์ ----
        st.markdown("---")
        st.subheader("📈 กราฟทางเทคนิค")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # กราฟราคา
            fig_price = go.Figure()
            
            # แท่งเทียน
            fig_price.add_trace(go.Candlestick(
                x=st.session_state["dates"][-30:],
                open=[p * (1 + np.random.uniform(-0.01, 0.01)) for p in st.session_state["prices"][-30:]],
                high=[p * (1 + np.random.uniform(0, 0.02)) for p in st.session_state["prices"][-30:]],
                low=[p * (1 - np.random.uniform(0, 0.02)) for p in st.session_state["prices"][-30:]],
                close=st.session_state["prices"][-30:],
                name="ราคา",
                showlegend=False
            ))
            
            # เส้น MA
            ma5_vals = pd.Series(st.session_state["prices"][-30:]).rolling(5).mean()
            ma20_vals = pd.Series(st.session_state["prices"][-30:]).rolling(20).mean()
            
            fig_price.add_trace(go.Scatter(
                x=st.session_state["dates"][-30:], y=ma5_vals,
                mode='lines', name='MA5',
                line=dict(color='orange', width=1.5)
            ))
            
            fig_price.add_trace(go.Scatter(
                x=st.session_state["dates"][-30:], y=ma20_vals,
                mode='lines', name='MA20',
                line=dict(color='red', width=1.5)
            ))
            
            fig_price.update_layout(
                title=f"{selected} ราคา 30 วัน",
                xaxis_title="วันที่",
                yaxis_title="ราคา",
                height=400,
                template="plotly_white",
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig_price, use_container_width=True)
        
        with col2:
            # กราฟ Volume
            fig_vol = go.Figure()
            
            colors = ['green' if v > avg_vol else 'red' for v in st.session_state["volumes"][-30:]]
            
            fig_vol.add_trace(go.Bar(
                x=st.session_state["dates"][-30:],
                y=st.session_state["volumes"][-30:],
                name='Volume',
                marker_color=colors
            ))
            
            fig_vol.add_hline(
                y=avg_vol,
                line_dash="dash",
                line_color="orange",
                annotation_text=f"เฉลี่ย {avg_vol/1_000_000:.1f}M"
            )
            
            fig_vol.update_layout(
                title="ปริมาณซื้อขาย",
                xaxis_title="วันที่",
                yaxis_title="Volume",
                height=400,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_vol, use_container_width=True)
        
        # ---- แถวที่ 5: จุดซื้อ-ขาย ----
        st.markdown("---")
        st.subheader("🎯 จุดซื้อ-ขาย แนะนำ")
        
        # คำนวณแนวรับ-แนวต้าน
        recent_prices = st.session_state["prices"][-10:]
        support = min(recent_prices) * 0.98
        resistance = max(recent_prices) * 1.02
        strong_support = min(st.session_state["prices"][-20:]) * 0.95
        strong_resistance = max(st.session_state["prices"][-20:]) * 1.05
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="padding: 15px; border-radius: 5px; background-color: #e8f5e9; border-left: 5px solid #4caf50;">
                <h4 style="color: #2e7d32;">🟢 จุดซื้อ</h4>
            """, unsafe_allow_html=True)
            
            if wave_signal == "buy" or wave_signal == "accumulate":
                buy_zone = f"{support:.2f} - {rt['current']:.2f}"
                buy_note = "ตามสัญญาณ Elliott Wave"
            elif rsi < 30:
                buy_zone = f"{strong_support:.2f} - {support:.2f}"
                buy_note = "RSI ต่ำ (oversold)"
            else:
                buy_zone = f"{support:.2f} - {rt['current']:.2f}"
                buy_note = "รออ่อนตัว"
            
            st.markdown(f"""
            - **โซนซื้อ:** {buy_zone}
            - **จุดน่าสนใจ:** {support:.2f}
            - **RSI:** {rsi}
            - **หมายเหตุ:** {buy_note}
            """)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="padding: 15px; border-radius: 5px; background-color: #ffebee; border-left: 5px solid #f44336;">
                <h4 style="color: #c62828;">🔴 จุดขาย / Cut loss</h4>
            """, unsafe_allow_html=True)
            
            tp1 = rt["current"] * 1.02
            tp2 = rt["current"] * 1.05
            sl = rt["current"] * 0.97
            
            st.markdown(f"""
            - **TP1:** {tp1:.2f} (+2%)
            - **TP2:** {tp2:.2f} (+5%)
            - **Cut loss:** {sl:.2f} (-3%)
            - **แนวต้าน:** {resistance:.2f}
            - **หมายเหตุ:** หลุด {strong_support:.2f} ให้ cut ทันที
            """)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # ---- แถวที่ 6: คำแนะนำ ----
        st.markdown("---")
        st.subheader("💡 คำแนะนำ")
        
        # วิเคราะห์รวม
        if wave_signal == "buy" or (rsi < 30 and vol_ratio > 1.5):
            action = "🟢 ซื้อ"
            reason = "Elliott Wave บอกซื้อ + RSI ต่ำ"
            color = "success"
        elif wave_signal == "sell" or (rsi > 70 and vol_ratio > 1.5):
            action = "🔴 ขาย"
            reason = "Elliott Wave บอกขาย + RSI สูง"
            color = "error"
        elif wave_signal == "accumulate":
            action = "🟡 สะสม"
            reason = "รอจังหวะอ่อนตัว"
            color = "info"
        else:
            action = "⚪ รอดู"
            reason = "ไม่มีสัญญาณชัดเจน"
            color = "info"
        
        if color == "success":
            st.success(f"**{action}** - {reason}")
        elif color == "error":
            st.error(f"**{action}** - {reason}")
        else:
            st.info(f"**{action}** - {reason}")
        
        # ---- แนวรับ-แนวต้านละเอียด ----
        with st.expander("📊 แนวรับ-แนวต้าน (ละเอียด)"):
            levels = pd.DataFrame({
                "ระดับ": ["แนวรับแข็ง", "แนวรับ", "ราคาปัจจุบัน", "แนวต้าน", "แนวต้านแข็ง"],
                "ราคา": [f"{strong_support:.2f}", f"{support:.2f}", f"{rt['current']:.2f}", 
                        f"{resistance:.2f}", f"{strong_resistance:.2f}"],
                "ระยะทาง": [f"-{(rt['current'] - strong_support)/rt['current']*100:.1f}%",
                           f"-{(rt['current'] - support)/rt['current']*100:.1f}%",
                           "0%",
                           f"+{(resistance - rt['current'])/rt['current']*100:.1f}%",
                           f"+{(strong_resistance - rt['current'])/rt['current']*100:.1f}%"]
            })
            st.dataframe(levels, use_container_width=True)
        
        # ---- ทิ้งท้ายให้กำลังใจ ----
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
            <p>💰 <strong>เทรดอย่างมีสติ ได้กำไรแล้วอย่าลืมถอนออกมากินข้าว</strong> 🍚</p>
        </div>
        """, unsafe_allow_html=True)
