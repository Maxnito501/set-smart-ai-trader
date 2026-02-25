#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ทดสอบการวิเคราะห์หุ้นระยะสั้น (Short Term)
"""

from analyzers import ShortTermAnalyzer
from database import DatabaseManager
import sys

def main():
    print("="*60)
    print("🚀 กำลังทดสอบ ShortTermAnalyzer...")
    print("="*60)
    
    try:
        with ShortTermAnalyzer() as analyzer:
            
            # 🔍 ทดสอบวิเคราะห์หุ้น SCC
            print("\n📊 วิเคราะห์ SCC...")
            result = analyzer.scan_symbol("SCC")
            
            print(f"   คะแนน: {result['score']}/10")
            print(f"   คำแนะนำ: {result['recommendation']}")
            print(f"   สัญญาณ: {result['signals']}")
            
            # 📈 แสดงราคา
            if "technical" in result:
                tech = result["technical"]
                print(f"   ราคา: {tech.get('current_price', 0):.2f}")
                print(f"   RSI: {tech.get('rsi', 0):.1f}")
            
            # 📋 ทดสอบ scan watchlist
            print("\n🔍 วิเคราะห์ watchlist...")
            watchlist = ["SCC", "PTT", "ADVANC", "CPALL", "KCE"]
            results = analyzer.scan_watchlist(watchlist)
            
            print("\n📋 ผลลัพธ์ (เรียงตามคะแนน):")
            for r in results:
                print(f"   {r['symbol']}: คะแนน {r['score']} - {r['recommendation']}")
            
            # 🟢 ดึงสัญญาณซื้อ
            print("\n🟢 สัญญาณซื้อวันนี้:")
            buys = analyzer.get_buy_signals(min_score=5)
            if buys:
                for b in buys:
                    print(f"   {b['symbol']}: คะแนน {b['score']}")
            else:
                print("   ไม่มีสัญญาณซื้อ")
            
            print("\n" + "="*60)
            print("✅ ทดสอบเสร็จสิ้น")
            print("="*60)
            
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        print("\n🔧 วิธีแก้:")
        print("   1. ตรวจสอบว่าเชื่อมต่อ API ได้ (python test_api.py)")
        print("   2. ตรวจสอบว่ามีข้อมูลในฐานข้อมูล (python test_database.py)")
        print("   3. ตรวจสอบ .env ว่าใส่ API Key ถูกต้อง")
        sys.exit(1)

if __name__ == "__main__":
    main()