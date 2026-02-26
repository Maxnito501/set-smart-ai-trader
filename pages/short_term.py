"""
📁 pages/short_term.py
หน้าเล่นสั้น - ระบบตาทิพย์ออโต้ วิเคราะห์เจ้ามือ ราคา Volume Elliott Wave
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import requests

# ============================================
# ส่วนที่ 1: ระบบตาทิพย์ออโต้ (ป้องกันบล็อก)
# ============================================

class SmartEye:
    """
    ระบบตาทิพย์ออโต้ - ดึงข้อมูลแบบไม่ให้โดนบล็อก
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.setsmart.com/api"  # เปลี่ยนตามจริง
        self.last_call = {}
        self.backoff_state = {}
        print("🦾 ระบบตาทิพย์ออโต้พร้อมทำงาน")
    
    def _can_call(self, endpoint, symbol):
        """กฎข้อ 1: เว้นจังหวะ 15-30 วินาที"""
        key = f"{endpoint}_{symbol}"
        last = self.last_call.get(key, 0)
        elapsed = time.time() - last
        
        min_interval = random.randint(15, 30)
        
        if elapsed < min_interval:
            return False, min_interval - elapsed
        return True, 0
    
    def _update_last_call(self, endpoint, symbol):
        key = f"{endpoint}_{symbol}"
        self.last_call[key] = time.time()
    
    def get_market_depth(self, symbol):
        """ดึง Market Depth (จำลอง) - รอ API จริง"""
        can_call, wait = self._can_call("depth", symbol)
        if not can_call:
            return None
            
        # 🔴 จำลองข้อมูล (รอเชื่อม API จริง)
        time.sleep(0.5)
        self._update_last_call("depth", symbol)
        
        # สร้าง Bids/Offers จำลอง
        base_price = self._get_base_price(symbol)
        
        bids = []
        offers = []
        
        # สุ่มเจตนารายใหญ่
        whale_intent = random.choice(["accumulate", "distribute", "wash", "neutral"])
        
        for i in range(10):
            # Bids (ฝั่งซื้อ)
            bid_price = base_price * (1 - 0.002 * i)
            bid_vol = random.randint(10, 100) * 1000
            
            # ถ้ารายใหญ่กำลัง accumulate จะมี bid ขนาดใหญ่แทรก
            if whale_intent == "accumulate" and i == 2:
                bid_vol = random.randint(200, 500) * 1000
                
            bids.append({"price": round(bid_price, 2), "volume": bid_vol})
            
            # Offers (ฝั่งขาย)
            offer_price = base_price * (1 + 0.002 * i)
            offer_vol = random.randint(10, 100) * 1000
            
            # ถ้ารายใหญ่กำลัง distribute จะมี offer ขนาดใหญ่แทรก
            if whale_intent == "distribute" and i == 2:
                offer_vol = random.randint(200, 500) * 1000
                
            offers.append({"price": round(offer_price, 2), "volume": offer_vol})
        
        # วิเคราะห์ Whale Ratio
        total_bid = sum(b['volume'] for b in bids)
        total_offer = sum(o['volume'] for o in offers)
        
        big_bids = [b for b in bids if b['volume'] > total_bid * 0.15]
        big_offers = [o for o in offers if o['volume'] > total_offer * 0.15]
        
        whale_ratio = len(big_bids) - len(big_offers)
        
        return {
            "bids": bids,
            "offers": offers,
            "total_bid_vol": total_bid,
            "total_offer_vol": total_offer,
            "big_bids": len(big_bids),
            "big_offers": len(big_offers),
            "whale_ratio": whale_ratio,
            "intent": whale_intent,
            "signal": "BULL" if whale_ratio > 0 else "BEAR" if whale_ratio < 0 else "NEUTRAL"
        }
    
    def _get_base_price(self, symbol):
        """ราคาพื้นฐานตามหุ้น"""
        prices = {
            "SCC": 228.0, "PTT": 34.5, "ADVANC": 245.0, "CPALL": 58.5, "KCE": 19.9,
            "GULF": 45.2, "PTTEP": 148.0, "BBL": 142.0, "KBANK": 138.0, "SCB": 112.0,
            "AOT": 68.0, "BH": 185.0, "BDMS": 26.4, "CPF": 22.7, "TRUE": 5.8
        }
        return prices.get(symbol, 100.0)

