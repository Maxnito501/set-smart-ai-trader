#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ทดสอบการวิเคราะห์รายใหญ่ (Smart Money)
"""

from analyzers import SmartMoneyAnalyzer
from database import DatabaseManager

def main():
    print("🚀 กำลังทดสอบ SmartMoneyAnalyzer...")
    
    try:
        with SmartMoneyAnalyzer() as analyzer:
            
            # 🔴 1. วิเคราะห์ NVDR รายหุ้น
            print("\n🔍 วิเคราะห์ NVDR สำหรับ SCC...")
            nvdr = analyzer.analyze_nvdr_trend("SCC", days=20)
            
            if "error" not in nvdr:
                print(f"  ยอดซื้อสุทธิ 20 วัน: {nvdr['net_total']:,.0f} บาท")
                print(f"  วันซื้อ: {nvdr['buy_days']} วัน, วันขาย: {nvdr['sell_days']} วัน")
                print(f"  แนวโน้ม: {nvdr['trend']} ({nvdr['strength']})")
            
            # 🔴 2. หาหุ้นที่ NVDR กำลังสะสม
            print("\n💰 หุ้นที่ NVDR กำลังสะสม...")
            accum = analyzer.find_nvdr_accumulation(min_net=10_000_000)
            
            for a in accum[:5]:
                print(f"  {a['symbol']}: ยอดซื้อสุทธิ {a['net_total']:,.0f} บาท, {a['trend']}")
            
            # 🔴 3. วิเคราะห์ Big Lot
            print("\n📊 วิเคราะห์ Big Lot สำหรับ SCC...")
            big_lot = analyzer.analyze_big_lot("SCC", days=14)
            
            if "error" not in big_lot:
                print(f"  ซื้อสุทธิ: {big_lot['net']:,.0f} บาท")
                print(f"  จำนวนรายการ: {big_lot['transaction_count']} ครั้ง")
                print(f"  สัญญาณ: {big_lot['signal']}")
            
            # 🔴 4. วิเคราะห์ A/D Line
            print("\n📈 วิเคราะห์ Accumulation/Distribution สำหรับ SCC...")
            ad = analyzer.calculate_ad_line("SCC")
            
            if "error" not in ad:
                print(f"  A/D Trend: {ad['ad_trend']}")
                print(f"  สัญญาณ: {ad['signal']}")
                if ad.get('divergence'):
                    print(f"  Divergence: {ad['divergence']}")
            
            # 🔴 5. วิเคราะห์ครบวงจร
            print("\n🕵️ วิเคราะห์พฤติกรรมรายใหญ่ครบวงจร สำหรับ SCC...")
            smart = analyzer.analyze_smart_money("SCC")
            
            print(f"  คะแนน: {smart['score']}/10")
            print(f"  คำแนะนำ: {smart.get('recommendation', '')}")
            print(f"  สัญญาณ: {smart['signals']}")
            
            # 🔴 6. สแกนหุ้นทั้งหมด
            print("\n🔎 สแกนหุ้นที่รายใหญ่สนใจ...")
            all_smart = analyzer.scan_all_smart_money(limit=20)
            
            for s in all_smart[:5]:
                print(f"  {s['symbol']}: คะแนน {s['score']} - {s['recommendation']}")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main()
