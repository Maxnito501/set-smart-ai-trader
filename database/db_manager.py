"""
📁 database/db_manager.py
จัดการฐานข้อมูล SQLite สำหรับเก็บข้อมูลหุ้น
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path

from config.settings import settings


class DatabaseManager:
    """
    จัดการการเชื่อมต่อและคำสั่งต่างๆ กับฐานข้อมูล SQLite
    
    วิธีใช้:
        db = DatabaseManager()
        db.create_tables()
        db.insert_stock({"symbol": "SCC", "name": "ปูนซิเมนต์ไทย"})
        stocks = db.get_all_stocks()
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        🔴 เริ่มต้นการเชื่อมต่อฐานข้อมูล
        
        Args:
            db_path: ตำแหน่งไฟล์ฐานข้อมูล (ถ้าไม่ใส่ ใช้จาก settings)
        """
        # 🔴 ใช้ db_path จาก settings ถ้าไม่ระบุ
        self.db_path = db_path or settings.DB_PATH
        
        # 🔴 สร้างโฟลเดอร์ data ถ้ายังไม่มี
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 🔴 เชื่อมต่อฐานข้อมูล
        self.conn = None
        self.cursor = None
        self.connect()
        
        print(f"✅ เชื่อมต่อฐานข้อมูล: {self.db_path}")
    
    def connect(self):
        """🔴 เชื่อมต่อกับฐานข้อมูล"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # ให้ผลลัพธ์เป็น dict-like
            self.cursor = self.conn.cursor()
            
            # 🔴 เปิดใช้ foreign keys
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
        except sqlite3.Error as e:
            print(f"❌ ไม่สามารถเชื่อมต่อฐานข้อมูล: {e}")
            raise
    
    def close(self):
        """🔴 ปิดการเชื่อมต่อฐานข้อมูล"""
        if self.conn:
            self.conn.close()
            print("✅ ปิดการเชื่อมต่อฐานข้อมูล")
    
    def __enter__(self):
        """ใช้กับ context manager (with)"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """ปิด connection อัตโนมัติเมื่อออกจาก with"""
        self.close()
    
    def execute_query(self, query: str, params: Tuple = ()) -> Optional[List[Dict]]:
        """
        🔴 รันคำสั่ง SQL และคืนผลลัพธ์
        
        Args:
            query: คำสั่ง SQL
            params: พารามิเตอร์ (สำหรับป้องกัน SQL injection)
        
        Returns:
            รายการข้อมูล (สำหรับ SELECT) หรือ None (สำหรับ INSERT/UPDATE/DELETE)
        """
        try:
            self.cursor.execute(query, params)
            
            # ถ้าเป็น SELECT ให้คืนค่า
            if query.strip().upper().startswith("SELECT"):
                rows = self.cursor.fetchall()
                return [dict(row) for row in rows]
            
            # ถ้าเป็น INSERT/UPDATE/DELETE ให้ commit
            self.conn.commit()
            return None
            
        except sqlite3.Error as e:
            print(f"❌ SQL Error: {e}")
            print(f"   Query: {query}")
            print(f"   Params: {params}")
            self.conn.rollback()
            raise
    
    def create_tables(self):
        """🔴 สร้างตารางต่างๆ ในฐานข้อมูล (ถ้ายังไม่มี)"""
        
        # 🔴 ตารางหุ้น (stocks)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS stocks (
                symbol TEXT PRIMARY KEY,
                name_th TEXT,
                name_en TEXT,
                sector TEXT,
                industry TEXT,
                market TEXT,
                last_updated TIMESTAMP
            )
        """)
        
        # 🔴 ตารางราคารายวัน (daily_prices)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS daily_prices (
                symbol TEXT,
                date DATE,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                value REAL,
                PRIMARY KEY (symbol, date),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        """)
        
        # 🔴 ตารางงบการเงิน (financials)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS financials (
                symbol TEXT,
                year INTEGER,
                quarter INTEGER,
                revenue REAL,
                net_profit REAL,
                eps REAL,
                roe REAL,
                pe REAL,
                pbv REAL,
                dividend_yield REAL,
                PRIMARY KEY (symbol, year, quarter),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        """)
        
        # 🔴 ตาราง NVDR (nvdr_flow)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS nvdr_flow (
                symbol TEXT,
                date DATE,
                buy REAL,
                sell REAL,
                net REAL,
                PRIMARY KEY (symbol, date),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        """)
        
        # 🔴 ตาราง Big Lot (big_lot)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS big_lot (
                symbol TEXT,
                date DATE,
                time TIME,
                price REAL,
                volume INTEGER,
                value REAL,
                PRIMARY KEY (symbol, date, time),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        """)
        
        # 🔴 ตารางปันผล (dividends)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS dividends (
                symbol TEXT,
                xd_date DATE,
                dividend_per_share REAL,
                payment_date DATE,
                year INTEGER,
                PRIMARY KEY (symbol, xd_date),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        """)
        
        # 🔴 ตารางสัญญาณซื้อขาย (signals)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS signals (
                symbol TEXT,
                date DATE,
                signal_type TEXT,
                strategy TEXT,
                price REAL,
                target REAL,
                stop_loss REAL,
                reason TEXT,
                PRIMARY KEY (symbol, date, strategy),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        """)
        
        print("✅ สร้างตารางเรียบร้อย")
    
    # ---------- CRUD สำหรับตาราง stocks ----------
    
    def insert_stock(self, stock_data: Dict) -> bool:
        """
        🔴 เพิ่มข้อมูลหุ้น
        
        Args:
            stock_data: {
                "symbol": "SCC",
                "name_th": "ปูนซิเมนต์ไทย",
                "name_en": "Siam Cement",
                "sector": "Construction Materials",
                "industry": "Construction",
                "market": "SET"
            }
        """
        query = """
            INSERT OR REPLACE INTO stocks 
            (symbol, name_th, name_en, sector, industry, market, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            stock_data.get("symbol"),
            stock_data.get("name_th"),
            stock_data.get("name_en"),
            stock_data.get("sector"),
            stock_data.get("industry"),
            stock_data.get("market"),
            datetime.now()
        )
        self.execute_query(query, params)
        return True
    
    def get_stock(self, symbol: str) -> Optional[Dict]:
        """🔴 ดึงข้อมูลหุ้นรายตัว"""
        result = self.execute_query(
            "SELECT * FROM stocks WHERE symbol = ?", 
            (symbol,)
        )
        return result[0] if result else None
    
    def get_all_stocks(self) -> List[Dict]:
        """🔴 ดึงข้อมูลหุ้นทั้งหมด"""
        return self.execute_query(
            "SELECT * FROM stocks ORDER BY symbol"
        ) or []
    
    # ---------- CRUD สำหรับตาราง daily_prices ----------
    
    def insert_daily_price(self, price_data: Dict) -> bool:
        """
        🔴 เพิ่มราคารายวัน
        
        Args:
            price_data: {
                "symbol": "SCC",
                "date": "2026-02-25",
                "open": 227.0,
                "high": 229.0,
                "low": 226.0,
                "close": 228.0,
                "volume": 8244564,
                "value": 1864937060
            }
        """
        query = """
            INSERT OR REPLACE INTO daily_prices 
            (symbol, date, open, high, low, close, volume, value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            price_data.get("symbol"),
            price_data.get("date"),
            price_data.get("open"),
            price_data.get("high"),
            price_data.get("low"),
            price_data.get("close"),
            price_data.get("volume"),
            price_data.get("value")
        )
        self.execute_query(query, params)
        return True
    
    def get_prices(self, symbol: str, limit: int = 100) -> List[Dict]:
        """🔴 ดึงราคาย้อนหลังของหุ้น"""
        return self.execute_query("""
            SELECT * FROM daily_prices 
            WHERE symbol = ? 
            ORDER BY date DESC 
            LIMIT ?
        """, (symbol, limit)) or []
    
    # ---------- CRUD สำหรับตาราง nvdr_flow ----------
    
    def insert_nvdr(self, nvdr_data: Dict) -> bool:
        """
        🔴 เพิ่มข้อมูล NVDR
        
        Args:
            nvdr_data: {
                "symbol": "SCC",
                "date": "2026-02-25",
                "buy": 120000000,
                "sell": 80000000,
                "net": 40000000
            }
        """
        query = """
            INSERT OR REPLACE INTO nvdr_flow 
            (symbol, date, buy, sell, net)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            nvdr_data.get("symbol"),
            nvdr_data.get("date"),
            nvdr_data.get("buy"),
            nvdr_data.get("sell"),
            nvdr_data.get("net")
        )
        self.execute_query(query, params)
        return True
    
    def get_nvdr_summary(self, symbol: str, days: int = 30) -> List[Dict]:
        """🔴 ดึงสรุป NVDR ย้อนหลัง"""
        return self.execute_query("""
            SELECT * FROM nvdr_flow 
            WHERE symbol = ? 
            ORDER BY date DESC 
            LIMIT ?
        """, (symbol, days)) or []
    
    # ---------- สำหรับสัญญาณซื้อขาย ----------
    
    def save_signal(self, signal_data: Dict) -> bool:
        """
        🔴 บันทึกสัญญาณซื้อขาย
        
        Args:
            signal_data: {
                "symbol": "SCC",
                "date": "2026-02-25",
                "signal_type": "BUY",
                "strategy": "short_volume",
                "price": 228.0,
                "target": 232.0,
                "stop_loss": 224.0,
                "reason": "Volume spike + NVDR buy"
            }
        """
        query = """
            INSERT OR REPLACE INTO signals 
            (symbol, date, signal_type, strategy, price, target, stop_loss, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            signal_data.get("symbol"),
            signal_data.get("date"),
            signal_data.get("signal_type"),
            signal_data.get("strategy"),
            signal_data.get("price"),
            signal_data.get("target"),
            signal_data.get("stop_loss"),
            signal_data.get("reason")
        )
        self.execute_query(query, params)
        return True
    
    def get_today_signals(self) -> List[Dict]:
        """🔴 ดึงสัญญาณซื้อขายของวันนี้"""
        today = datetime.now().date().isoformat()
        return self.execute_query("""
            SELECT * FROM signals 
            WHERE date = ? 
            ORDER BY symbol
        """, (today,)) or []
