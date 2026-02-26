"""
📁 pages/short_term.py
เล่นสั้น - ระบบตาทิพย์ ครบทุกดัชนี
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import time
import random

# ============================================
# ส่วนที่ 1: Yahoo Finance Client (มี Cache)
# ============================================

class YahooClient:
    """ดึงข้อมูลจาก Yahoo Finance"""
    
    def __init__(self):
        self.cache = {}
        print("✅ เชื่อมต่อ Yahoo Finance แล้ว")
    
    # 🔥 CACHE 5 นาที
    @st.cache_data(ttl=300)
    def get_price_cached(self, symbol):
        """ดึงราคาแบบมี Cache"""
        return self._get_price(symbol)
    
    # 🔥 CACHE 10 นาที
    @st.cache_data(ttl=600)
    def get_historical_cached(self, symbol, days=60):
        """ดึงข้อมูลย้อนหลังแบบมี Cache"""
        return self._get_historical(symbol, days)
    
    def _get_price(self, symbol):
        """ดึงราคาปัจจุบัน (จริง)"""
        try:
            ticker = yf.Ticker(f"{symbol}.BK")
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return None
            
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            volume = hist['Volume'].iloc[-1]
            
            # คำนวณค่าเฉลี่ย Volume 20 วัน
            if len(hist) >= 20:
                avg_vol = hist['Volume'].iloc[-21:-1].mean()
            else:
                avg_vol = volume
            
            return {
                "current": round(current, 2),
                "change": round(current - prev, 2),
                "change_pct": round((current - prev) / prev * 100, 2),
                "volume": volume,
                "avg_volume": avg_vol,
                "high": round(hist['High'].iloc[-1], 2),
                "low": round(hist['Low'].iloc[-1], 2),
                "open": round(hist['Open'].iloc[-1], 2),
                "prev_close": round(prev, 2)
            }
        except Exception as e:
            print(f"❌ Error {symbol}: {e}")
            return None
    
    def _get_historical(self, symbol, days=60):
        """ดึงข้อมูลย้อนหลัง (จริง)"""
        try:
            ticker = yf.Ticker(f"{symbol}.BK")
            hist = ticker.history(period=f"{days+20}d")
            
            if hist.empty:
                return None
            
            # ตัดให้ได้จำนวนวันที่ต้องการ
            if len(hist) > days:
                hist = hist.tail(days)
            
            return {
                "dates": hist.index.tolist(),
                "open": hist['Open'].tolist(),
                "high": hist['High'].tolist(),
                "low": hist['Low'].tolist(),
                "close": hist['Close'].tolist(),
                "volume": hist['Volume'].tolist()
            }
        except Exception as e:
            print(f"❌ Error historical {symbol}: {e}")
            return None


# ============================================
# ส่วนที่ 2: ฟังก์ชันคำนวณ Indicators
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

def calculate_macd(prices):
    """คำนวณ MACD เบื้องต้น"""
    if len(prices) < 26:
        return 0, 0, 0
    
    ema12 = pd.Series(prices).ewm(span=12).mean().iloc[-1]
    ema26 = pd.Series(prices).ewm(span=26).mean().iloc[-1]
    macd = ema12 - ema26
    signal = pd.Series(prices).ewm(span=9).mean().iloc[-1]
    histogram = macd - signal
    
    return round(macd, 2), round(signal, 2), round(histogram, 2)

def calculate_stochastic(prices, highs, lows, period=14):
    """คำนวณ Stochastic"""
    if len(prices) < period:
        return 50, 50
    
    recent_high = max(highs[-period:])
    recent_low = min(lows[-period:])
    current = prices[-1]
    
    if recent_high - recent_low == 0:
        k = 50
    else:
        k = ((current - recent_low) / (recent_high - recent_low)) * 100
    
    return round(k, 2), round(k, 2)

def elliott_wave_analysis(prices, volumes):
    """วิเคราะห์ Elliott Wave"""
    if len(prices) < 30:
        return "ข้อมูลไม่พอ", "neutral", 0, 0, ""
    
    current = prices[-1]
    recent_high = max(prices[-15:])
    recent_low = min(prices[-15:])
    
    vol_recent = sum(volumes[-5:]) / 5
    vol_prev = sum(volumes[-10:-5]) / 5
    vol_ratio = vol_recent / vol_prev if vol_prev > 0 else 1
    
    if current > recent_high * 0.98:
        if vol_ratio > 1.3:
            return "🌊 คลื่น 3 (กำลังขึ้น)", "buy", recent_high * 1.08, recent_low, "Volume หนุน"
        else:
            return "🌊 คลื่น 5 (ใกล้จบ)", "sell", current, recent_low * 0.97, "Volume ไม่มา"
    
    elif current < recent_low * 1.02:
        if vol_ratio > 1.3:
            return "🌊 คลื่น C (จบรอบ)", "accumulate", recent_low, recent_low * 0.95, "Volume หนุน"
        else:
            return "🌊 คลื่น 2 (ย่อตัว)", "wait", recent_high, recent_low, "รอจังหวะ"
    
    else:
        return "🌊 คลื่น 4 (พักตัว)", "hold", recent_high, recent_low, "sideways"


# ============================================
# ส่วนที่ 3: วิเคราะห์เจ้ามือ
# ============================================

class SmartEye:
    """จำลอง Market Depth"""
    
    def get_depth(self, symbol, base_price):
        """สร้าง Market Depth จำลอง"""
        
        scenarios = [
            {"intent": "accumulate", "whale": "🐋 กำลังสะสม", "bias": 2},
            {"intent": "distribute", "whale": "🦈 กำลังกระจาย", "bias": -2},
            {"intent": "wash", "whale": "🌀 เขย่าเม่า", "bias": 0},
            {"intent": "neutral", "whale": "🐟 ตลาดปกติ", "bias": 0}
        ]
        scene = random.choice(scenarios)
        
        bids = []
        offers = []
        
        for i in range(10):
            bid_price = base_price * (1 - 0.002 * i)
            if scene["intent"] == "accumulate" and i == 2:
                bid_vol = random.randint(300, 500) * 1000
            else:
                bid_vol = random.randint(50, 150) * 1000
            bids.append({"price": round(bid_price, 2), "volume": bid_vol})
        
        for i in range(10):
            offer_price = base_price * (1 + 0.002 * i)
            if scene["intent"] == "distribute" and i == 2:
                offer_vol = random.randint(300, 500) * 1000
            else:
                offer_vol = random.randint(50, 150) * 1000
            offers.append({"price": round(offer_price, 2), "volume": offer_vol})
        
        total_bid = sum(b['volume'] for b in bids)
        total_offer = sum(o['volume'] for o in offers)
        
        big_bids = [b for b in bids if b['volume'] > total_bid * 0.15]
        big_offers = [o for o in offers if o['volume'] > total_offer * 0.15]
        
        whale_ratio = len(big_bids) - len(big_offers) + scene["bias"]
        
        return {
            "bids": bids,
            "offers": offers,
            "whale_ratio": whale_ratio,
            "big_bids": len(big_bids),
            "big_offers": len(big_offers),
            "whale_desc": scene["whale"],
            "intent": scene["intent"]
        }


# ============================================
# ส่วนที่ 4: หน้าจอหลัก
# ============================================

def show():
    st.markdown("# ⚡ เล่นสั้น - ระบบตาทิพย์")
    st.markdown("### 📊 RSI | MACD | เส้นแกว่งตัว | Elliott | Volume | Depth")
    st.markdown("---")
    
    # เริ่มต้น clients
    if 'yahoo' not in st.session_state:
        st.session_state.yahoo = YahooClient()
    if 'eye' not in st.session_state:
        st.session_state.eye = SmartEye()
    
    # เลือกหุ้น
    col1, col2 = st.columns([3, 1])
    
    with col1:
        popular = ["SCC", "PTT", "ADVANC", "CPALL", "KCE"]
        symbol = st.selectbox("🔍 เลือกหุ้น", popular, index=0)
    
    with col2:
        analyze = st.button("🔮 วิเคราะห์", use_container_width=True, type="primary")
    
    # ============================================
    # วิเคราะห์เมื่อกดปุ่ม
    # ============================================
    if analyze or "last_symbol" not in st.session_state or st.session_state["last_symbol"] != symbol:
        
        st.session_state["last_symbol"] = symbol
        
        with st.spinner(f"🦅 กำลังวิเคราะห์ {symbol}..."):
            
            # ใช้ Cache
            price = st.session_state.yahoo.get_price_cached(symbol)
            hist = st.session_state.yahoo.get_historical_cached(symbol, 60)
            
            if not price or not hist:
                st.error(f"❌ ไม่สามารถดึงข้อมูล {symbol} ได้")
                st.stop()
            
            # คำนวณ Indicators
            rsi = calculate_rsi(hist['close'])
            ma5 = calculate_ma(hist['close'], 5)
            ma10 = calculate_ma(hist['close'], 10)
            ma20 = calculate_ma(hist['close'], 20)
            ma50 = calculate_ma(hist['close'], 50)
            
            macd, signal, hist_macd = calculate_macd(hist['close'])
            stoch_k, stoch_d = calculate_stochastic(hist['close'], hist['high'], hist['low'])
            
            # Volume
            vol_ratio = price['volume'] / price['avg_volume'] if price['avg_volume'] > 0 else 1
            if vol_ratio > 2:
                vol_signal = "🔥 SPIKE แรง"
            elif vol_ratio > 1.5:
                vol_signal = "📊 สูงกว่าปกติ"
            elif vol_ratio < 0.5:
                vol_signal = "😴 ต่ำ"
            else:
                vol_signal = "⚖️ ปกติ"
            
            # Elliott Wave
            wave_name, wave_signal, wave_target, wave_support, wave_desc = elliott_wave_analysis(
                hist['close'], hist['volume']
            )
            
            # Market Depth
            depth = st.session_state.eye.get_depth(symbol, price['current'])
            
            # เก็บใน session
            st.session_state.update({
                "price": price,
                "hist": hist,
                "rsi": rsi,
                "ma5": ma5,
                "ma10": ma10,
                "ma20": ma20,
                "ma50": ma50,
                "macd": macd,
                "signal": signal,
                "hist_macd": hist_macd,
                "stoch_k": stoch_k,
                "stoch_d": stoch_d,
                "vol_ratio": vol_ratio,
                "vol_signal": vol_signal,
                "wave_name": wave_name,
                "wave_signal": wave_signal,
                "wave_target": wave_target,
                "wave_support": wave_support,
                "wave_desc": wave_desc,
                "depth": depth
            })
    
    # ============================================
    # แสดงผล
    # ============================================
    if "price" in st.session_state:
        p = st.session_state.price
        
        # ---- แถวที่ 1: ราคา ----
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            delta = f"{p['change']:+.2f} ({p['change_pct']:+.2f}%)"
            st.metric("💰 ราคาปัจจุบัน", f"{p['current']:.2f}", delta)
        with col2:
            st.metric("📊 ราคาเปิด", f"{p['open']:.2f}")
        with col3:
            st.metric("📈 สูงสุด", f"{p['high']:.2f}")
        with col4:
            st.metric("📉 ต่ำสุด", f"{p['low']:.2f}")
        
        # ---- แถวที่ 2: Volume + RSI + MA ----
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 ปริมาณ", f"{p['volume']/1_000_000:.2f}M", 
                     f"{st.session_state.vol_ratio:.2f}x")
            st.caption(st.session_state.vol_signal)
        with col2:
            rsi = st.session_state.rsi
            rsi_status = "🟢 Oversold" if rsi < 30 else "🔴 Overbought" if rsi > 70 else "⚪ Neutral"
            st.metric("📊 RSI", f"{rsi}", rsi_status)
        with col3:
            st.metric("📉 MA20", f"{st.session_state.ma20:.2f}")
        with col4:
            st.metric("📈 MA50", f"{st.session_state.ma50:.2f}")
        
        # ---- แถวที่ 3: MACD + เส้นแกว่งตัว ----
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 MACD", f"{st.session_state.macd:.2f}")
        with col2:
            st.metric("📈 Signal", f"{st.session_state.signal:.2f}")
        with col3:
            st.metric("📉 Histogram", f"{st.session_state.hist_macd:.2f}")
        with col4:
            k_val = st.session_state.stoch_k
            status = "🟢 ต่ำ" if k_val < 20 else "🔴 สูง" if k_val > 80 else "⚪ ปกติ"
            st.metric("🎯 เส้นเร็ว", f"{k_val:.1f}", status)
        
        # ---- แถวที่ 4: เส้นแกว่งตัว (รายละเอียด) ----
        st.markdown("---")
        st.subheader("📊 เส้นแกว่งตัว (Stochastic)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            k_val = st.session_state.stoch_k
            if k_val < 20:
                st.success(f"**เส้นเร็ว:** {k_val:.1f} 🟢 ต่ำเกิน")
            elif k_val > 80:
                st.error(f"**เส้นเร็ว:** {k_val:.1f} 🔴 สูงเกิน")
            else:
                st.info(f"**เส้นเร็ว:** {k_val:.1f} ⚪ ปกติ")
        
        with col2:
            d_val = st.session_state.stoch_d
            if d_val < 20:
                st.success(f"**เส้นช้า:** {d_val:.1f} 🟢 ต่ำเกิน")
            elif d_val > 80:
                st.error(f"**เส้นช้า:** {d_val:.1f} 🔴 สูงเกิน")
            else:
                st.info(f"**เส้นช้า:** {d_val:.1f} ⚪ ปกติ")
        
        with col3:
            k_val = st.session_state.stoch_k
            d_val = st.session_state.stoch_d
            if k_val < 20 and d_val < 20:
                st.success("🟢 **ซื้อ** (oversold)")
            elif k_val > 80 and d_val > 80:
                st.error("🔴 **ขาย** (overbought)")
            else:
                st.info("⚪ **รอดู**")
        
        # ---- แถวที่ 5: Market Depth ----
        st.markdown("---")
        st.subheader("🐋 Market Depth 10 ชั้น")
        
        d = st.session_state.depth
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🟢 Bids")
            bids_df = pd.DataFrame(d['bids'][:7])
            bids_df.columns = ["ราคา", "จำนวน"]
            bids_df['จำนวน'] = (bids_df['จำนวน'] / 1000).astype(int).astype(str) + 'K'
            st.dataframe(bids_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 🔴 Offers")
            offers_df = pd.DataFrame(d['offers'][:7])
            offers_df.columns = ["ราคา", "จำนวน"]
            offers_df['จำนวน'] = (offers_df['จำนวน'] / 1000).astype(int).astype(str) + 'K'
            st.dataframe(offers_df, use_container_width=True, hide_index=True)
        
        # ---- แถวที่ 6: Elliott Wave ----
        st.markdown("---")
        st.subheader("🌊 Elliott Wave")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{st.session_state.wave_name}**")
            st.caption(st.session_state.wave_desc)
        with col2:
            st.markdown(f"🎯 **เป้าหมาย:** {st.session_state.wave_target:.2f}")
            st.markdown(f"🛡️ **แนวรับ:** {st.session_state.wave_support:.2f}")
        
        # ---- แถวที่ 7: กราฟ ----
        st.markdown("---")
        st.subheader("📈 กราฟราคา 45 วัน")
        
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=st.session_state.hist['dates'][-45:],
            open=st.session_state.hist['open'][-45:],
            high=st.session_state.hist['high'][-45:],
            low=st.session_state.hist['low'][-45:],
            close=st.session_state.hist['close'][-45:],
            name="ราคา",
            showlegend=False
        ))
        
        closes = st.session_state.hist['close'][-45:]
        ma20_vals = pd.Series(closes).rolling(20).mean()
        
        fig.add_trace(go.Scatter(
            x=st.session_state.hist['dates'][-45:], y=ma20_vals,
            mode='lines', name='MA20',
            line=dict(color='orange', width=1.5)
        ))
        
        fig.update_layout(height=400, xaxis_rangeslider_visible=False, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        
        # ---- แถวที่ 8: จุดซื้อ-ขาย ----
        st.markdown("---")
        st.subheader("🎯 จุดซื้อ-ขาย")
        
        recent = st.session_state.hist['close'][-10:]
        support = min(recent) * 0.98
        resistance = max(recent) * 1.02
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🟢 จุดซื้อ")
            st.markdown(f"**โซน:** {support:.2f} - {p['current']:.2f}")
            st.markdown(f"**จุดช้อน:** {support:.2f}")
        with col2:
            st.markdown("### 🔴 จุดขาย")
            st.markdown(f"**TP1:** {p['current']*1.02:.2f} (+2%)")
            st.markdown(f"**TP2:** {p['current']*1.05:.2f} (+5%)")
            st.markdown(f"**Cut:** {p['current']*0.97:.2f} (-3%)")
        
        st.caption(f"⏱️ อัปเดต: {datetime.now().strftime('%H:%M:%S')}")
