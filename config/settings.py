"""
📁 config/settings.py
ไว้สำหรับโหลดค่าต่างๆ จากไฟล์ .env และจัดการ configurations
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 🔴 โหลดไฟล์ .env จาก root directory
#    ไฟล์ .env ต้องอยู่ที่เดียวกับ README.md
load_dotenv()


class Settings:
    """
    คลาสสำหรับเก็บค่าตั้งค่าต่างๆ ของโปรเจกต์
    """
    
    def __init__(self):
        # 🔴 BASE DIRECTORY (ที่อยู่ของโปรเจกต์)
        #    เช่น C:/Users/yourname/set-smart-ai-trader
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        
        # ============================================
        # 🔴🔴🔴 SET SMART API CONFIGURATION 🔴🔴🔴
        # ============================================
        # เอามาจาก .env: SETSMART_API_KEY
        # ถ้าไม่มี ให้ขึ้น Warning
        self.SETSMART_API_KEY = os.getenv("SETSMART_API_KEY")
        
        # เอามาจาก .env: SETSMART_BASE_URL
        # ถ้าไม่มี ให้ใช้ค่า default
        self.SETSMART_BASE_URL = os.getenv("SETSMART_BASE_URL", "https://api.setsmart.com")
        
        # ============================================
        # 🔴🔴🔴 LINE MESSAGING API CONFIGURATION 🔴🔴🔴
        # ============================================
        # เอามาจาก .env: LINE_CHANNEL_ACCESS_TOKEN
        # ดูวิธีขอได้ที่: https://developers.line.biz/console/
        self.LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        
        # เอามาจาก .env: LINE_USER_ID
        # User ID ของเรา (ขึ้นต้นด้วย U...)
        self.LINE_USER_ID = os.getenv("LINE_USER_ID")
        
        # ============================================
        # 🔴🔴🔴 DATABASE CONFIGURATION 🔴🔴🔴
        # ============================================
        # เอามาจาก .env: DB_PATH
        # ถ้าไม่มี ให้ใช้ค่า default: data/setsmart.db
        db_path = os.getenv("DB_PATH", "data/setsmart.db")
        self.DB_PATH = str(self.BASE_DIR / db_path)
        
        # ============================================
        # 🔴🔴🔴 ENVIRONMENT CONFIGURATION 🔴🔴🔴
        # ============================================
        # เอามาจาก .env: ENVIRONMENT
        # ถ้าไม่มี ให้ใช้ "development"
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        
        # ============================================
        # 🔴🔴🔴 TRADING CONFIGURATION (OPTIONAL) 🔴🔴🔴
        # ============================================
        # ค่าเริ่มต้นสำหรับการซื้อขาย (ถ้าต้องการตั้งค่า)
        self.DEFAULT_COMMISSION_RATE = 0.001  # 0.1%
        self.DEFAULT_SLIPPAGE = 0.001  # 0.1%
        self.DEFAULT_TAX_RATE = 0.0007  # 0.07% (ถ้ามี)
        
        # ============================================
        # 🔴🔴🔴 VALIDATE ALL CONFIGURATIONS 🔴🔴🔴
        # ============================================
        self.validate()
    
    def validate(self):
        """
        🔴 ตรวจสอบว่ามีค่าที่จำเป็นครบหรือไม่
        แสดง Warning ถ้าขาด แต่ไม่หยุดทำงาน (ยกเว้น production)
        """
        print("\n" + "="*50)
        print("🔍 กำลังตรวจสอบการตั้งค่า...")
        print("="*50)
        
        # 🔴 ตรวจสอบ SET SMART API Key
        if not self.SETSMART_API_KEY:
            print("❌ ไม่พบ SETSMART_API_KEY ในไฟล์ .env")
            print("   กรุณาใส่ API Key ที่ได้จาก SET SMART")
            print("   แก้ไขไฟล์ .env และใส่ค่าจริง")
        elif self.SETSMART_API_KEY == "YOUR_API_KEY_HERE":
            print("⚠️ SETSMART_API_KEY ยังเป็นค่าตัวอย่าง")
            print("   กรุณาเปลี่ยนเป็น API Key จริงใน .env")
        else:
            print("✅ SETSMART_API_KEY: พบแล้ว")
        
        # 🔴 ตรวจสอบ LINE Channel Access Token
        if not self.LINE_CHANNEL_ACCESS_TOKEN:
            print("⚠️ ไม่พบ LINE_CHANNEL_ACCESS_TOKEN ใน .env")
            print("   (ไม่เป็นไร ถ้าไม่ต้องการแจ้งเตือนทาง LINE)")
        elif self.LINE_CHANNEL_ACCESS_TOKEN == "YOUR_CHANNEL_ACCESS_TOKEN_HERE":
            print("⚠️ LINE_CHANNEL_ACCESS_TOKEN ยังเป็นค่าตัวอย่าง")
        else:
            print("✅ LINE_CHANNEL_ACCESS_TOKEN: พบแล้ว")
        
        # 🔴 ตรวจสอบ LINE User ID
        if not self.LINE_USER_ID:
            print("⚠️ ไม่พบ LINE_USER_ID ใน .env")
            print("   (ไม่เป็นไร ถ้าไม่ต้องการแจ้งเตือนทาง LINE)")
        elif self.LINE_USER_ID == "YOUR_USER_ID_HERE":
            print("⚠️ LINE_USER_ID ยังเป็นค่าตัวอย่าง")
        else:
            print("✅ LINE_USER_ID: พบแล้ว")
        
        # 🔴 ตรวจสอบ Environment
        print(f"🌍 Environment: {self.ENVIRONMENT}")
        
        # 🔴 ตรวจสอบ Database Path
        db_dir = os.path.dirname(self.DB_PATH)
        if not os.path.exists(db_dir):
            print(f"📁 จะสร้างโฟลเดอร์ฐานข้อมูล: {db_dir}")
        print(f"🗄️ Database: {self.DB_PATH}")
        
        print("="*50 + "\n")
        
        # 🔴 ถ้าเป็น production และไม่มี API Key ให้หยุดทำงาน
        if self.ENVIRONMENT == "production" and not self.SETSMART_API_KEY:
            raise ValueError("❌ production mode ต้องมี SETSMART_API_KEY")
    
    def is_development(self):
        """🔴 เช็คว่าเป็น development mode หรือไม่"""
        return self.ENVIRONMENT == "development"
    
    def is_production(self):
        """🔴 เช็คว่าเป็น production mode หรือไม่"""
        return self.ENVIRONMENT == "production"


# 🔴 สร้าง instance ของ settings ไว้ใช้ที่อื่นๆ
# เวลา import: from config.settings import settings
settings = Settings()
