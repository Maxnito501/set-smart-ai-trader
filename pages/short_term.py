import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf
import time

# ============================================
# ส่วนที่ 1: ดึงข้อมูล (เพิ่ม Cache + Timeout)
# ============================================

@st.cache_data(ttl=300)  # Cache 5 นาที
def get_stock_data(symbol):
    """ดึงข้อมูลหุ้น (มี Cache ป้องกัน Rate Limit)"""
    try:
        # จำกัดเวลา Request ไม่เกิน 5 วินาที
        ticker = yf.Ticker(f"{symbol}.BK")
        hist = ticker.history(period="2mo", timeout=5)
        
        if hist.empty:
            return None
        
        # ข้อมูลล่าสุด
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        
        return {
            "current": round(current, 2),
            "change": round(current - prev, 2),
            "change_pct": round((current - prev) / prev * 100, 2),
            "volume": hist['Volume'].iloc[-1],
            "dates": hist.index.tolist(),
            "closes": hist['Close'].tolist()
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

# ============================================
# ส่วนที่ 2: หน้าจอหลัก (แบบสั้น เร็ว)
# ============================================

def show():
    st.markdown("# ⚡ เล่นสั้น")
    
    # เลือกแค่ 3 หุ้นก่อน (ลดการเรียก API)
    symbol = st.selectbox("เลือกหุ้น", ["SCC", "PTT", "ADVANC"])
    
    if st.button("วิเคราะห์", type="primary"):
        with st.spinner("กำลังโหลด..."):
            data = get_stock_data(symbol)
            
            if data:
                st.metric("ราคา", f"{data['current']:.2f}", 
                         f"{data['change']:+.2f} ({data['change_pct']:+.2f}%)")
                st.metric("Volume", f"{data['volume']/1e6:.1f}M")
                
                # กราฟ
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data['dates'][-30:], 
                    y=data['closes'][-30:],
                    mode='lines'
                ))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("ไม่สามารถโหลดข้อมูลได้ ลองอีกครั้ง")
