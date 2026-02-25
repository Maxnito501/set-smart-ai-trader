#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ทดสอบการเชื่อมต่อ API
"""

from api import SetSmartClient
from config.settings import settings

def main():
    print("🚀 กำลังทดสอบ API...")
    
    # โชว์ API Key บางส่วน (ซ่อนไว้)
    api_key = settings.SETSMART_API_KEY
    if api_key and len(api_key) > 8:
        print(f"🔑 API Key: {api_key[:5]}...{api_key[-5:]}")
    else:
        print("⚠️ ไม่พบ API Key ใน .env")
    
    # ทดสอบเชื่อมต่อ
    client = SetSmartClient()
    if client.test_connection():
        print("\n✅ พร้อมใช้งานแล้ว!")
    else:
        print("\n❌ ยังเชื่อมต่อไม่ได้")

if __name__ == "__main__":
    main()