"""
📁 analyzers/smart_money.py
อ่านเจ้ามือ วิเคราะห์พฤติกรรมรายใหญ่
ดู NVDR, Big Lot, Short Sales, Accumulation/Distribution
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import statistics

from database.db_manager import DatabaseManager
from config.settings import settings


class SmartMoneyAnalyzer:
    """
    วิเคราะห์พฤติกรรมรายใหญ่ (Smart Money)
    ติดตาม NVDR, Big Lot, Short Sales
    
    วิธีใช้:
        analyzer = SmartMoneyAnalyzer()
        big_moves = analyzer.detect_big_lot_accumulation()
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        🔴 เริ่มต้น analyzer
        
        Args:
            db_manager: ตัวจัดการฐานข้อมูล (ถ้าไม่มี จะสร้างใหม่)
        """
        self.db = db_manager or DatabaseManager()
        print("✅ สร้าง SmartMoneyAnalyzer แล้ว")
    
    def close(self):
        """🔴 ปิดการเชื่อมต่อฐานข้อมูล"""
        self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ---------- วิเคราะห์ NVDR (ต่างชาติ) ----------
    
    def analyze_nvdr_trend(self, symbol: str, days: int = 20) -> Dict:
        """
        🔴 วิเคราะห์แนวโน้ม NVDR รายหุ้น
        
        Args:
            symbol: ชื่อหุ้น
            days: จำนวนวันย้อนหลัง
        
        Returns:
            {
                "symbol": "SCC",
                "net_total": 150000000,
                "avg_daily_net": 7500000,
                "buy_days": 12,
                "sell_days": 8,
                "trend": "ACCUMULATING",
                "strength": "STRONG"
            }
        """
        nvdr_data = self.db.get_nvdr_summary(symbol, days)
        
        if len(nvdr_data) < 5:
            return {
                "symbol": symbol,
                "error": "ข้อมูล NVDR ไม่เพียงพอ"
            }
        
        # คำนวณยอดรวม
        net_total = sum([n["net"] for n in nvdr_data])
        buy_days = sum(1 for n in nvdr_data if n["net"] > 0)
        sell_days = sum(1 for n in nvdr_data if n["net"] < 0)
        
        # คำนวณค่าเฉลี่ย
        avg_daily_net = net_total / len(nvdr_data)
        
        # ดูแนวโน้ม 5 วันล่าสุด
        last_5_days = nvdr_data[:5]
        last_5_net = sum(n["net"] for n in last_5_days)
        
        # กำหนดแนวโน้ม
        if net_total > 0 and last_5_net > 0:
            if buy_days / len(nvdr_data) > 0.7:
                trend = "STRONG_ACCUMULATING"
                strength = "STRONG"
            else:
                trend = "ACCUMULATING"
                strength = "MEDIUM"
        elif net_total < 0 and last_5_net < 0:
            if sell_days / len(nvdr_data) > 0.7:
                trend = "STRONG_DISTRIBUTING"
                strength = "STRONG"
            else:
                trend = "DISTRIBUTING"
                strength = "MEDIUM"
        else:
            trend = "NEUTRAL"
            strength = "WEAK"
        
        # หาจุดเปลี่ยน (reversal)
        reversal = False
        if net_total < 0 and last_5_net > 0:
            reversal = "POSSIBLE_REVERSAL_BUY"
        elif net_total > 0 and last_5_net < 0:
            reversal = "POSSIBLE_REVERSAL_SELL"
        
        return {
            "symbol": symbol,
            "net_total": net_total,
            "avg_daily_net": round(avg_daily_net, 2),
            "buy_days": buy_days,
            "sell_days": sell_days,
            "buy_ratio": round(buy_days / len(nvdr_data) * 100, 2),
            "last_5_days_net": last_5_net,
            "trend": trend,
            "strength": strength,
            "reversal_signal": reversal,
            "data_points": len(nvdr_data)
        }
    
    def find_nvdr_accumulation(self, min_net: float = 50000000, days: int = 20) -> List[Dict]:
        """
        🔴 หาหุ้นที่ NVDR กำลังสะสม
        
        Args:
            min_net: ยอดซื้อสุทธิขั้นต่ำ (บาท)
            days: จำนวนวันย้อนหลัง
        
        Returns:
            รายการหุ้นที่ NVDR ซื้อสุทธิ
        """
        stocks = self.db.get_all_stocks()
        
        results = []
        
        for stock in stocks:
            symbol = stock["symbol"]
            
            try:
                analysis = self.analyze_nvdr_trend(symbol, days)
                
                if "error" in analysis:
                    continue
                
                if analysis["net_total"] > min_net and analysis["trend"] in ["ACCUMULATING", "STRONG_ACCUMULATING"]:
                    
                    # ดึงราคาปัจจุบัน
                    prices = self.db.get_prices(symbol, limit=1)
                    current_price = prices[0]["close"] if prices else 0
                    
                    results.append({
                        "symbol": symbol,
                        "name": stock.get("name_th", ""),
                        "net_total": analysis["net_total"],
                        "avg_daily_net": analysis["avg_daily_net"],
                        "buy_ratio": analysis["buy_ratio"],
                        "trend": analysis["trend"],
                        "strength": analysis["strength"],
                        "current_price": current_price,
                        "score": self._score_nvdr(analysis)
                    })
                    
            except Exception as e:
                continue
        
        # เรียงตามคะแนน
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    def _score_nvdr(self, analysis: Dict) -> float:
        """🔴 ให้คะแนน NVDR"""
        score = 0
        
        # คะแนนจาก net total
        net = analysis["net_total"]
        if net > 100_000_000:
            score += 5
        elif net > 50_000_000:
            score += 4
        elif net > 20_000_000:
            score += 3
        elif net > 10_000_000:
            score += 2
        elif net > 0:
            score += 1
        
        # คะแนนจาก buy ratio
        ratio = analysis["buy_ratio"]
        if ratio > 80:
            score += 3
        elif ratio > 70:
            score += 2
        elif ratio > 60:
            score += 1
        
        # คะแนนจาก trend
        if analysis["trend"] == "STRONG_ACCUMULATING":
            score += 3
        elif analysis["trend"] == "ACCUMULATING":
            score += 2
        
        return score
    
    # ---------- วิเคราะห์ Big Lot (รายการใหญ่) ----------
    
    def analyze_big_lot(self, symbol: str, days: int = 30) -> Dict:
        """
        🔴 วิเคราะห์ Big Lot รายหุ้น
        
        Args:
            symbol: ชื่อหุ้น
            days: จำนวนวันย้อนหลัง
        
        Returns:
            {
                "symbol": "SCC",
                "total_big_lot_buy": 1000000,
                "total_big_lot_sell": 500000,
                "net_big_lot": 500000,
                "transaction_count": 5,
                "avg_price": 227.5,
                "signal": "BIG_BUYING"
            }
        """
        # 🔴 ดึงข้อมูล Big Lot (ต้องมีตารางนี้ใน DB)
        # ถ้ายังไม่มี ให้จำลองข้อมูลหรือรอ API
        
        query = """
            SELECT * FROM big_lot 
            WHERE symbol = ? 
            ORDER BY date DESC, time DESC 
            LIMIT 100
        """
        big_lot_data = self.db.execute_query(query, (symbol,)) or []
        
        if not big_lot_data:
            return {
                "symbol": symbol,
                "error": "ไม่มีข้อมูล Big Lot"
            }
        
        # กรองตามจำนวนวัน
        cutoff_date = (datetime.now() - timedelta(days=days)).date()
        recent = [b for b in big_lot_data if datetime.strptime(b["date"], "%Y-%m-%d").date() >= cutoff_date]
        
        if not recent:
            return {
                "symbol": symbol,
                "error": f"ไม่มี Big Lot ใน {days} วัน"
            }
        
        # วิเคราะห์
        buy_trans = []
        sell_trans = []
        
        for b in recent:
            # 🔴 สมมติว่า big lot ที่ volume > 100000 และราคาสูง เป็น buy
            # จริงๆ ต้องดูจากข้อมูลว่ามี flag บอก buy/sell หรือไม่
            if b["volume"] > 100000 and b["price"] > 0:
                buy_trans.append(b)
            else:
                sell_trans.append(b)
        
        total_buy = sum(b["value"] for b in buy_trans) if buy_trans else 0
        total_sell = sum(b["value"] for b in sell_trans) if sell_trans else 0
        net = total_buy - total_sell
        
        # ราคาเฉลี่ย
        all_prices = [b["price"] for b in recent]
        avg_price = statistics.mean(all_prices) if all_prices else 0
        
        # สัญญาณ
        if net > 10_000_000:
            signal = "STRONG_BUYING"
        elif net > 1_000_000:
            signal = "BUYING"
        elif net < -10_000_000:
            signal = "STRONG_SELLING"
        elif net < -1_000_000:
            signal = "SELLING"
        else:
            signal = "NEUTRAL"
        
        return {
            "symbol": symbol,
            "total_buy": total_buy,
            "total_sell": total_sell,
            "net": net,
            "transaction_count": len(recent),
            "buy_count": len(buy_trans),
            "sell_count": len(sell_trans),
            "avg_price": round(avg_price, 2),
            "signal": signal,
            "days_analyzed": days
        }
    
    def find_big_lot_accumulation(self, min_net: float = 5_000_000) -> List[Dict]:
        """
        🔴 หาหุ้นที่มี Big Lot สะสม
        
        Args:
            min_net: ยอดซื้อสุทธิขั้นต่ำ
        
        Returns:
            รายการหุ้นที่รายใหญ่กำลังสะสม
        """
        stocks = self.db.get_all_stocks()
        
        results = []
        
        for stock in stocks[:50]:  # จำกัด 50 ตัวแรก
            symbol = stock["symbol"]
            
            try:
                analysis = self.analyze_big_lot(symbol, days=14)
                
                if "error" in analysis:
                    continue
                
                if analysis["net"] > min_net and analysis["signal"] in ["BUYING", "STRONG_BUYING"]:
                    
                    prices = self.db.get_prices(symbol, limit=1)
                    current_price = prices[0]["close"] if prices else 0
                    
                    results.append({
                        "symbol": symbol,
                        "name": stock.get("name_th", ""),
                        "net_big_lot": analysis["net"],
                        "avg_price": analysis["avg_price"],
                        "current_price": current_price,
                        "price_vs_avg": round((current_price - analysis["avg_price"]) / analysis["avg_price"] * 100, 2),
                        "transaction_count": analysis["transaction_count"],
                        "signal": analysis["signal"]
                    })
                    
            except Exception as e:
                continue
        
        results.sort(key=lambda x: x["net_big_lot"], reverse=True)
        
        return results
    
    # ---------- วิเคราะห์ Short Sales (ขายชอร์ต) ----------
    
    def analyze_short_sales(self, symbol: str, days: int = 30) -> Dict:
        """
        🔴 วิเคราะห์ Short Sales
        
        Args:
            symbol: ชื่อหุ้น
            days: จำนวนวันย้อนหลัง
        
        Returns:
            {
                "symbol": "SCC",
                "total_short": 1000000,
                "avg_daily_short": 33000,
                "short_trend": "DECREASING",
                "cover_signal": True
            }
        """
        # 🔴 ต้องมีข้อมูล Short Sales ใน DB
        # ถ้ายังไม่มี ให้จำลองหรือรอ API
        
        query = """
            SELECT * FROM short_sales 
            WHERE symbol = ? 
            ORDER BY date DESC 
            LIMIT 30
        """
        short_data = self.db.execute_query(query, (symbol,)) or []
        
        if not short_data:
            return {
                "symbol": symbol,
                "error": "ไม่มีข้อมูล Short Sales"
            }
        
        total_short = sum(s["volume"] for s in short_data)
        avg_short = total_short / len(short_data)
        
        # ดูแนวโน้ม
        last_week = short_data[:7]
        prev_week = short_data[7:14]
        
        last_week_avg = sum(s["volume"] for s in last_week) / len(last_week) if last_week else 0
        prev_week_avg = sum(s["volume"] for s in prev_week) / len(prev_week) if prev_week else 0
        
        if last_week_avg < prev_week_avg * 0.7:
            trend = "DECREASING (SHORT_COVERING)"
            cover_signal = True
        elif last_week_avg > prev_week_avg * 1.3:
            trend = "INCREASING (MORE_SHORT)"
            cover_signal = False
        else:
            trend = "STABLE"
            cover_signal = False
        
        return {
            "symbol": symbol,
            "total_short": total_short,
            "avg_daily_short": round(avg_short, 2),
            "last_week_avg": round(last_week_avg, 2),
            "prev_week_avg": round(prev_week_avg, 2),
            "trend": trend,
            "cover_signal": cover_signal,
            "data_points": len(short_data)
        }
    
    # ---------- วิเคราะห์ Accumulation/Distribution ----------
    
    def calculate_ad_line(self, symbol: str, days: int = 50) -> Dict:
        """
        🔴 คำนวณ Accumulation/Distribution Line
        
        Args:
            symbol: ชื่อหุ้น
            days: จำนวนวันย้อนหลัง
        
        Returns:
            {
                "symbol": "SCC",
                "ad_line": 1234567,
                "ad_trend": "UP",
                "money_flow": "POSITIVE",
                "signal": "ACCUMULATION"
            }
        """
        prices = self.db.get_prices(symbol, limit=days + 10)
        
        if len(prices) < 20:
            return {
                "symbol": symbol,
                "error": "ข้อมูลราคาไม่เพียงพอ"
            }
        
        # คำนวณ A/D Line
        ad_line = 0
        ad_values = []
        
        for i in range(len(prices) - 1, -1, -1):  # ย้อนจากเก่าไปใหม่
            p = prices[i]
            
            close = p["close"]
            low = p["low"]
            high = p["high"]
            volume = p["volume"]
            
            if high > low:
                mfv = ((close - low) - (high - close)) / (high - low) * volume
                ad_line += mfv
                ad_values.append(ad_line)
            else:
                ad_values.append(ad_line)
        
        # ดูแนวโน้ม A/D Line
        if len(ad_values) < 10:
            return {
                "symbol": symbol,
                "error": "คำนวณ A/D ไม่สำเร็จ"
            }
        
        # 5 วันล่าสุด
        recent_ad = ad_values[-5:]
        prev_ad = ad_values[-10:-5]
        
        if recent_ad[-1] > recent_ad[0] and recent_ad[-1] > prev_ad[-1]:
            ad_trend = "UP"
            signal = "ACCUMULATION"
        elif recent_ad[-1] < recent_ad[0] and recent_ad[-1] < prev_ad[-1]:
            ad_trend = "DOWN"
            signal = "DISTRIBUTION"
        else:
            ad_trend = "SIDEWAYS"
            signal = "NEUTRAL"
        
        # ราคาล่าสุด
        current_price = prices[0]["close"]
        
        # divergence (ราคาขึ้นแต่ A/D ลง = รายใหญ่แจก)
        divergence = None
        price_up = prices[0]["close"] > prices[5]["close"]
        ad_up = ad_values[-1] > ad_values[-6]
        
        if price_up and not ad_up:
            divergence = "BEARISH_DIVERGENCE (PRICE_UP_AD_DOWN)"
        elif not price_up and ad_up:
            divergence = "BULLISH_DIVERGENCE (PRICE_DOWN_AD_UP)"
        
        return {
            "symbol": symbol,
            "current_ad_line": ad_values[-1],
            "ad_trend": ad_trend,
            "signal": signal,
            "divergence": divergence,
            "current_price": current_price
        }
    
    # ---------- สรุปรวม ----------
    
    def analyze_smart_money(self, symbol: str) -> Dict:
        """
        🔴 วิเคราะห์พฤติกรรมรายใหญ่แบบครบวงจร
        
        Args:
            symbol: ชื่อหุ้น
        
        Returns:
            สรุปทุกมิติ
        """
        result = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "signals": [],
            "score": 0,
            "max_score": 10,
            "summary": {}
        }
        
        # 1. NVDR
        try:
            nvdr = self.analyze_nvdr_trend(symbol)
            if "error" not in nvdr:
                result["nvdr"] = nvdr
                if nvdr["trend"] in ["ACCUMULATING", "STRONG_ACCUMULATING"]:
                    result["signals"].append(f"NVDR_{nvdr['trend']}")
                    result["score"] += 3
                elif nvdr["trend"] in ["DISTRIBUTING", "STRONG_DISTRIBUTING"]:
                    result["signals"].append(f"NVDR_{nvdr['trend']}")
                    result["score"] -= 2
        except:
            pass
        
        # 2. Big Lot
        try:
            big_lot = self.analyze_big_lot(symbol)
            if "error" not in big_lot:
                result["big_lot"] = big_lot
                if big_lot["signal"] == "STRONG_BUYING":
                    result["signals"].append("BIG_LOT_STRONG_BUYING")
                    result["score"] += 4
                elif big_lot["signal"] == "BUYING":
                    result["signals"].append("BIG_LOT_BUYING")
                    result["score"] += 2
                elif big_lot["signal"] == "STRONG_SELLING":
                    result["signals"].append("BIG_LOT_STRONG_SELLING")
                    result["score"] -= 3
                elif big_lot["signal"] == "SELLING":
                    result["signals"].append("BIG_LOT_SELLING")
                    result["score"] -= 1
        except:
            pass
        
        # 3. Short Sales
        try:
            short = self.analyze_short_sales(symbol)
            if "error" not in short:
                result["short_sales"] = short
                if short.get("cover_signal"):
                    result["signals"].append("SHORT_COVERING")
                    result["score"] += 2
        except:
            pass
        
        # 4. A/D Line
        try:
            ad = self.calculate_ad_line(symbol)
            if "error" not in ad:
                result["ad_line"] = ad
                if ad["signal"] == "ACCUMULATION":
                    result["signals"].append("AD_ACCUMULATION")
                    result["score"] += 2
                elif ad["signal"] == "DISTRIBUTION":
                    result["signals"].append("AD_DISTRIBUTION")
                    result["score"] -= 2
                
                if ad.get("divergence"):
                    result["signals"].append(ad["divergence"])
                    if "BULLISH" in ad["divergence"]:
                        result["score"] += 3
                    elif "BEARISH" in ad["divergence"]:
                        result["score"] -= 3
        except:
            pass
        
        # สรุป
        if result["score"] >= 5:
            result["recommendation"] = "STRONG_BULLISH (รายใหญ่กำลังเก็บ)"
        elif result["score"] >= 2:
            result["recommendation"] = "BULLISH (รายใหญ่เริ่มเก็บ)"
        elif result["score"] <= -5:
            result["recommendation"] = "STRONG_BEARISH (รายใหญ่กำลังทิ้ง)"
        elif result["score"] <= -2:
            result["recommendation"] = "BEARISH (รายใหญ่เริ่มทิ้ง)"
        else:
            result["recommendation"] = "NEUTRAL (รายใหญ่ยังไม่ชัด)"
        
        return result
    
    def scan_all_smart_money(self, limit: int = 50) -> List[Dict]:
        """
        🔴 สแกนหุ้นทั้งหมดเพื่อหาพฤติกรรมรายใหญ่
        
        Args:
            limit: จำนวนหุ้นสูงสุด
        
        Returns:
            รายการหุ้นที่รายใหญ่สนใจ
        """
        stocks = self.db.get_all_stocks()
        
        if not stocks:
            return []
        
        results = []
        
        for stock in stocks[:limit]:
            symbol = stock["symbol"]
            
            try:
                analysis = self.analyze_smart_money(symbol)
                
                if analysis["score"] != 0:  # เฉพาะที่มีสัญญาณ
                    results.append({
                        "symbol": symbol,
                        "name": stock.get("name_th", ""),
                        "score": analysis["score"],
                        "recommendation": analysis.get("recommendation", ""),
                        "signals": analysis["signals"],
                        "nvdr_trend": analysis.get("nvdr", {}).get("trend", ""),
                        "big_lot_signal": analysis.get("big_lot", {}).get("signal", "")
                    })
                    
            except Exception as e:
                continue
        
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
