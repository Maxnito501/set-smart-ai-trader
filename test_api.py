#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ทดสอบการเชื่อมต่อ API
"""

from api import SetSmartClient
from config.settings import settings

def main():
    print("🚀 กำลังทดสอบ API...")
    print(f"🔑 API Key: {settings.SETSMART_API_KEY[:5]}... (ซ่อนบางส่วน)")
    
    client = SetSmartClient()
    client.test_connection()

if __name__ == "__main__":
    main()