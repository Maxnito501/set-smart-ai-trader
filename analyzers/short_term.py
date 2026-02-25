"""
📁 analyzers/short_term.py
วิเคราะห์หุ้นระยะสั้น (เล่นสั้น)
หา Volume Spike, NVDR Flow, Big Lot, สัญญาณซื้อขาย
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

from database.db_manager import DatabaseManager
from config.settings import settings


class ShortTermAnalyzer:
    """
    วิเคราะห์หุ้นระยะสั้น สำหรับเล่นสั้น 1-7 วัน
    
    วิธีใช้:
        analyzer = ShortTermAnalyzer()
        signals = analyzer.scan_all()
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        🔴 เริ่มต้น analyzer
        
        Args:
            db_manager: ตัวจัดการฐานข้อมูล (ถ้าไม่มี จะสร้างใหม่)
        """
        self.db = db_manager or DatabaseManager()
        print("✅ สร้าง ShortTermAnalyzer แล้ว")
    
    def close(self):
        """🔴 ปิดการเชื่อมต่อฐานข้อมูล"""
        self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ---------- ฟังก์ชันช่วยคำนวณ ----------
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        🔴 คำนวณ RSI (Relative Strength Index)
        
        Args:
            prices: รายการราคาปิด
            period: จำนวนวัน (ปกติ 14)
        
        Returns:
            ค่า RSI ล่าสุด (0-100)
        """
        if len(prices) < period + 1:
            return 50.0  # ค่ากลางถ้าข้อมูลไม่พอ
        
        # คำนวณ price change
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # แยก gain/loss
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        # ค่าเฉลี่ย
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def calculate_moving_average(self, prices: List[float], period: int) -> float:
        """🔴 คำนวณ Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        return sum(prices[-period:]) / period
    
    def calculate_volume_ratio(self, volumes: List[int], period: int = 20) -> float:
        """
        🔴 คำนวณ Volume Ratio (volume ล่าสุด / ค่าเฉลี่ย volume)
        
        Returns:
            > 2 = volume spike, > 3 = volume spike แรง
        """
        if len(volumes) < period + 1:
            return 1.0
        
        avg_volume = sum(volumes[-period-1:-1]) / period  # ไม่นับวันนี้
        current_volume = volumes[-1]
        
        if avg_volume == 0:
            return 1.0
        
        return round(current_volume / avg_volume, 2)
    
    # ---------- ฟังก์ชันวิเคราะห์หลัก ----------
    
    def analyze_volume_spike(self, symbol: str, days: int = 30) -> Dict:
        """
        🔴 วิเคราะห์ Volume Spike ของหุ้น
        
        Args:
            symbol: ชื่อหุ้น เช่น "SCC"
            days: จำนวนวันย้อนหลัง
        
        Returns:
            {
                "symbol": "SCC",
                "volume_ratio": 2.5,
                "is_spike": True,
                "avg_volume": 1000000,
                "current_volume": 2500000,
                "date": "2026-02-25"
            }
        """
        # ดึงข้อมูลราคา
        prices = self.db.get_prices(symbol, limit=days + 5)
        
        if len(prices) < 20:
            return {
                "symbol": symbol,
                "volume_ratio": 1.0,
                "is_spike": False,
                "avg_volume": 0,
                "current_volume": 0,
                "date": datetime.now().date().isoformat(),
                "error": "ข้อมูลไม่พอ"
            }
        
        # ดึง volumes
        volumes = [p["volume"] for p in prices]
        current_volume = volumes[0]  # ล่าสุด
        
        # คำนวณค่าเฉลี่ย 20 วัน (ไม่นับวันนี้)
        avg_volume = sum(volumes[1:21]) / 20
        
        if avg_volume == 0:
            volume_ratio = 1.0
        else:
            volume_ratio = current_volume / avg_volume
        
        return {
            "symbol": symbol,
            "volume_ratio": round(volume_ratio, 2),
            "is_spike": volume_ratio > 2.0,
            "is_strong_spike": volume_ratio > 3.0,
            "avg_volume": int(avg_volume),
            "current_volume": current_volume,
            "date": prices[0]["date"]
        }
    
    def analyze_nvdr_flow(self, symbol: str, days: int = 5) -> Dict:
        """
        🔴 วิเคราะห์ NVDR Flow (ต่างชาติซื้อขาย)
        
        Args:
            symbol: ชื่อหุ้น
            days: จำนวนวันย้อนหลัง
        
        Returns:
            {
                "symbol": "SCC",
                "net_total": 50000000,
                "is_buying": True,
                "consecutive_days": 3,
                "details": [...]
            }
        """
        nvdr_data = self.db.get_nvdr_summary(symbol, days)
        
        if len(nvdr_data) < 2:
            return {
                "symbol": symbol,
                "net_total": 0,
                "is_buying": False,
                "consecutive_days": 0,
                "details": nvdr_data
            }
        
        # คำนวณ net รวม
        net_total = sum([n["net"] for n in nvdr_data])
        
        # ดูว่าซื้อติดต่อกันกี่วัน
        consecutive_days = 0
        for n in nvdr_data:
            if n["net"] > 0:
                consecutive_days += 1
            else:
                break
        
        # 3 วันล่าสุดเป็นอย่างไร
        last_3_days = nvdr_data[:3]
        is_buying = all(n["net"] > 0 for n in last_3_days) if len(last_3_days) == 3 else False
        
        return {
            "symbol": symbol,
            "net_total": net_total,
            "is_buying": is_buying,
            "consecutive_days": consecutive_days,
            "last_net": nvdr_data[0]["net"] if nvdr_data else 0,
            "details": nvdr_data[:5]
        }
    
    def analyze_technical(self, symbol: str) -> Dict:
        """
        🔴 วิเคราะห์ทางเทคนิคเบื้องต้น
        
        Args:
            symbol: ชื่อหุ้น
        
        Returns:
            {
                "symbol": "SCC",
                "current_price": 228.0,
                "rsi": 65.2,
                "ma_5": 225.5,
                "ma_10": 223.0,
                "ma_20": 220.5,
                "is_above_ma": True,
                "is_overbought": False,
                "is_oversold": False
            }
        """
        prices = self.db.get_prices(symbol, limit=30)
        
        if len(prices) < 20:
            return {
                "symbol": symbol,
                "current_price": 0,
                "rsi": 50,
                "error": "ข้อมูลไม่พอ"
            }
        
        # เรียงจากล่าสุดไปเก่าสุด
        close_prices = [p["close"] for p in prices]
        current_price = close_prices[0]
        
        # คำนวณ RSI
        rsi = self.calculate_rsi(close_prices[::-1])  # เรียงจากเก่าไปใหม่
        
        # คำนวณ Moving Averages
        ma_5 = self.calculate_moving_average(close_prices[::-1], 5)
        ma_10 = self.calculate_moving_average(close_prices[::-1], 10)
        ma_20 = self.calculate_moving_average(close_prices[::-1], 20)
        
        # ตรวจสอบสภาวะ
        is_above_ma5 = current_price > ma_5
        is_above_ma10 = current_price > ma_10
        is_above_ma20 = current_price > ma_20
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "rsi": rsi,
            "ma_5": round(ma_5, 2),
            "ma_10": round(ma_10, 2),
            "ma_20": round(ma_20, 2),
            "is_above_ma5": is_above_ma5,
            "is_above_ma10": is_above_ma10,
            "is_above_ma20": is_above_ma20,
            "is_overbought": rsi > 70,
            "is_oversold": rsi < 30,
            "date": prices[0]["date"]
        }
    
    def scan_symbol(self, symbol: str) -> Dict:
        """
        🔴 วิเคราะห์หุ้นตัวเดียว ครอบคลุมทุกมุม
        
        Args:
            symbol: ชื่อหุ้น เช่น "SCC"
        
        Returns:
            ข้อมูลวิเคราะห์ครบถ้วน พร้อมสัญญาณ
        """
        result = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "signals": [],
            "score": 0,
            "max_score": 10,
            "recommendation": "HOLD"
        }
        
        # 🔴 1. วิเคราะห์ Volume
        volume_analysis = self.analyze_volume_spike(symbol)
        result["volume"] = volume_analysis
        if volume_analysis["is_strong_spike"]:
            result["signals"].append("VOLUME_STRONG_SPIKE")
            result["score"] += 3
        elif volume_analysis["is_spike"]:
            result["signals"].append("VOLUME_SPIKE")
            result["score"] += 2
        
        # 🔴 2. วิเคราะห์ NVDR
        nvdr_analysis = self.analyze_nvdr_flow(symbol)
        result["nvdr"] = nvdr_analysis
        if nvdr_analysis["is_buying"]:
            result["signals"].append("NVDR_BUYING")
            result["score"] += 3
        elif nvdr_analysis["consecutive_days"] >= 2:
            result["signals"].append("NVDR_ACCUMULATING")
            result["score"] += 2
        elif nvdr_analysis["net_total"] > 0:
            result["signals"].append("NVDR_POSITIVE")
            result["score"] += 1
        
        # 🔴 3. วิเคราะห์ Technical
        tech_analysis = self.analyze_technical(symbol)
        result["technical"] = tech_analysis
        if "error" not in tech_analysis:
            if tech_analysis["is_oversold"]:
                result["signals"].append("OVERSOLD")
                result["score"] += 2
            elif tech_analysis["is_above_ma5"] and tech_analysis["is_above_ma10"]:
                result["signals"].append("ABOVE_MA")
                result["score"] += 2
            elif tech_analysis["is_above_ma20"]:
                result["signals"].append("ABOVE_MA20")
                result["score"] += 1
        
        # 🔴 4. สรุปคะแนนและคำแนะนำ
        if result["score"] >= 7:
            result["recommendation"] = "STRONG_BUY"
        elif result["score"] >= 5:
            result["recommendation"] = "BUY"
        elif result["score"] >= 3:
            result["recommendation"] = "WATCH"
        else:
            result["recommendation"] = "HOLD"
        
        return result
    
    def scan_watchlist(self, symbols: List[str]) -> List[Dict]:
        """
        🔴 วิเคราะห์หุ้นหลายตัวใน watchlist
        
        Args:
            symbols: รายชื่อหุ้น เช่น ["SCC", "PTT", "ADVANC"]
        
        Returns:
            รายการวิเคราะห์ เรียงตามคะแนน
        """
        results = []
        
        for symbol in symbols:
            try:
                print(f"🔍 กำลังวิเคราะห์ {symbol}...")
                result = self.scan_symbol(symbol)
                results.append(result)
            except Exception as e:
                print(f"❌ วิเคราะห์ {symbol} ไม่สำเร็จ: {e}")
        
        # เรียงตามคะแนน จากมากไปน้อย
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    def scan_all(self, limit: int = 50) -> List[Dict]:
        """
        🔴 วิเคราะห์หุ้นทั้งหมดในฐานข้อมูล
        
        Args:
            limit: จำนวนหุ้นสูงสุดที่วิเคราะห์ (ป้องกันช้าเกินไป)
        
        Returns:
            รายการหุ้นที่น่าสนใจ เรียงตามคะแนน
        """
        # ดึงรายชื่อหุ้นทั้งหมด
        stocks = self.db.get_all_stocks()
        
        if not stocks:
            print("⚠️ ไม่มีข้อมูลหุ้นในฐานข้อมูล")
            return []
        
        # จำกัดจำนวน
        symbols = [s["symbol"] for s in stocks[:limit]]
        
        return self.scan_watchlist(symbols)
    
    def get_buy_signals(self, min_score: int = 5) -> List[Dict]:
        """
        🔴 ดึงเฉพาะสัญญาณซื้อ
        
        Args:
            min_score: คะแนนขั้นต่ำ (5 = BUY, 7 = STRONG_BUY)
        
        Returns:
            รายการหุ้นที่มีสัญญาณซื้อ
        """
        results = self.scan_all(limit=100)
        
        buy_signals = []
        for r in results:
            if r["score"] >= min_score:
                buy_signals.append(r)
                
                # บันทึกลงฐานข้อมูล
                try:
                    self.db.save_signal({
                        "symbol": r["symbol"],
                        "date": datetime.now().date().isoformat(),
                        "signal_type": "BUY" if r["score"] < 7 else "STRONG_BUY",
                        "strategy": "short_term",
                        "price": r.get("technical", {}).get("current_price", 0),
                        "target": r.get("technical", {}).get("current_price", 0) * 1.05,
                        "stop_loss": r.get("technical", {}).get("current_price", 0) * 0.95,
                        "reason": f"Score: {r['score']}, Signals: {r['signals']}"
                    })
                except:
                    pass
        
        return buy_signals
