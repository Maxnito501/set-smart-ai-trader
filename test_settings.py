#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ทดสอบว่า settings โหลดค่าถูกต้อง
"""

from config.settings import settings

def main():
    print("\n" + "="*60)
    print("📋 สรุปค่าที่โหลดจาก .env")
    print("="*60)
    
    # 🔴 SET SMART
    print(f"\n🔑 SETSMART_API_KEY: {settings.SETSMART_API_KEY}")
    print(f"🌐 SETSMART_BASE_URL: {settings.SETSMART_BASE_URL}")
    
    # 🔴 LINE
    print(f"\n💬 LINE_CHANNEL_ACCESS_TOKEN: {settings.LINE_CHANNEL_ACCESS_TOKEN}")
    print(f"👤 LINE_USER_ID: {settings.LINE_USER_ID}")
    
    # 🔴 Database
    print(f"\n🗄️ DB_PATH: {settings.DB_PATH}")
    
    # 🔴 Environment
    print(f"\n🌍 ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"   is_development(): {settings.is_development()}")
    print(f"   is_production(): {settings.is_production()}")
    
    # 🔴 Base Directory
    print(f"\n📁 BASE_DIR: {settings.BASE_DIR}")
    
    print("\n" + "="*60)
    print("✅ ทดสอบเสร็จสิ้น")
    print("="*60)

if __name__ == "__main__":
    main()
