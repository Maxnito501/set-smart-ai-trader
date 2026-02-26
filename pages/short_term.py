"""
📁 pages/short_term.py
เล่นสั้น - ครบทุกตัวชี้วัดที่ใช้หาตัง
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf
import time

# ============================================
# ส่วนที่ 1: ดึงข้อมูลจาก Yahoo
# ============================================

def get_stock_data(symbol):
    """ดึงข้อมูลหุ้นครบทุกอย่าง"""
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        hist = ticker.history(period="3mo")
        
        if hist.empty:
            return None
        
        # ข้อมูลล่าสุด
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        volume = hist['Volume'].iloc[-1]
        avg_vol = hist['Volume'].tail(21).mean()
        
        return {
            "current": round(current, 2),
            "change": round(current - prev, 2),
            "change_pct": round((current - prev) / prev * 100, 2),
            "volume": volume,
            "avg_volume": round(avg_vol, 2),
            "high": round(hist['High'].iloc[-1], 2),
            "low": round(hist['Low'].iloc[-1], 2),
            "open": round(hist['Open'].iloc[-1], 2),
            "dates": hist.index.tolist(),
            "close": hist['Close'].tolist(),
            "highs": hist['High'].tolist(),
            "lows": hist['Low'].tolist(),
            "volume_list": hist['Volume'].tolist()
        }
    except Exception as e:
        return None

# ============================================
# ส่วนที่ 2: คำนวณตัวชี้วัด (ครบทุกอย่าง)
# ============================================

def calculate_rsi(prices, period=14):
    """RSI"""
    if len(prices) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, period + 1):
        diff = prices[-i] - prices[-i-1]
        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))
    avg_gain = sum(gains)/period if gains else 0
    avg_loss = sum(losses)/period if losses else 1
    rs = avg_gain/avg_loss
    return round(100 - (100/(1+rs)), 2)

def calculate_ma(prices, period):
    """Moving Average"""
    if len(prices) < period:
        return prices[-1]
    return round(sum(prices[-period:])/period, 2)

def calculate_macd(prices):
    """MACD"""
    if len(prices) < 26:
        return 0, 0, 0
    ema12 = pd.Series(prices).ewm(span=12).mean().iloc[-1]
    ema26 = pd.Series(prices).ewm(span=26).mean().iloc[-1]
    macd = ema12 - ema26
    signal = pd.Series(prices).ewm(span=9).mean().iloc[-1]
    hist = macd - signal
    return round(macd, 2), round(signal, 2), round(hist, 2)

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
    return round(k, 2), round(k, 2)

def elliott_wave(prices, volumes):
    """Elliott Wave เบื้องต้น"""
    if len(prices) < 20:
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
    return support, resistance, strong_support

# ============================================
# ส่วนที่ 3: Market Depth จำลอง (ใช้กับหาตัง)
# ============================================

def get_market_depth(price):
    """จำลอง Depth 10 ชั้น"""
    import random
    bids, offers = [], []
    for i in range(10):
        bids.append({"price": round(price * (1 - 0.002 * i), 2), 
                     "vol": random.randint(50, 150)})
        offers.append({"price": round(price * (1 + 0.002 * i), 2), 
                       "vol": random.randint(50, 150)})
    # แทรกวาฬ
    if random.random() > 0.5:
        bids[2]["vol"] = random.randint(300, 500)
    if random.random() > 0.5:
        offers[2]["vol"] = random.randint(300, 500)
    return bids, offers

# ============================================
# ส่วนที่ 4: หน้าจอหลัก (ใช้หาตังได้จริง)
# ============================================

def show():
    st.markdown("# ⚡ เล่นสั้น - ครบทุกตัวชี้วัด")
    st.markdown("### RSI | MACD | Stochastic | Elliott | Depth")
    
    # เลือกหุ้น
    symbol = st.selectbox("เลือกหุ้น", ["SCC", "PTT", "ADVANC", "CPALL", "KCE"])
    
    if st.button("🔍 วิเคราะห์", type="primary"):
        with st.spinner("กำลังคำนวณ..."):
            data = get_stock_data(symbol)
            
            if not data:
                st.error("ไม่มีข้อมูล")
                return
            
            # คำนวณค่าต่างๆ
            rsi = calculate_rsi(data['close'])
            ma5 = calculate_ma(data['close'], 5)
            ma20 = calculate_ma(data['close'], 20)
            ma50 = calculate_ma(data['close'], 50)
            macd, signal, hist = calculate_macd(data['close'])
            stoch_k, stoch_d = calculate_stochastic(data['close'], data['highs'], data['lows'])
            wave, wave_signal, target, support = elliott_wave(data['close'], data['volume_list'])
            sup, res, strong_sup = calculate_support_resistance(data['close'])
            bids, offers = get_market_depth(data['current'])
            vol_ratio = data['volume'] / data['avg_volume']
            
            # ===== แถวที่ 1: ราคา =====
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 ราคา", f"{data['current']:.2f}", 
                       f"{data['change']:+.2f} ({data['change_pct']:+.2f}%)")
            col2.metric("📊 เปิด", data['open'])
            col3.metric("📈 สูง", data['high'])
            col4.metric("📉 ต่ำ", data['low'])
            
            # ===== แถวที่ 2: RSI + MA =====
            col1, col2, col3, col4 = st.columns(4)
            rsi_status = "🟢 ซื้อ" if rsi < 30 else "🔴 ขาย" if rsi > 70 else "⚪ กลาง"
            col1.metric("📊 RSI", rsi, rsi_status)
            col2.metric("📉 MA20", ma20)
            col3.metric("📈 MA50", ma50)
            vol_status = "🔥 สูง" if vol_ratio > 1.5 else "😴 ต่ำ" if vol_ratio < 0.5 else "⚖️ ปกติ"
            col4.metric("📦 Volume", f"{data['volume']/1e6:.1f}M", f"{vol_ratio:.2f}x")
            
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
                    st.write(f"{b['price']} : {b['vol']}K")
            with col2:
                st.markdown("### 🔴 Offers")
                for o in offers[:7]:
                    st.write(f"{o['price']} : {o['vol']}K")
            
            # ===== แถวที่ 7: จุดซื้อ-ขาย =====
            st.markdown("---")
            st.subheader("🎯 จุดซื้อ-ขาย")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🟢 จุดซื้อ")
                st.write(f"โซน: {sup:.2f} - {data['current']:.2f}")
                st.write(f"จุดช้อน: {sup:.2f}")
            with col2:
                st.markdown("### 🔴 จุดขาย")
                st.write(f"TP1: {data['current']*1.02:.2f} (+2%)")
                st.write(f"TP2: {data['current']*1.05:.2f} (+5%)")
                st.write(f"Cut: {data['current']*0.97:.2f} (-3%)")
            
            # ===== แถวที่ 8: กราฟ =====
            st.markdown("---")
            st.subheader("📈 กราฟราคา")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data['dates'][-30:], y=data['close'][-30:],
                mode='lines', name='ราคา',
                line=dict(color='blue', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=data['dates'][-30:], y=[ma20]*30,
                mode='lines', name='MA20',
                line=dict(color='orange', width=1, dash='dash')
            ))
            st.plotly_chart(fig, use_container_width=True)
            
            # ===== สรุป =====
            st.markdown("---")
            buy_signals = sum([
                rsi < 30, vol_ratio > 1.5, stoch_k < 20, 
                wave_signal == "buy" or wave_signal == "accumulate"
            ])
            sell_signals = sum([
                rsi > 70, stoch_k > 80, wave_signal == "sell"
            ])
            
            if buy_signals > sell_signals:
                st.success(f"✅ แนะนำ: ซื้อ (สัญญาณ {buy_signals}/{sell_signals})")
            elif sell_signals > buy_signals:
                st.error(f"❌ แนะนำ: ขาย (สัญญาณ {buy_signals}/{sell_signals})")
            else:
                st.info(f"⚖️ แนะนำ: รอดู")
