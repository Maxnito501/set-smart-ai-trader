"""
📁 api/client.py
ตัวจัดการการเชื่อมต่อกับ SET SMART API
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, date

from config.settings import settings


class SetSmartClient:
    """
    คลาสหลักสำหรับเรียกใช้ SET SMART API
    
    วิธีใช้:
        client = SetSmartClient()
        data = client.get_securities()
    """
    
    def __init__(self):
        """🔴 ตั้งค่าการเชื่อมต่อ API"""
        self.api_key = settings.SETSMART_API_KEY
        self.base_url = settings.SETSMART_BASE_URL
        self.timeout = 30  # รอ response ไม่เกิน 30 วินาที
        
        # 🔴 ตรวจสอบ API Key
        self._check_api_key()
        
        # 🔴 headers ที่ต้องส่งไปกับทุก request
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "SET-SMART-AI-TRADER/1.0"
        }
        
        print(f"✅ สร้าง API Client แล้ว: {self.base_url}")
    
    def _check_api_key(self):
        """🔴 ตรวจสอบ API Key ว่าถูกต้องหรือไม่"""
        if not self.api_key:
            raise ValueError("""
            ❌ ไม่พบ SETSMART_API_KEY ในไฟล์ .env
            
            กรุณาทำตามขั้นตอน:
            1. สมัครสมาชิก SET SMART (เสียเงินเอง)
            2. ขอ API Key จาก SET SMART
            3. Copy .env.example เป็น .env
            4. ใส่ API Key ของตัวเองใน .env
            
            ดูรายละเอียดใน README.md
            """)
        
        if self.api_key == "YOUR_API_KEY_HERE":
            raise ValueError("""
            ❌ กรุณาใส่ API Key จริงใน .env
            
            ตอนนี้กำลังใช้: YOUR_API_KEY_HERE
            """)
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        🔴 ฟังก์ชันภายในสำหรับเรียก API
        
        Args:
            endpoint: เช่น "/securities", "/historical/SCC"
            params: พารามิเตอร์เพิ่มเติม (เช่น {"limit": 100})
        
        Returns:
            ข้อมูล JSON จาก API
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            print(f"📡 กำลังเรียก: {url}")
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            
            # 🔴 ตรวจสอบสถานะ HTTP
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise Exception("❌ API Key ไม่ถูกต้อง หรือหมดอายุ")
            elif response.status_code == 403:
                raise Exception("❌ ไม่มีสิทธิ์เข้าถึงข้อมูลนี้")
            elif response.status_code == 404:
                raise Exception(f"❌ ไม่พบ endpoint: {endpoint}")
            elif response.status_code == 429:
                raise Exception("❌ เรียก API บ่อยเกินไป (Rate limit)")
            else:
                raise Exception(f"❌ HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            raise Exception(f"❌ ไม่สามารถเชื่อมต่อ {self.base_url} ได้")
        except requests.exceptions.Timeout:
            raise Exception(f"❌ รอ response นานเกิน {self.timeout} วินาที")
        except Exception as e:
            raise Exception(f"❌ เกิดข้อผิดพลาด: {e}")
    
    def test_connection(self) -> bool:
        """
        🔴 ทดสอบว่าเชื่อมต่อ API ได้หรือไม่
        
        Returns:
            True ถ้าเชื่อมต่อได้, False ถ้าไม่ได้
        """
        try:
            # 🔴 ต้องเปลี่ยน endpoint ตามที่ SET SMART ให้มาจริงๆ
            # อาจจะเป็น /ping, /status, หรือ /securities?limit=1
            data = self._make_request("/🔴ใส่ endpoint สำหรับทดสอบ")
            print("✅ เชื่อมต่อ API สำเร็จ")
            return True
        except Exception as e:
            print(f"❌ เชื่อมต่อไม่ได้: {e}")
            return False
    
    def get_securities(self, limit: int = 1000, offset: int = 0) -> List[Dict]:
        """
        🔴 ดึงรายชื่อหลักทรัพย์ทั้งหมด
        
        Args:
            limit: จำนวนที่ต้องการต่อครั้ง
            offset: เริ่มต้นที่
        
        Returns:
            รายชื่อหุ้นทั้งหมด
        """
        endpoint = "/🔴[securities หรือ endpoint สำหรับดึงรายชื่อหุ้น]"
        params = {
            "🔴[limit]": limit,
            "🔴[offset]": offset
        }
        
        data = self._make_request(endpoint, params)
        return data.get("🔴[data]", [])  # ปรับตาม structure จริง
    
    def get_stock_info(self, symbol: str) -> Dict:
        """
        🔴 ดึงข้อมูลรายบริษัท
        
        Args:
            symbol: เช่น "SCC", "PTT", "ADVANC"
        
        Returns:
            ข้อมูลบริษัท
        """
        endpoint = f"/🔴[securities]/{symbol}"
        return self._make_request(endpoint)
    
    def get_historical_prices(
        self, 
        symbol: str, 
        from_date: date, 
        to_date: date
    ) -> List[Dict]:
        """
        🔴 ดึงราคาย้อนหลัง
        
        Args:
            symbol: เช่น "SCC"
            from_date: วันที่เริ่มต้น (YYYY-MM-DD)
            to_date: วันที่สิ้นสุด (YYYY-MM-DD)
        
        Returns:
            ราคาย้อนหลังรายวัน
        """
        endpoint = f"/🔴[historical]/{symbol}"
        params = {
            "🔴[from]": from_date.isoformat(),
            "🔴[to]": to_date.isoformat()
        }
        
        data = self._make_request(endpoint, params)
        return data.get("🔴[prices]", [])
    
    def get_financials(self, symbol: str, year: Optional[int] = None) -> List[Dict]:
        """
        🔴 ดึงงบการเงิน
        
        Args:
            symbol: เช่น "SCC"
            year: ปีที่ต้องการ (ถ้าไม่ใส่ ได้ทั้งหมด)
        
        Returns:
            งบการเงิน
        """
        endpoint = f"/🔴[financials]/{symbol}"
        params = {}
        if year:
            params["🔴[year]"] = year
        
        data = self._make_request(endpoint, params)
        return data.get("🔴[financials]", [])
    
    def get_nvdr_flow(self, symbol: str, days: int = 30) -> List[Dict]:
        """
        🔴 ดึงข้อมูล NVDR (ต่างชาติซื้อขาย)
        
        Args:
            symbol: เช่น "SCC"
            days: จำนวนวันย้อนหลัง
        
        Returns:
            NVDR flow รายวัน
        """
        endpoint = f"/🔴[nvdr]/{symbol}"
        params = {
            "🔴[days]": days
        }
        
        data = self._make_request(endpoint, params)
        return data.get("🔴[data]", [])
    
    def get_big_lot(self, symbol: str, days: int = 7) -> List[Dict]:
        """
        🔴 ดึงข้อมูล Big Lot (รายการใหญ่)
        
        Args:
            symbol: เช่น "SCC"
            days: จำนวนวันย้อนหลัง
        
        Returns:
            Big Lot transactions
        """
        endpoint = f"/🔴[biglot]/{symbol}"
        params = {
            "🔴[days]": days
        }
        
        data = self._make_request(endpoint, params)
        return data.get("🔴[transactions]", [])
    
    def get_dividend_calendar(self, from_date: date, to_date: date) -> List[Dict]:
        """
        🔴 ดึงปฏิทินปันผล (XD)
        
        Args:
            from_date: วันที่เริ่มต้น
            to_date: วันที่สิ้นสุด
        
        Returns:
            รายการหุ้นขึ้น XD
        """
        endpoint = "/🔴[dividend/calendar]"
        params = {
            "🔴[from]": from_date.isoformat(),
            "🔴[to]": to_date.isoformat()
        }
        
        data = self._make_request(endpoint, params)
        return data.get("🔴[data]", [])
