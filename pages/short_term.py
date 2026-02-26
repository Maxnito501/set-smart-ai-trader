"""
📁 pages/short_term.py
หน้าเล่นสั้น - ดึงข้อมูลจาก SET SMART API จริง 100%
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests

# ============================================
# ส่วนที่ 1: เรียก API (ของจริงเท่านั้น!)
# ============================================

@st.cache_data(ttl=10)
def get_realtime_price(symbol):
    """ดึงราคาปัจจุบันจาก SET SMART API จริง"""
    try:
        api_key = st.secrets["SETSMART_API_KEY"]
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
                "change": data.get("change", 0),
                "change_pct": data.get("change_pct", 0),
                "bid": data.get("bid", 0),
                "offer": data.get("offer", 0),
                "prev_close": data.get("prev_close", 0)
            }
        else:
            return None
    except:
        return None

@st.cache_data(ttl=60)
def get_historical_prices(symbol, days=45):
    """ดึงราคาย้อนหลังจาก SET SMART API จริง"""
    try:
        api_key = st.secrets["SETSMART_API_KEY"]
        url = f"https://api.setsmart.com/historical/{symbol}"
        params = {"days": days}
        headers = {"x-api-key": api_key}
        
        response = requests.get(url, headers=headers, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            prices = data.get("prices", [])
            
            if prices and len(prices) > 0:
                dates = [datetime.strptime(p["date"], "%Y-%m-%d") for p in prices]
                closes = [p["close"] for p in prices]
                opens = [p["open"] for p in prices]
                highs = [p["high"] for p in prices]
                lows = [p["low"] for p in prices]
                volumes = [p["volume"] for p in prices]
                
                return dates, closes, opens, highs, lows, volumes
        return None, None, None, None, None, None
    except:
        return None, None, None, None, None, None

# ============================================
# ส่วนที่ 2: คำนวณตัวเลขทางเทคนิค
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
# ส่วนที่ 3: หน้าจอหลัก (ใช้ API จริงเท่านั้น)
# ============================================

def show():
    st.markdown("# ⚡ เล่นสั้น - วิเคราะห์รายตัว")
    st.markdown("---")
    
    # ============================================
    # เลือกหุ้น
    # ============================================
    col1, col2 = st.columns([3, 1])
    
    with col1:
        popular = ["PTT", "SCC", "ADVANC", "CPALL", "KCE", "GULF", "PTTEP", "BBL", "KBANK", "SCB"]
        selected = st.selectbox("🔍 เลือกหุ้น", popular, index=0)
    
    with col2:
        refresh = st.button("🔄 รีเฟรช", use_container_width=True)
    
    # ============================================
    # ดึงข้อมูลจาก API เท่านั้น!
    # ============================================
    if refresh or "last_symbol" not in st.session_state or st.session_state["last_symbol"] != selected:
        
        st.session_state["last_symbol"] = selected
        
        with st.spinner(f"⚡ กำลังดึงข้อมูล {selected} จาก API..."):
            
            # 1. ดึงราคาปัจจุบัน
            rt = get_realtime_price(selected)
            
            if rt is None:
                st.error(f"❌ ไม่สามารถดึงข้อมูล {selected} ได้")
                st.stop()
            
            # 2. ดึงข้อมูลย้อนหลัง
            dates, closes, opens, highs, lows, volumes = get_historical_prices(selected, 45)
            
            if dates is None:
                st.error(f"❌ ไม่สามารถดึงข้อมูลย้อนหลังของ {selected} ได้")
                st.stop()
            
            # 3. คำนวณค่าทางเทคนิค
            rsi = calculate_rsi(closes)
            ma5 = calculate_ma(closes, 5)
            ma10 = calculate_ma(closes, 10)
            ma20 = calculate_ma(closes, 20)
            wave, wave_signal, wave_target = elliott_wave(closes)
            
            # 4. คำนวณ Volume เฉลี่ย
            if len(volumes) > 20:
                avg_vol = sum(volumes[-21:-1]) / 20
            else:
                avg_vol = rt["volume"]
            
            vol_ratio = rt["volume"] / avg_vol if avg_vol > 0 else 1
            
            # 5. เก็บข้อมูลทั้งหมดใน session_state
            st.session_state.update({
                "rt": rt,
                "dates": dates,
                "closes": closes,
                "opens": opens,
                "highs": highs,
                "lows": lows,
                "volumes": volumes,
                "rsi": rsi,
                "ma5": ma5,
                "ma10": ma10,
                "ma20": ma20,
                "wave": wave,
                "wave_signal": wave_signal,
                "wave_target": wave_target,
                "avg_vol": avg_vol,
                "vol_ratio": vol_ratio
            })
    
    # ============================================
    # แสดงผล (ใช้ข้อมูลจาก session_state เท่านั้น)
    # ============================================
    if "rt" in st.session_state:
        rt = st.session_state["rt"]
        
        # ---------- แถวที่ 1: ราคา ----------
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            delta = f"{rt['change']:+.2f} ({rt['change_pct']:+.2f}%)"
            st.metric("💰 ราคาปัจจุบัน", f"{rt['current']:.2f}", delta)
        
        with col2:
            st.metric("📊 ราคาเปิด", f"{rt['open']:.2f}")
        
        with col3:
            st.metric("📈 สูงสุด", f"{rt['high']:.2f}")
        
        with col4:
            st.metric("📉 ต่ำสุด", f"{rt['low']:.2f}")
        
        # ---------- แถวที่ 2: Volume + RSI ----------
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📦 ปริมาณ", f"{rt['volume']/1_000_000:.2f}M", f"{st.session_state['vol_ratio']:.2f}x")
        
        with col2:
            rsi_val = st.session_state["rsi"]
            status = "oversold" if rsi_val < 30 else "overbought" if rsi_val > 70 else "neutral"
            st.metric("📊 RSI (14)", f"{rsi_val}", status)
        
        with col3:
            ma20_val = st.session_state["ma20"]
            status = "above" if rt["current"] > ma20_val else "below"
            st.metric("📉 MA20", f"{ma20_val:.2f}", status)
        
        with col4:
            st.metric("📈 Bid/Offer", f"{rt['bid']:.2f} / {rt['offer']:.2f}")
        
        # ---------- แถวที่ 3: Elliott Wave ----------
        wave = st.session_state["wave"]
        wave_signal = st.session_state["wave_signal"]
        wave_target = st.session_state["wave_target"]
        
        if wave_signal == "buy":
            st.success(f"🌊 {wave} - 🎯 เป้าหมาย {wave_target:.2f} (🟢 ซื้อ)")
        elif wave_signal == "sell":
            st.error(f"🌊 {wave} - 🎯 เป้าหมาย {wave_target:.2f} (🔴 ขาย)")
        elif wave_signal == "accumulate":
            st.info(f"🌊 {wave} - 🎯 เป้าหมาย {wave_target:.2f} (🟡 สะสม)")
        else:
            st.info(f"🌊 {wave} - 🎯 เป้าหมาย {wave_target:.2f} (⚪ รอดู)")
        
        # ---------- แถวที่ 4: กราฟแท่งเทียน ----------
        st.markdown("---")
        st.subheader("📈 กราฟแท่งเทียน (ข้อมูลจาก API)")
        
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=st.session_state["dates"][-30:],
            open=st.session_state["opens"][-30:],
            high=st.session_state["highs"][-30:],
            low=st.session_state["lows"][-30:],
            close=st.session_state["closes"][-30:],
            name="ราคา"
        ))
        
        # MA5
        ma5_vals = pd.Series(st.session_state["closes"][-30:]).rolling(5).mean()
        fig.add_trace(go.Scatter(
            x=st.session_state["dates"][-30:], y=ma5_vals,
            mode='lines', name='MA5',
            line=dict(color='orange', width=1.5)
        ))
        
        # MA20
        ma20_vals = pd.Series(st.session_state["closes"][-30:]).rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=st.session_state["dates"][-30:], y=ma20_vals,
            mode='lines', name='MA20',
            line=dict(color='red', width=1.5)
        ))
        
        fig.update_layout(
            height=500,
            xaxis_rangeslider_visible=False,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ---------- แถวที่ 5: กราฟ Volume ----------
        st.subheader("📊 ปริมาณซื้อขาย (ข้อมูลจาก API)")
        
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
            height=300,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_vol, use_container_width=True)
        
        # ---------- แถวที่ 6: จุดซื้อ-ขาย ----------
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
            st.markdown("### 🟢 จุดซื้อ")
            st.markdown(f"**โซนซื้อ:** {support:.2f} - {rt['current']:.2f}")
            st.markdown(f"**จุดช้อน:** {support:.2f}")
            st.markdown(f"**RSI:** {st.session_state['rsi']}")
        
        with col2:
            st.markdown("### 🔴 จุดขาย / Cut loss")
            st.markdown(f"**TP1:** {rt['current']*1.02:.2f} (+2%)")
            st.markdown(f"**TP2:** {rt['current']*1.05:.2f} (+5%)")
            st.markdown(f"**Cut loss:** {rt['current']*0.97:.2f} (-3%)")
            st.markdown(f"**แนวต้าน:** {resistance:.2f}")
        
        # ---------- แนวรับ-แนวต้านละเอียด ----------
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
        
        # ---------- เวลาอัปเดท ----------
        st.caption(f"⏱️ ข้อมูลล่าสุด: {datetime.now().strftime('%H:%M:%S')}")
