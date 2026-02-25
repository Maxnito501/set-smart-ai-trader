#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ทดสอบการวิเคราะห์หุ้นระยะยาว
"""

from analyzers import LongTermAnalyzer
from database import DatabaseManager
from datetime import datetime

def main():
    print("🚀 กำลังทดสอบ LongTermAnalyzer...")
    
    try:
        with LongTermAnalyzer() as analyzer:
            
            # 🔴 1. คัดกรองหุ้นปันผลสูง
            print("\n🔍 คัดกรองหุ้นปันผลสูง (Yield > 4%, ROE > 10%)...")
            div_stocks = analyzer.screen_high_dividend()
            
            print(f"📊 พบ {len(div_stocks)} ตัว")
            for s in div_stocks[:5]:  # แค่ 5 ตัวแรก
                print(f"  {s['symbol']}: Yield {s['current_dividend_yield']}% (เฉลี่ย {s['avg_dividend_yield_5y']}%), ROE {s['roe']}%")
            
            # 🔴 2. โอกาส DCA
            print("\n💰 โอกาส DCA (งบเดือนละ 10,000 บาท)...")
            dca = analyzer.find_dca_opportunities(budget_per_month=10000)
            
            for d in dca[:3]:
                print(f"  {d['symbol']}: {d['shares_per_month']} หุ้น/เดือน, ปีได้ปันผล {d['expected_annual_dividend']:,.0f} บาท")
            
            # 🔴 3. วิเคราะห์จังหวะ XD
            print("\n📅 วิเคราะห์จังหวะ XD สำหรับ SCC...")
            xd = analyzer.analyze_xd_timing("SCC")
            
            print(f"  ราคา: {xd.get('current_price')}")
            print(f"  ปันผลล่าสุด: {xd.get('last_dividend')} บาท")
            print(f"  Yield ปัจจุบัน: {xd.get('current_yield')}%")
            print(f"  คำแนะนำ: {xd.get('recommendation')}")
            print(f"  เหตุผล: {xd.get('reason')}")
            
            # 🔴 4. โอกาสซื้อ
            print("\n🟢 โอกาสซื้อสำหรับระยะยาว...")
            buys = analyzer.get_buy_opportunities(min_score=5)
            
            for b in buys[:5]:
                print(f"  {b['symbol']}: คะแนน {b['score']}, {b['reason']}")
            
            # 🔴 5. เทียบกับดอกเบี้ย
            print("\n🏦 เทียบกับดอกเบี้ย 2.5%...")
            compare = analyzer.compare_with_risk_free()
            
            for c in compare[:5]:
                star = "⭐" if c["attractive"] else ""
                print(f"  {c['symbol']}: {c['dividend_yield']}% - ส่วนต่าง {c['premium']}% {star}")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main()
