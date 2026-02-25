"""
📁 config/settings.py
ไว้สำหรับโหลดค่าต่างๆ จากไฟล์ .env และจัดการ configurations
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 🔴 โหลดไฟล์ .env จาก root directory
load_dotenv()

class Settings:
    """
    คลาสสำหรับเก็บค่าตั้งค่าต่างๆ ของโปรเจกต์
    """
    
    def __init__(self):
        # 🔴 BASE DIRECTORY (ที่อยู่ของโปรเจกต์)
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        
        # 🔴 SET SMART API Configuration
        self.SETSMART_API_KEY = os.getenv("SETSMART_API_KEY")
        self.SETSMART_BASE_URL = os.getenv("SETSMART_BASE_URL", "https://api.setsmart.com")
        
        # 🔴 LINE Notification
        self.LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")
        
        # 🔴 Database Configuration
        self.DB_PATH = os.getenv("DB_PATH", str(self.BASE_DIR / "data" / "setsmart.db"))
        
        # 🔴 Environment
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        
        # 🔴 ตรวจสอบค่าสำคัญ
        self.validate()
    
    def validate(self):
        """
        ตรวจสอบว่ามีค่าที่จำเป็นครบหรือไม่
        """
        # ถ้าไม่มี API Key ให้แสดง warning
        if not self.SETSMART_API_KEY or self.SETSMART_API_KEY == "YOUR_API_KEY_HERE":
            print("⚠️ Warning: กรุณาใส่ SETSMART_API_KEY ในไฟล์ .env")
            print("   (ถ้ายังไม่มี Key ให้ขอจาก SET SMART ก่อน)")
        
        # ถ้าอยู่ใน production ควรมี API Key
        if self.ENVIRONMENT == "production" and not self.SETSMART_API_KEY:
            raise ValueError("❌ production mode ต้องมี SETSMART_API_KEY")
    
    def is_development(self):
        """เช็คว่าเป็น development mode หรือไม่"""
        return self.ENVIRONMENT == "development"
    
    def is_production(self):
        """เช็คว่าเป็น production mode หรือไม่"""
        return self.ENVIRONMENT == "production"

# 🔴 สร้าง instance ของ settings ไว้ใช้ที่อื่นๆ
settings = Settings()
