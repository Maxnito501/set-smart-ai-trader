"""
📁 pages/short_term.py
หน้าเล่นสั้น - ดึงข้อมูลจาก SET SMART API จริง
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import time

# ============================================
# 🔴 ฟังก์ชันเรียก SET SMART API (ของจริง)
# ============================================

@st.cache_data(ttl=10)  # cache แค่ 10 วินาที ให้ข้อมูลสด
def get_realtime_price(symbol):
    """
    ดึงราคาปัจจุบันจาก SET SMART API จริง
    """
    try:
        # ดึง API Key จาก secrets
        api_key = st.secrets["SETSMART_API_KEY"]
        
        # 🔴 เปลี่ยน endpoint ตามที่ SET SMART ให้มาจริง
        url = f"https://api.setsmart.com/realtime/{symbol}"
        headers = {"x-api-key": api_key}
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "current": data.get("last", 0),
                "open": data.get("open", 0),
                "high": data.get("high", 0),
                "low": data.get("low", 0),
                "volume": data.get("volume", 0),
                "value": data.get("value", 0),
                "change": data.get("change", 0),
                "change_pct": data.get("change_pct", 0),
                "bid": data.get("bid", 0),
                "offer": data.get("offer", 0),
                "prev_close": data.get("prev_close", 0),
                "timestamp": datetime.now().isoformat()
            }
        else:
            st.error(f"❌ API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"❌ ไม่สามารถเชื่อมต่อ API: {e}")
        return None

@st.cache_data(ttl=60)  # cache 1 นาที
def get_historical_prices(symbol, days=45):
    """
    ดึงราคาย้อนหลังจาก SET SMART API จริง
    """
    try:
        api_key = st.secrets["SETSMART_API_KEY"]
        url = f"https://api.setsmart.com/historical/{symbol}"
        params = {"days": days}
        headers = {"x-api-key": api_key}
        
        response = requests.get(url, headers=headers, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            prices_data = data.get("prices", [])
            
            if prices_data:
                dates = [datetime.strptime(p["date"], "%Y-%m-%d") for p in prices_data]
                closes = [p["close"] for p in prices_data]
                opens = [p["open"] for p in prices_data]
                highs = [p["high"] for p in prices_data]
                lows = [p["low"] for p in prices_data]
                volumes = [p["volume"] for p in prices_data]
                
                return dates, closes, opens, highs, lows, volumes
        return None, None, None, None, None, None
    except Exception as e:
        st.error(f"❌ ไม่สามารถดึงข้อมูลย้อนหลัง: {e}")
        return None, None, None, None, None, None

@st.cache_data(ttl=300)  # cache 5 นาที
def get_securities_list():
    """
    ดึงรายชื่อหุ้นทั้งหมดจาก SET SMART API
    """
    try:
        api_key = st.secrets["SETSMART_API_KEY"]
        url = "https://api.setsmart.com/securities"
        headers = {"x-api-key": api_key}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # สมมติว่า API คืนค่า list ของ dict ที่มี key "symbol"
            stocks = [s["symbol"] for s in data if "symbol" in s]
            return sorted(stocks)
        else:
            # ถ้าไม่ได้ ให้ใช้ list สำรอง
            return ["SCC", "PTT", "ADVANC", "CPALL", "KCE", "GULF", "IVL", 
                    "BBL", "KBANK", "SCB", "KTB", "TISCO", "MINT", "AOT",
                    "BH", "BDMS", "CPF", "PTTEP", "EA"]
    except Exception as e:
        st.warning(f"ใช้รายชื่อหุ้นสำรอง: {e}")
        return ["SCC", "PTT", "ADVANC", "CPALL", "KCE", "GULF", "IVL", 
                "BBL", "KBANK", "SCB", "KTB", "TISCO", "MINT", "AOT",
                "BH", "BDMS", "CPF", "PTTEP", "EA"]

# ============================================
# 🔴 ฟังก์ชันคำนวณทางเทคนิค (เหมือนเดิม)
# ============================================

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
# 🔴 หน้าเล่นสั้น
# ============================================
def show():
    st.title("⚡ เล่นสั้น - หาตังค์กินข้าว")
    st.caption(f"💰 ข้อมูลจาก SET SMART API (เสียเงินปีละ 2,400 บาท ต้องใช้ให้คุ้ม!)")
    
    # ============================================
    # ดึงรายชื่อหุ้นจาก API
    # ============================================
    if "stock_list" not in st.session_state:
        with st.spinner("กำลังโหลดรายชื่อหุ้น..."):
            stocks = get_securities_list()
            st.session_state["stock_list"] = stocks
    
    # ============================================
    # เลือกหุ้น
    # ============================================
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected = st.selectbox("🔍 เลือกหุ้น", st.session_state["stock_list"], index=0)
    
    with col2:
        custom = st.text_input("หรือพิมพ์ชื่อ", "").upper()
        if custom and custom not in st.session_state["stock_list"]:
            selected = custom
    
    with col3:
        refresh = st.button("🔄 รีเฟรช", use_container_width=True)
    
    # ============================================
    # ดึงข้อมูลจริงจาก API
    # ============================================
    if refresh or "last_symbol" not in st.session_state or st.session_state["last_symbol"] != selected:
        
        st.session_state["last_symbol"] = selected
        
        with st.spinner(f"⚡ กำลังดึงข้อมูล {selected} จาก SET SMART..."):
            
            # 1. ดึงราคาปัจจุบัน
            rt = get_realtime_price(selected)
            
            if not rt:
                st.error(f"❌ ไม่สามารถดึงข้อมูล {selected} ได้")
                st.stop()
            
            # 2. ดึงข้อมูลย้อนหลัง
            dates, closes, opens, highs, lows, volumes = get_historical_prices(selected, 45)
            
            if not dates:
                st.error(f"❌ ไม่สามารถดึงข้อมูลย้อนหลังของ {selected} ได้")
                st.stop()
            
            # 3. คำนวณ Indicators
            rsi = calculate_rsi(closes)
            ma5 = calculate_ma(closes, 5)
            ma10 = calculate_ma(closes, 10)
            ma20 = calculate_ma(closes, 20)
            
            # 4. Elliott Wave
            wave, wave_signal, wave_target = elliott_wave(closes)
            
            # 5. Volume ratio
            avg_vol = sum(volumes[-21:-1]) / 20 if len(volumes) > 20 else rt["volume"]
            vol_ratio = rt["volume"] / avg_vol if avg_vol > 0 else 1
            
            # เก็บใน session
            st.session_state["rt"] = rt
            st.session_state["dates"] = dates
            st.session_state["closes"] = closes
            st.session_state["opens"] = opens
            st.session_state["highs"] = highs
            st.session_state["lows"] = lows
            st.session_state["volumes"] = volumes
            st.session_state["rsi"] = rsi
            st.session_state["ma5"] = ma5
            st.session_state["ma10"] = ma10
            st.session_state["ma20"] = ma20
            st.session_state["wave"] = wave
            st.session_state["wave_signal"] = wave_signal
            st.session_state["wave_target"] = wave_target
            st.session_state["vol_ratio"] = vol_ratio
            st.session_state["avg_vol"] = avg_vol
    
    # ============================================
    # แสดงผล
    # ============================================
    if "rt" in st.session_state:
        rt = st.session_state["rt"]
        
        # ---- แถวที่ 1: ราคา (ของจริง) ----
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
        
        # ---- แถวที่ 2: Volume + Indicators (ของจริง) ----
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📦 ปริมาณ",
                f"{rt['volume']/1_000_000:.2f}M",
                delta=f"{st.session_state['vol_ratio']:.2f}x"
            )
        
        with col2:
            rsi = st.session_state["rsi"]
            rsi_color = "🟢" if rsi < 30 else "🔴" if rsi > 70 else "⚪"
            st.metric("📊 RSI (14)", f"{rsi}", delta=rsi_color)
        
        with col3:
            ma20 = st.session_state["ma20"]
            ma_status = "🟢 above" if rt["current"] > ma20 else "🔴 below"
            st.metric("📉 MA20", f"{ma20:.2f}", delta=ma_status)
        
        with col4:
            st.metric("📈 Bid/Offer", f"{rt['bid']:.2f} / {rt['offer']:.2f}")
        
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
        
        # ---- แถวที่ 4: กราฟ (ของจริง) ----
        st.markdown("---")
        st.subheader("📈 กราฟทางเทคนิค (ข้อมูลจริงจาก SET SMART)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # กราฟแท่งเทียน
            fig_price = go.Figure()
            
            fig_price.add_trace(go.Candlestick(
                x=st.session_state["dates"][-30:],
                open=st.session_state["opens"][-30:],
                high=st.session_state["highs"][-30:],
                low=st.session_state["lows"][-30:],
                close=st.session_state["closes"][-30:],
                name="ราคา",
                showlegend=False
            ))
            
            # เส้น MA
            ma5_vals = pd.Series(st.session_state["closes"][-30:]).rolling(5).mean()
            ma20_vals = pd.Series(st.session_state["closes"][-30:]).rolling(20).mean()
            
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
            
            colors = ['green' if v > st.session_state["avg_vol"] else 'red' for v in st.session_state["volumes"][-30:]]
            
            fig_vol.add_trace(go.Bar(
                x=st.session_state["dates"][-30:],
                y=st.session_state["volumes"][-30:],
                name='Volume',
                marker_color=colors
            ))
            
            fig_vol.add_hline(
                y=st.session_state["avg_vol"],
                line_dash="dash",
                line_color="orange",
                annotation_text=f"เฉลี่ย {st.session_state['avg_vol']/1_000_000:.1f}M"
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
        
        # คำนวณแนวรับ-แนวต้านจากข้อมูลจริง
        recent_prices = st.session_state["closes"][-10:]
        support = min(recent_prices) * 0.98
        resistance = max(recent_prices) * 1.02
        strong_support = min(st.session_state["closes"][-20:]) * 0.95
        strong_resistance = max(st.session_state["closes"][-20:]) * 1.05
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="padding: 15px; border-radius: 5px; background-color: #e8f5e9; border-left: 5px solid #4caf50;">
                <h4 style="color: #2e7d32;">🟢 จุดซื้อ</h4>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            - **โซนซื้อ:** {support:.2f} - {rt['current']:.2f}
            - **จุดน่าสนใจ:** {support:.2f}
            - **RSI:** {st.session_state['rsi']}
            - **Volume Ratio:** {st.session_state['vol_ratio']:.2f}x
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
            """)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # ---- แถวที่ 6: คำแนะนำ ----
        st.markdown("---")
        st.subheader("💡 คำแนะนำ")
        
        # วิเคราะห์รวม
        if wave_signal == "buy" or (st.session_state['rsi'] < 30 and st.session_state['vol_ratio'] > 1.5):
            action = "🟢 ซื้อ"
            reason = f"Elliott Wave: {wave} | RSI: {st.session_state['rsi']} | Volume: {st.session_state['vol_ratio']:.2f}x"
            st.success(f"**{action}** - {reason}")
        elif wave_signal == "sell" or (st.session_state['rsi'] > 70 and st.session_state['vol_ratio'] > 1.5):
            action = "🔴 ขาย"
            reason = f"Elliott Wave: {wave} | RSI: {st.session_state['rsi']} | Volume: {st.session_state['vol_ratio']:.2f}x"
            st.error(f"**{action}** - {reason}")
        elif wave_signal == "accumulate":
            action = "🟡 สะสม"
            reason = f"Elliott Wave: {wave} | รอซื้อที่ {support:.2f}"
            st.info(f"**{action}** - {reason}")
        else:
            action = "⚪ รอดู"
            reason = f"Elliott Wave: {wave} | RSI: {st.session_state['rsi']}"
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
        
        # ---- เวลาอัปเดท ----
        st.caption(f"⏱️ ข้อมูลล่าสุด: {datetime.now().strftime('%H:%M:%S')}")
        
        # ---- ทิ้งท้าย ----
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
            <p>💰 <strong>ข้อมูลจาก SET SMART API คุ้มค่ากับ 2,400 บาทแน่นอน</strong> 🍚</p>
        </div>
        """, unsafe_allow_html=True)