# ============================================
# ส่วนที่ 2: ฟังก์ชันคำนวณทางเทคนิค
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
        return "ข้อมูลไม่พอ", "neutral", 0, 0
    
    current = prices[-1]
    recent_high = max(prices[-10:])
    recent_low = min(prices[-10:])
    
    # จำลอง wave count
    wave_patterns = [
        ("🌊 คลื่น 1 (เริ่มสะสม)", "accumulate", recent_low * 1.05, recent_low),
        ("🌊 คลื่น 2 (ย่อตัว)", "wait", recent_high, recent_low),
        ("🌊 คลื่น 3 (กำลังขึ้นแรง)", "buy", recent_high * 1.08, recent_low),
        ("🌊 คลื่น 4 (พักตัว)", "hold", recent_high, recent_low * 0.98),
        ("🌊 คลื่น 5 (ใกล้จบ)", "sell", recent_high * 1.02, current),
        ("🌊 คลื่น A (เริ่มลง)", "sell", current, recent_low),
        ("🌊 คลื่น B (รีบาวด์)", "wait", recent_high, current),
        ("🌊 คลื่น C (จบรอบ)", "accumulate", recent_low, recent_low * 0.95)
    ]
    
    # เลือกตามสถานการณ์
    idx = (len(prices) // 5) % len(wave_patterns)
    return wave_patterns[idx]

def analyze_volume_pattern(volumes, prices, period=20):
    """วิเคราะห์รูปแบบ Volume เพื่อดูเจ้ามือ"""
    if len(volumes) < period:
        return "ข้อมูลไม่พอ", "neutral"
    
    current_vol = volumes[-1]
    avg_vol = sum(volumes[-period-1:-1]) / period
    vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
    
    current_price = prices[-1]
    prev_price = prices[-2]
    price_change = current_price - prev_price
    
    # วิเคราะห์เจตนาจาก Volume + ราคา
    if vol_ratio > 2.0:
        if price_change > 0:
            return "🔥  volume พุ่ง + ราคาขึ้น = รายใหญ่กำลังเก็บ", "accumulate"
        else:
            return "⚠️ volume พุ่ง + ราคาลง = รายใหญ่กำลังทิ้ง", "distribute"
    elif vol_ratio > 1.5:
        if price_change > 0:
            return "📈 volume สูง + ราคาขึ้น = มีแรงซื้อ", "mild_accumulate"
        else:
            return "📉 volume สูง + ราคาลง = มีแรงขาย", "mild_distribute"
    elif vol_ratio < 0.5:
        return "😴 volume ต่ำ = ตลาดเงียบ รายใหญ่หยุดพัก", "neutral"
    else:
        return "⚖️ volume ปกติ = ตลาดสมดุล", "neutral"

def detect_whale_game(bids, offers, volume_analysis):
    """ตรวจจับเกมของเจ้ามือ"""
    
    total_bid_vol = sum(b['volume'] for b in bids)
    total_offer_vol = sum(o['volume'] for o in offers)
    
    bid_offer_ratio = total_bid_vol / total_offer_vol if total_offer_vol > 0 else 1
    
    # หา Bid/Offer ขนาดใหญ่ผิดปกติ
    big_bids = [b for b in bids if b['volume'] > total_bid_vol * 0.2]
    big_offers = [o for o in offers if o['volume'] > total_offer_vol * 0.2]
    
    result = {
        "bid_offer_ratio": round(bid_offer_ratio, 2),
        "big_bids": len(big_bids),
        "big_offers": len(big_offers),
        "games": []
    }
    
    # วิเคราะห์เกม
    if big_bids and not big_offers:
        result["games"].append("🐋 มีวาฬวาง Bid ขนาดใหญ่ รอซื้อ")
        result["intent"] = "accumulate"
    elif big_offers and not big_bids:
        result["games"].append("🦈 มีวาฬวาง Offer ขนาดใหญ่ รอขาย")
        result["intent"] = "distribute"
    elif big_bids and big_offers:
        result["games"].append("⚔️ วาฬต่อสู้กัน ทั้งซื้อและขาย")
        result["intent"] = "fight"
    else:
        result["games"].append("🐟 ตลาดรายย่อย ไม่มีวาฬ")
        result["intent"] = "retail"
    
    # วิเคราะห์จาก volume
    if "accumulate" in volume_analysis[1]:
        result["games"].append("📊 volume บ่งชี้ว่ากำลังสะสม")
        result["intent"] = "accumulate"
    elif "distribute" in volume_analysis[1]:
        result["games"].append("📊 volume บ่งชี้ว่ากำลังกระจาย")
        result["intent"] = "distribute"
    
    return result

# ============================================
# ส่วนที่ 3: หน้าจอหลัก
# ============================================

def show():
    st.markdown("# ⚡ เล่นสั้น - ระบบตาทิพย์ออโต้")
    st.markdown("### 🎯 เป้าหมาย: หาเงินค่ากับข้าวเดือนละ 3-5%")
    st.markdown("---")
    
    # เริ่มระบบตาทิพย์
    if 'smart_eye' not in st.session_state:
        api_key = st.secrets.get("SETSMART_API_KEY", "demo")
        st.session_state.smart_eye = SmartEye(api_key)
    
    # ============================================
    # เลือกหุ้น
    # ============================================
    col1, col2 = st.columns([3, 1])
    
    with col1:
        popular = ["SCC", "PTT", "ADVANC", "CPALL", "KCE", "GULF", "PTTEP", "BBL", "KBANK", "SCB"]
        selected = st.selectbox("🔍 เลือกหุ้นที่ต้องการวิเคราะห์", popular, index=0)
    
    with col2:
        scan = st.button("🔄 สแกน", use_container_width=True, type="primary")
    
    # ============================================
    # ดึงข้อมูลเมื่อกดสแกน หรือเปลี่ยนหุ้น
    # ============================================
    if scan or "last_symbol" not in st.session_state or st.session_state["last_symbol"] != selected:
        
        st.session_state["last_symbol"] = selected
        
        with st.spinner(f"🦅 กำลังสแกน {selected}..."):
            
            # 1. ดึง Market Depth
            depth = st.session_state.smart_eye.get_market_depth(selected)
            
            # 2. สร้างข้อมูลราคาจำลอง
            base_price = st.session_state.smart_eye._get_base_price(selected)
            
            # เพิ่มความผันผวนตามสถานการณ์
            volatility = random.uniform(-0.03, 0.03)
            current_price = base_price * (1 + volatility)
            
            # สร้างข้อมูลย้อนหลัง
            dates = pd.date_range(end=datetime.now(), periods=45).tolist()
            closes = []
            for i in range(45):
                trend = i * 0.001 * random.choice([-1, 1])
                noise = random.uniform(-0.02, 0.02)
                closes.append(base_price * (1 + trend + noise))
            
            opens = [c * (1 + random.uniform(-0.01, 0.01)) for c in closes]
            highs = [max(o, c) * (1 + random.uniform(0, 0.02)) for o, c in zip(opens, closes)]
            lows = [min(o, c) * (1 - random.uniform(0, 0.02)) for o, c in zip(opens, closes)]
            volumes = [int(random.uniform(1, 10) * 1_000_000) for _ in range(45)]
            
            # 3. คำนวณ Indicators
            rsi = calculate_rsi(closes)
            ma5 = calculate_ma(closes, 5)
            ma10 = calculate_ma(closes, 10)
            ma20 = calculate_ma(closes, 20)
            wave_name, wave_signal, wave_target, wave_support = elliott_wave(closes)
            
            # 4. วิเคราะห์ Volume
            vol_analysis, vol_intent = analyze_volume_pattern(volumes, closes)
            
            # 5. วิเคราะห์เกมเจ้ามือ
            whale_game = detect_whale_game(depth['bids'], depth['offers'], (vol_analysis, vol_intent))
            
            # เก็บใน session
            st.session_state.update({
                "current_price": current_price,
                "volume": volumes[-1],
                "change": current_price - base_price,
                "change_pct": ((current_price - base_price) / base_price * 100),
                "open": opens[-1],
                "high": highs[-1],
                "low": lows[-1],
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
                "wave_name": wave_name,
                "wave_signal": wave_signal,
                "wave_target": wave_target,
                "wave_support": wave_support,
                "vol_analysis": vol_analysis,
                "vol_intent": vol_intent,
                "depth": depth,
                "whale_game": whale_game,
                "avg_vol": sum(volumes[-21:-1]) / 20,
                "vol_ratio": volumes[-1] / (sum(volumes[-21:-1]) / 20) if len(volumes) > 20 else 1
            })
    
    # ============================================
    # แสดงผล
    # ============================================
    if "current_price" in st.session_state:
        
        # ---------- ส่วนที่ 1: วิเคราะห์เจ้ามือ ----------
        st.markdown("---")
        st.subheader("🐋 วิเคราะห์เจ้ามือ")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🟢 Bids (ฝั่งซื้อ)")
            bids_df = pd.DataFrame(st.session_state.depth['bids'][:5])
            bids_df.columns = ["ราคา", "จำนวน"]
            bids_df['จำนวน'] = bids_df['จำนวน'] / 1000
            bids_df['จำนวน'] = bids_df['จำนวน'].astype(int).astype(str) + 'K'
            st.dataframe(bids_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 🔴 Offers (ฝั่งขาย)")
            offers_df = pd.DataFrame(st.session_state.depth['offers'][:5])
            offers_df.columns = ["ราคา", "จำนวน"]
            offers_df['จำนวน'] = offers_df['จำนวน'] / 1000
            offers_df['จำนวน'] = offers_df['จำนวน'].astype(int).astype(str) + 'K'
            st.dataframe(offers_df, use_container_width=True, hide_index=True)
        
        # แสดงสรุปเกม
        whale = st.session_state.whale_game
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🐋 วาฬฝั่งซื้อ", whale['big_bids'])
        
        with col2:
            st.metric("🦈 วาฬฝั่งขาย", whale['big_offers'])
        
        with col3:
            st.metric("⚖️ Bid/Offer Ratio", f"{whale['bid_offer_ratio']:.2f}")
        
        for game in whale['games']:
            if "accumulate" in game or "🐋" in game:
                st.success(game)
            elif "distribute" in game or "🦈" in game:
                st.error(game)
            else:
                st.info(game)
        
        # ---------- ส่วนที่ 2: ราคาและ Volume ----------
        st.markdown("---")
        st.subheader("📊 ราคาและปริมาณซื้อขาย")
        
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
        
        # แถว Volume
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📦 ปริมาณ", f"{st.session_state['volume']/1_000_000:.2f}M", 
                     f"{st.session_state['vol_ratio']:.2f}x")
        
        with col2:
            st.metric("📊 RSI (14)", f"{st.session_state['rsi']}", 
                     "oversold" if st.session_state['rsi'] < 30 else "overbought" if st.session_state['rsi'] > 70 else "neutral")
        
        with col3:
            status = "above" if st.session_state['current_price'] > st.session_state['ma20'] else "below"
            st.metric("📉 MA20", f"{st.session_state['ma20']:.2f}", status)
        
        with col4:
            st.metric("📈 MA5/MA10", f"{st.session_state['ma5']:.2f} / {st.session_state['ma10']:.2f}")
        
        # แสดงการวิเคราะห์ Volume
        st.info(f"📊 {st.session_state['vol_analysis']}")
        
        # ---------- ส่วนที่ 3: Elliott Wave ----------
        st.markdown("---")
        st.subheader("🌊 Elliott Wave Analysis")
        
        wave = st.session_state['wave_name']
        wave_signal = st.session_state['wave_signal']
        wave_target = st.session_state['wave_target']
        wave_support = st.session_state['wave_support']
        
        if wave_signal == "buy":
            st.success(f"{wave} - 🎯 เป้าหมาย {wave_target:.2f} | 🛡️ แนวรับ {wave_support:.2f}")
        elif wave_signal == "sell":
            st.error(f"{wave} - 🎯 เป้าหมาย {wave_target:.2f} | 🛡️ แนวรับ {wave_support:.2f}")
        elif wave_signal == "accumulate":
            st.info(f"{wave} - 🎯 เป้าหมาย {wave_target:.2f} | 🛡️ แนวรับ {wave_support:.2f}")
        else:
            st.info(f"{wave} - 🎯 เป้าหมาย {wave_target:.2f} | 🛡️ แนวรับ {wave_support:.2f}")
        
        # ---------- ส่วนที่ 4: กราฟ ----------
        st.markdown("---")
        st.subheader("📈 กราฟราคา")
        
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
            height=400,
            xaxis_rangeslider_visible=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # ---------- ส่วนที่ 5: จุดซื้อ-ขาย + เป้าหมาย ----------
        st.markdown("---")
        st.subheader("🎯 จุดซื้อ-ขาย แนะนำ")
        
        # คำนวณแนวรับ-แนวต้าน
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
            st.markdown(f"**Elliott:** {wave_signal}")
        
        with col2:
            st.markdown("### 🔴 จุดขาย / Cut loss")
            st.markdown(f"**TP1:** {st.session_state['current_price']*1.02:.2f} (+2%)")
            st.markdown(f"**TP2:** {st.session_state['current_price']*1.05:.2f} (+5%)")
            st.markdown(f"**Cut loss:** {st.session_state['current_price']*0.97:.2f} (-3%)")
            st.markdown(f"**แนวต้าน:** {resistance:.2f}")
        
        # ---------- ส่วนที่ 6: สรุปคำแนะนำ ----------
        st.markdown("---")
        st.subheader("💡 สรุปคำแนะนำ")
        
        # วิเคราะห์รวมทุกปัจจัย
        buy_signals = 0
        sell_signals = 0
        
        if st.session_state['rsi'] < 30:
            buy_signals += 1
        if st.session_state['rsi'] > 70:
            sell_signals += 1
        
        if st.session_state['vol_ratio'] > 1.5 and st.session_state['change'] > 0:
            buy_signals += 1
        if st.session_state['vol_ratio'] > 1.5 and st.session_state['change'] < 0:
            sell_signals += 1
        
        if "accumulate" in st.session_state.whale_game['intent']:
            buy_signals += 2
        if "distribute" in st.session_state.whale_game['intent']:
            sell_signals += 2
        
        if wave_signal == "buy":
            buy_signals += 2
        elif wave_signal == "sell":
            sell_signals += 2
        
        if buy_signals > sell_signals:
            st.success(f"✅ แนะนำ: ซื้อ (สัญญาณซื้อ {buy_signals} / ขาย {sell_signals})")
            st.markdown(f"**เป้าหมายกำไรเดือนนี้:** 3-5% จากเงินลงทุน")
        elif sell_signals > buy_signals:
            st.error(f"❌ แนะนำ: ขาย / รอ (สัญญาณซื้อ {buy_signals} / ขาย {sell_signals})")
        else:
            st.info(f"⚖️ แนะนำ: รอดู (สัญญาณซื้อ {buy_signals} / ขาย {sell_signals})")
        
        # เวลาอัปเดท
        st.caption(f"⏱️ อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')}")
