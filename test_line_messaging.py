#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ทดสอบ LINE Messaging API
"""

from notification import LineMessaging
from datetime import datetime

def main():
    print("🚀 กำลังทดสอบ LineMessaging...")
    
    # 🔴 สร้าง LINE messaging
    line = LineMessaging()
    
    # 🔴 ทดสอบส่งข้อความธรรมดา
    print("\n📝 ทดสอบส่งข้อความธรรมดา...")
    line.send("🚀 ทดสอบระบบแจ้งเตือน LINE Messaging API")
    
    # 🔴 ทดสอบส่งสัญญาณซื้อ (จำลอง)
    print("\n🟢 ทดสอบส่งสัญญาณซื้อ...")
    
    mock_signal = {
        "symbol": "SCC",
        "score": 8,
        "recommendation": "STRONG_BUY",
        "signals": ["VOLUME_SPIKE", "NVDR_BUYING", "OVERSOLD"],
        "technical": {
            "current_price": 228.50,
            "rsi": 32.5
        },
        "volume": {
            "volume_ratio": 2.8
        },
        "nvdr": {
            "net_total": 45000000,
            "trend": "ACCUMULATING"
        }
    }
    
    line.send_buy_signal(mock_signal)
    
    # 🔴 ทดสอบส่งรายใหญ่
    print("\n🐳 ทดสอบส่งรายใหญ่...")
    
    mock_smart = {
        "symbol": "SCC",
        "score": 6,
        "recommendation": "BULLISH (รายใหญ่เริ่มเก็บ)",
        "signals": ["NVDR_ACCUMULATING", "BIG_LOT_BUYING", "AD_ACCUMULATION"],
        "nvdr": {
            "trend": "ACCUMULATING"
        },
        "big_lot": {
            "signal": "BUYING",
            "net": 12500000
        },
        "ad_line": {
            "signal": "ACCUMULATION"
        }
    }
    
    line.send_smart_money_alert(mock_smart)
    
    # 🔴 ทดสอบส่งสรุปรายวัน
    print("\n📊 ทดสอบส่งสรุปรายวัน...")
    
    mock_short = [
        {"symbol": "SCC", "score": 8, "recommendation": "STRONG_BUY", "technical": {"current_price": 228.5}},
        {"symbol": "PTT", "score": 6, "recommendation": "BUY", "technical": {"current_price": 34.5}},
        {"symbol": "ADVANC", "score": 4, "recommendation": "WATCH", "technical": {"current_price": 245.0}}
    ]
    
    mock_long = [
        {"symbol": "SCC", "dividend_yield": 5.2, "score": 8},
        {"symbol": "PTT", "dividend_yield": 4.8, "score": 7},
        {"symbol": "CPALL", "dividend_yield": 3.5, "score": 5}
    ]
    
    mock_smart_list = [
        {"symbol": "SCC", "score": 6, "recommendation": "BULLISH"},
        {"symbol": "KCE", "score": -3, "recommendation": "BEARISH"}
    ]
    
    line.send_daily_summary(mock_short, mock_long, mock_smart_list)
    
    print("\n✅ ทดสอบ LINE Messaging API เสร็จสิ้น")
    print("📱 ดูผลที่แอป LINE (ถ้าใส่ Channel Access Token จริง)")

if __name__ == "__main__":
    main()
