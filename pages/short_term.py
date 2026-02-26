"""
📁 pages/short_term.py
เล่นสั้น - ใช้ SETSMART API (ของจริง) + ตัวชี้วัดครบ
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests

# ============================================
# ส่วนที่ 1: ดึงข้อมูลจาก SETSMART API
# ============================================

@st.cache_data(ttl=3600)  # cache 1 ชั่วโมง
def get_historical_data(symbol, days=90):
    """ดึงข้อมูลย้อนหลังจาก SETSMART API"""
    try:
        api_key = st.secrets["SETSMART_API_KEY"]
        url = "https://www.setsmart.com/api/listed-company-api/eod-price-by-symbol"
        
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        params = {
            "symbol": symbol,
            "startDate": start_date,
            "adjustedPriceFlag": "Y"
        }
        headers = {"x-api-key": api_key}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                # แปลงเป็น DataFrame
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                return df
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# ============================================
# ส่วนที่ 2: ฟังก์ชันคำนวณตัวชี้วัด
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
    """Moving Average"""
    if len(prices) < period:
        return prices[-1]
    return round(sum(prices[-period:]) / period, 2)

def calculate_macd(prices):
    """MACD"""
    if len(prices) < 26:
        return 0, 0, 0
    
    prices_series = pd.Series(prices)
    ema12 = prices_series.ewm(span=12).mean().iloc[-1]
    ema26 = prices_series.ewm(span=26).mean().iloc[-1]
    macd = ema12 - ema26
    signal = prices_series.ewm(span=9).mean().iloc[-1]
    histogram = macd - signal
    
    return round(macd, 2), round(signal, 2), round(histogram, 2)

def calculate_stochastic(prices, highs, lows, period=14):
    """Stochastic"""
    if len(prices) < period:
        return 50, 50
    
    recent_high = max(highs[-period:])
    recent_low = min(lows[-period:])
    current = prices[-1]
    
    if recent_high - recent_low == 0:
        return 50, 50
    
    k = ((current - recent_low) / (recent_high - recent_low)) * 100
    d = k  # simplified
    
    return round(k, 2), round(d, 2)

def calculate_volume_ratio(volumes, period=20):
    """Volume Ratio"""
    if len(volumes) < period + 1:
        return 1
    current = volumes[-1]
    avg = sum(volumes[-period-1:-1]) / period
    return round(current / avg, 2) if avg > 0 else 1

def elliott_wave(prices, volumes):
    """Elliott Wave เบื้องต้น"""
    if len(prices) < 30:
        return "ข้อมูลไม่พอ", "neutral", 0, 0
    
    current = prices[-1]
    recent_high = max(prices[-10:])
    recent_low = min(prices[-10:])
    vol_ratio = volumes[-1] / (sum(volumes[-6:-1])/5) if len(volumes) > 5 else 1
    
    if current > recent_high * 0.98:
        if vol_ratio > 1.3:
            return "🌊 คลื่น 3 (กำลังขึ้น)", "buy", recent_high * 1.05, recent_low
        else:
            return "🌊 คลื่น 5 (ใกล้จบ)", "sell", current, recent_low
    elif current < recent_low * 1.02:
        if vol_ratio > 1.3:
            return "🌊 คลื่น C (จบรอบ)", "accumulate", recent_low, recent_low * 0.95
        else:
            return "🌊 คลื่น 2 (ย่อตัว)", "wait", recent_high, recent_low
    else:
        return "🌊 คลื่น 4 (พักตัว)", "hold", recent_high, recent_low

def calculate_support_resistance(prices):
    """แนวรับ-แนวต้าน"""
    recent = prices[-10:]
    support = min(recent) * 0.98
    resistance = max(recent) * 1.02
    strong_support = min(prices[-20:]) * 0.95
    strong_resistance = max(prices[-20:]) * 1.05
    return support, resistance, strong_support, strong_resistance

# ============================================
# ส่วนที่ 3: Market Depth จำลอง (รอ API จริง)
# ============================================

def get_market_depth(current_price):
    """จำลอง Market Depth 10 ชั้น"""
    import random
    
    bids = []
    offers = []
    
    for i in range(10):
        bid_price = round(current_price * (1 - 0.002 * i), 2)
        bid_vol = random.randint(50, 150) * 1000
        bids.append({"price": bid_price, "volume": bid_vol})
        
        offer_price = round(current_price * (1 + 0.002 * i), 2)
        offer_vol = random.randint(50, 150) * 1000
        offers.append({"price": offer_price, "volume": offer_vol})
    
    # แทรกวาฬ
    if random.random() > 0.5:
        bids[2]["volume"] = random.randint(300, 500) * 1000
    if random.random() > 0.5:
        offers[2]["volume"] = random.randint(300, 500) * 1000
    
    return bids, offers

# ============================================
# ส่วนที่ 4: หน้าจอหลัก
# ============================================

def show():
    st.markdown("# ⚡ เล่นสั้น - SETSMART API")
    st.markdown("### RSI | MACD | Stochastic | Elliott | Volume | Depth")
    st.markdown("---")
    
    # เลือกหุ้น
    symbol = st.selectbox("🔍 เลือกหุ้น", ["SCC", "PTT", "ADVANC", "CPALL", "KCE"])
    
    if st.button("🔮 วิเคราะห์", type="primary"):
        with st.spinner("กำลังดึงข้อมูลจาก SETSMART..."):
            
            # ดึงข้อมูล
            df = get_historical_data(symbol, 90)
            
            if df is None or len(df) < 30:
                st.error("ไม่สามารถดึงข้อมูลได้")
                return
            
            # ดึงค่าล่าสุด
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # คำนวณตัวชี้วัด
            closes = df['close'].tolist()
            highs = df['high'].tolist()
            lows = df['low'].tolist()
            volumes = df['volume'].tolist()
            
            rsi = calculate_rsi(closes)
            ma5 = calculate_ma(closes, 5)
            ma20 = calculate_ma(closes, 20)
            ma50 = calculate_ma(closes, 50)
            macd, signal, hist = calculate_macd(closes)
            stoch_k, stoch_d = calculate_stochastic(closes, highs, lows)
            vol_ratio = calculate_volume_ratio(volumes)
            wave, wave_signal, target, support = elliott_wave(closes, volumes)
            sup, res, strong_sup, strong_res = calculate_support_resistance(closes)
            bids, offers = get_market_depth(latest['close'])
            
            # ===== แถวที่ 1: ราคา =====
            change = latest['close'] - prev['close']
            change_pct = (change / prev['close']) * 100
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 ราคา", f"{latest['close']:.2f}", 
                       f"{change:+.2f} ({change_pct:+.2f}%)")
            col2.metric("📊 เปิด", f"{latest['open']:.2f}")
            col3.metric("📈 สูง", f"{latest['high']:.2f}")
            col4.metric("📉 ต่ำ", f"{latest['low']:.2f}")
            
            # ===== แถวที่ 2: RSI + MA =====
            col1, col2, col3, col4 = st.columns(4)
            rsi_status = "🟢 ซื้อ" if rsi < 30 else "🔴 ขาย" if rsi > 70 else "⚪ กลาง"
            col1.metric("📊 RSI (14)", rsi, rsi_status)
            col2.metric("📉 MA20", ma20)
            col3.metric("📈 MA50", ma50)
            vol_status = "🔥 สูง" if vol_ratio > 1.5 else "😴 ต่ำ" if vol_ratio < 0.5 else "⚖️ ปกติ"
            col4.metric("📦 Volume", f"{latest['volume']/1e6:.1f}M", f"{vol_ratio}x")
            
            # ===== แถวที่ 3: MACD =====
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📊 MACD", macd)
            col2.metric("📈 Signal", signal)
            col3.metric("📉 Histogram", hist)
            macd_signal = "🟢 ซื้อ" if macd > signal else "🔴 ขาย"
            col4.metric("🎯 MACD สัญญาณ", macd_signal)
            
            # ===== แถวที่ 4: Stochastic =====
            st.markdown("---")
            st.subheader("📊 เส้นแกว่งตัว (Stochastic)")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("🔵 เส้นเร็ว (%K)", stoch_k)
            col2.metric("🟠 เส้นช้า (%D)", stoch_d)
            
            if stoch_k < 20 and stoch_d < 20:
                col3.success("🟢 ซื้อ (oversold)")
            elif stoch_k > 80 and stoch_d > 80:
                col3.error("🔴 ขาย (overbought)")
            else:
                col3.info("⚪ รอดู")
            
            # ===== แถวที่ 5: Elliott Wave =====
            st.markdown("---")
            st.subheader("🌊 Elliott Wave")
            
            col1, col2 = st.columns(2)
            col1.markdown(f"**{wave}**")
            if wave_signal == "buy":
                col1.success(f"🟢 {wave_signal}")
            elif wave_signal == "sell":
                col1.error(f"🔴 {wave_signal}")
            else:
                col1.info(f"⚪ {wave_signal}")
            
            col2.markdown(f"🎯 เป้าหมาย: {target:.2f}")
            col2.markdown(f"🛡️ แนวรับ: {support:.2f}")
            
            # ===== แถวที่ 6: Market Depth =====
            st.markdown("---")
            st.subheader("🐋 Market Depth 10 ชั้น")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🟢 Bids")
                for b in bids[:7]:
                    st.write(f"{b['price']} : {b['volume']/1000:.0f}K")
            
            with col2:
                st.markdown("### 🔴 Offers")
                for o in offers[:7]:
                    st.write(f"{o['price']} : {o['volume']/1000:.0f}K")
            
            # ===== แถวที่ 7: จุดซื้อ-ขาย =====
            st.markdown("---")
            st.subheader("🎯 จุดซื้อ-ขาย")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🟢 จุดซื้อ")
                st.write(f"โซน: {sup:.2f} - {latest['close']:.2f}")
                st.write(f"จุดช้อน: {sup:.2f}")
                st.write(f"แนวรับแข็ง: {strong_sup:.2f}")
            
            with col2:
                st.markdown("### 🔴 จุดขาย")
                st.write(f"TP1: {latest['close']*1.02:.2f} (+2%)")
                st.write(f"TP2: {latest['close']*1.05:.2f} (+5%)")
                st.write(f"Cut loss: {latest['close']*0.97:.2f} (-3%)")
                st.write(f"แนวต้าน: {res:.2f}")
            
            # ===== แถวที่ 8: กราฟ =====
            st.markdown("---")
            st.subheader("📈 กราฟราคา 60 วัน")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'].tail(60),
                y=df['close'].tail(60),
                mode='lines',
                name='ราคา',
                line=dict(color='blue', width=2)
            ))
            
            # เพิ่ม MA20
            ma20_vals = df['close'].rolling(20).mean().tail(60)
            fig.add_trace(go.Scatter(
                x=df['date'].tail(60),
                y=ma20_vals,
                mode='lines',
                name='MA20',
                line=dict(color='orange', width=1, dash='dash')
            ))
            
            fig.update_layout(
                height=400,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # ===== แถวที่ 9: กราฟ Volume =====
            st.subheader("📊 ปริมาณซื้อขาย")
            
            fig_vol = go.Figure()
            colors = ['green' if v > sum(volumes[-21:-1])/20 else 'red' 
                     for v in volumes[-60:]]
            
            fig_vol.add_trace(go.Bar(
                x=df['date'].tail(60),
                y=df['volume'].tail(60),
                marker_color=colors
            ))
            
            fig_vol.add_hline(
                y=sum(volumes[-21:-1])/20,
                line_dash="dash",
                line_color="orange"
            )
            
            fig_vol.update_layout(height=200, template="plotly_white")
            st.plotly_chart(fig_vol, use_container_width=True)
            
            # ===== สรุปคะแนน =====
            st.markdown("---")
            st.subheader("💡 สรุปสัญญาณ")
            
            buy_signals = 0
            sell_signals = 0
            
            if rsi < 30: buy_signals += 2
            if rsi > 70: sell_signals += 2
            if vol_ratio > 1.5 and change > 0: buy_signals += 1
            if vol_ratio > 1.5 and change < 0: sell_signals += 1
            if macd > signal: buy_signals += 1
            if macd < signal: sell_signals += 1
            if stoch_k < 20: buy_signals += 1
            if stoch_k > 80: sell_signals += 1
            if wave_signal == "buy": buy_signals += 2
            if wave_signal == "sell": sell_signals += 2
            if wave_signal == "accumulate": buy_signals += 1
            
            col1, col2 = st.columns(2)
            col1.metric("🟢 สัญญาณซื้อ", buy_signals)
            col2.metric("🔴 สัญญาณขาย", sell_signals)
            
            if buy_signals > sell_signals + 1:
                st.success("✅ แนะนำ: ซื้อ")
            elif sell_signals > buy_signals + 1:
                st.error("❌ แนะนำ: ขาย")
            else:
                st.info("⚖️ แนะนำ: รอดู")
            
            st.caption(f"⏱️ ข้อมูลล่าสุด: {datetime.now().strftime('%H:%M:%S')}")
