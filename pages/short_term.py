"""
📁 pages/short_term.py
หน้าเล่นสั้น - ใช้ API จริงจาก SET SMART
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests

# ============================================
# ส่วนที่ 1: เรียก API (ของจริงจากเอกสาร)
# ============================================

@st.cache_data(ttl=60)
def get_eod_price(symbol, date=None):
    """ดึงราคาปิดรายวัน"""
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
                return data[0]
        return None
    except:
        return None

@st.cache_data(ttl=300)
def get_historical_eod(symbol, days=45):
    """ดึงราคาย้อนหลัง"""
    try:
        api_key = st.secrets["SETSMART_API_KEY"]
        url = "https://www.setsmart.com/api/listed-company-api/eod-price-by-symbol"
        
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
                data.sort(key=lambda x: x.get("date", ""))
                return data
        return []
    except:
        return []

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
# ส่วนที่ 3: หน้าจอหลัก
# ============================================

def show():
    st.markdown("# ⚡ เล่นสั้น - วิเคราะห์รายตัว")
    st.markdown("---")
    
    # เลือกหุ้น
    col1, col2 = st.columns([3, 1])
    
    with col1:
        popular = ["SCC", "PTT", "ADVANC", "CPALL", "KCE", "GULF", "PTTEP", "BBL", "KBANK", "SCB"]
        selected = st.selectbox("🔍 เลือกหุ้น", popular, index=0)
    
    with col2:
        refresh = st.button("🔄 รีเฟรช", use_container_width=True)
    
    # ดึงข้อมูล
    if refresh or "last_symbol" not in st.session_state or st.session_state["last_symbol"] != selected:
        
        st.session_state["last_symbol"] = selected
        
        with st.spinner(f"⚡ กำลังดึงข้อมูล {selected}..."):
            
            # 1. ดึง EOD ล่าสุด (ใช้เป็นราคาปัจจุบัน)
            eod = get_eod_price(selected)
            
            if eod is None:
                st.warning(f"⚠️ ไม่พบข้อมูล {selected} ใช้ข้อมูลตัวอย่าง")
                # ใช้ข้อมูลตัวอย่าง
                current_price = 100.0
                volume = 5_000_000
                change = 0.5
                change_pct = 0.5
                open_price = 99.5
                high = 101.0
                low = 99.0
            else:
                current_price = eod.get("close", 0)
                volume = eod.get("volume", 0)
                prev_close = eod.get("prevClose", current_price)
                change = current_price - prev_close
                change_pct = (change / prev_close * 100) if prev_close > 0 else 0
                open_price = eod.get("open", current_price)
                high = eod.get("high", current_price)
                low = eod.get("low", current_price)
            
            # 2. ดึงข้อมูลย้อนหลัง
            hist_data = get_historical_eod(selected, 45)
            
            if hist_data and len(hist_data) > 0:
                dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in hist_data]
                closes = [d["close"] for d in hist_data]
                opens = [d["open"] for d in hist_data]
                highs = [d["high"] for d in hist_data]
                lows = [d["low"] for d in hist_data]
                volumes = [d["volume"] for d in hist_data]
            else:
                # ข้อมูลตัวอย่าง
                dates = pd.date_range(end=datetime.now(), periods=45).tolist()
                base = current_price
                closes = [base * (1 + np.random.uniform(-0.05, 0.05)) for _ in range(45)]
                opens = [c * (1 + np.random.uniform(-0.01, 0.01)) for c in closes]
                highs = [max(o, c) * (1 + np.random.uniform(0, 0.02)) for o, c in zip(opens, closes)]
                lows = [min(o, c) * (1 - np.random.uniform(0, 0.02)) for o, c in zip(opens, closes)]
                volumes = [int(np.random.uniform(1, 10) * 1_000_000) for _ in range(45)]
            
            # 3. คำนวณค่าต่างๆ
            rsi = calculate_rsi(closes)
            ma5 = calculate_ma(closes, 5)
            ma10 = calculate_ma(closes, 10)
            ma20 = calculate_ma(closes, 20)
            wave, wave_signal, wave_target = elliott_wave(closes)
            
            # 4. Volume เฉลี่ย
            if len(volumes) > 20:
                avg_vol = sum(volumes[-21:-1]) / 20
            else:
                avg_vol = volume
            vol_ratio = volume / avg_vol if avg_vol > 0 else 1
            
            # 5. เก็บใน session
            st.session_state.update({
                "current_price": current_price,
                "volume": volume,
                "change": change,
                "change_pct": change_pct,
                "open": open_price,
                "high": high,
                "low": low,
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
    # แสดงผล
    # ============================================
    if "current_price" in st.session_state:
        
        # แถวที่ 1: ราคา
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            delta = f"{st.session_state['change']:+.2f} ({st.session_state['change_pct']:+.2f}%)"
            st.metric("💰 ราคาปัจจุบัน", f"{st.session_state['current_price']:.2f}", delta)
        with col2:
            st.metric("📊 ราคาเปิด", f"{st.session_state['open']:.2f}")
        with col3:
            st.metric("📈 สูงสุด", f"{st.session_state['high']:.2f}")
        with col4:
            st.metric("📉 ต่ำสุด", f"{st.session_state['low']:.2f}")
        
        # แถวที่ 2: Volume + RSI
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 ปริมาณ", f"{st.session_state['volume']/1_000_000:.2f}M", 
                     f"{st.session_state['vol_ratio']:.2f}x")
        with col2:
            rsi_val = st.session_state['rsi']
            status = "oversold" if rsi_val < 30 else "overbought" if rsi_val > 70 else "neutral"
            st.metric("📊 RSI (14)", f"{rsi_val}", status)
        with col3:
            ma20_val = st.session_state['ma20']
            status = "above" if st.session_state['current_price'] > ma20_val else "below"
            st.metric("📉 MA20", f"{ma20_val:.2f}", status)
        with col4:
            st.metric("📈 MA5/MA10", f"{st.session_state['ma5']:.2f} / {st.session_state['ma10']:.2f}")
        
        # แถวที่ 3: Elliott Wave
        wave = st.session_state['wave']
        wave_signal = st.session_state['wave_signal']
        wave_target = st.session_state['wave_target']
        
        if wave_signal == "buy":
            st.success(f"🌊 {wave} - 🎯 เป้าหมาย {wave_target:.2f} (🟢 ซื้อ)")
        elif wave_signal == "sell":
            st.error(f"🌊 {wave} - 🎯 เป้าหมาย {wave_target:.2f} (🔴 ขาย)")
        elif wave_signal == "accumulate":
            st.info(f"🌊 {wave} - 🎯 เป้าหมาย {wave_target:.2f} (🟡 สะสม)")
        else:
            st.info(f"🌊 {wave} - 🎯 เป้าหมาย {wave_target:.2f} (⚪ รอดู)")
        
        # แถวที่ 4: กราฟแท่งเทียน
        st.markdown("---")
        st.subheader("📈 กราฟแท่งเทียน")
        
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=st.session_state['dates'][-30:],
            open=st.session_state['opens'][-30:],
            high=st.session_state['highs'][-30:],
            low=st.session_state['lows'][-30:],
            close=st.session_state['closes'][-30:],
            name="ราคา"
        ))
        
        ma5_vals = pd.Series(st.session_state['closes'][-30:]).rolling(5).mean()
        ma20_vals = pd.Series(st.session_state['closes'][-30:]).rolling(20).mean()
        
        fig.add_trace(go.Scatter(
            x=st.session_state['dates'][-30:], y=ma5_vals,
            mode='lines', name='MA5',
            line=dict(color='orange', width=1.5)
        ))
        
        fig.add_trace(go.Scatter(
            x=st.session_state['dates'][-30:], y=ma20_vals,
            mode='lines', name='MA20',
            line=dict(color='red', width=1.5)
        ))
        
        fig.update_layout(
            height=500,
            xaxis_rangeslider_visible=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # แถวที่ 5: กราฟ Volume
        st.subheader("📊 ปริมาณซื้อขาย")
        
        fig_vol = go.Figure()
        colors = ['green' if v > st.session_state['avg_vol'] else 'red' 
                  for v in st.session_state['volumes'][-30:]]
        
        fig_vol.add_trace(go.Bar(
            x=st.session_state['dates'][-30:],
            y=st.session_state['volumes'][-30:],
            name='Volume',
            marker_color=colors
        ))
        
        fig_vol.add_hline(
            y=st.session_state['avg_vol'],
            line_dash="dash",
            line_color="orange",
            annotation_text=f"เฉลี่ย {st.session_state['avg_vol']/1_000_000:.1f}M"
        )
        
        fig_vol.update_layout(height=300, template="plotly_white")
        st.plotly_chart(fig_vol, use_container_width=True)
        
        # แถวที่ 6: จุดซื้อ-ขาย
        st.markdown("---")
        st.subheader("🎯 จุดซื้อ-ขาย แนะนำ")
        
        recent_prices = st.session_state['closes'][-10:]
        support = min(recent_prices) * 0.98
        resistance = max(recent_prices) * 1.02
        strong_support = min(st.session_state['closes'][-20:]) * 0.95
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🟢 จุดซื้อ")
            st.markdown(f"**โซนซื้อ:** {support:.2f} - {st.session_state['current_price']:.2f}")
            st.markdown(f"**จุดช้อน:** {support:.2f}")
            st.markdown(f"**RSI:** {st.session_state['rsi']}")
        with col2:
            st.markdown("### 🔴 จุดขาย / Cut loss")
            st.markdown(f"**TP1:** {st.session_state['current_price']*1.02:.2f} (+2%)")
            st.markdown(f"**TP2:** {st.session_state['current_price']*1.05:.2f} (+5%)")
            st.markdown(f"**Cut loss:** {st.session_state['current_price']*0.97:.2f} (-3%)")
            st.markdown(f"**แนวต้าน:** {resistance:.2f}")
        
        # เวลาอัปเดท
        st.caption(f"⏱️ ข้อมูลล่าสุด: {datetime.now().strftime('%H:%M:%S')}")
