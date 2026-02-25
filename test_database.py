#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ทดสอบการทำงานของฐานข้อมูล
"""

from database import DatabaseManager
from datetime import datetime

def main():
    print("🚀 กำลังทดสอบฐานข้อมูล...")
    
    try:
        # 🔴 สร้าง instance
        with DatabaseManager() as db:
            
            # 🔴 สร้างตาราง
            db.create_tables()
            
            # 🔴 ทดสอบเพิ่มข้อมูลหุ้น
            stock_data = {
                "symbol": "SCC",
                "name_th": "ปูนซิเมนต์ไทย",
                "name_en": "Siam Cement",
                "sector": "Construction Materials",
                "industry": "Construction",
                "market": "SET"
            }
            db.insert_stock(stock_data)
            print("✅ เพิ่มข้อมูลหุ้น SCC")
            
            # 🔴 ทดสอบเพิ่มราคา
            price_data = {
                "symbol": "SCC",
                "date": datetime.now().date().isoformat(),
                "open": 227.0,
                "high": 229.0,
                "low": 226.0,
                "close": 228.0,
                "volume": 8244564,
                "value": 1864937060
            }
            db.insert_daily_price(price_data)
            print("✅ เพิ่มราคาประจำวัน")
            
            # 🔴 ทดสอบดึงข้อมูล
            stock = db.get_stock("SCC")
            print(f"📊 ข้อมูลหุ้น: {stock}")
            
            prices = db.get_prices("SCC", limit=5)
            print(f"📈 ราคาย้อนหลัง: {len(prices)} รายการ")
            
            print("\n✅ ทดสอบฐานข้อมูลสำเร็จ!")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main()
