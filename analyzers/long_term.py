"""
📁 analyzers/long_term.py
วิเคราะห์หุ้นระยะยาว (เล่นยาว, ปันผล, DCA)
คัดกรองหุ้นปันผลดี พื้นฐานแกร่ง หาจังหวะสะสม
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import statistics

from database.db_manager import DatabaseManager
from config.settings import settings


class LongTermAnalyzer:
    """
    วิเคราะห์หุ้นระยะยาว สำหรับถือยาว 3 เดือนขึ้นไป
    เน้นปันผล พื้นฐาน DCA
    
    วิธีใช้:
        analyzer = LongTermAnalyzer()
        stocks = analyzer.screen_high_dividend()
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        🔴 เริ่มต้น analyzer
        
        Args:
            db_manager: ตัวจัดการฐานข้อมูล (ถ้าไม่มี จะสร้างใหม่)
        """
        self.db = db_manager or DatabaseManager()
        print("✅ สร้าง LongTermAnalyzer แล้ว")
    
    def close(self):
        """🔴 ปิดการเชื่อมต่อฐานข้อมูล"""
        self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ---------- ฟังก์ชันช่วยคำนวณ ----------
    
    def calculate_dividend_yield(self, price: float, dividend: float) -> float:
        """🔴 คำนวณ Dividend Yield (%)"""
        if price <= 0:
            return 0
        return round((dividend / price) * 100, 2)
    
    def calculate_pe_ratio(self, price: float, eps: float) -> float:
        """🔴 คำนวณ P/E Ratio"""
        if eps <= 0:
            return 0
        return round(price / eps, 2)
    
    def calculate_roe(self, net_profit: float, equity: float) -> float:
        """🔴 คำนวณ ROE (%)"""
        if equity <= 0:
            return 0
        return round((net_profit / equity) * 100, 2)
    
    # ---------- ฟังก์ชันคัดกรอง ----------
    
    def screen_high_dividend(self, 
                            min_yield: float = 4.0,
                            min_years: int = 5,
                            min_roe: float = 10.0,
                            max_de: float = 1.5) -> List[Dict]:
        """
        🔴 คัดกรองหุ้นปันผลสูง
        
        Args:
            min_yield: Dividend Yield ขั้นต่ำ (%)
            min_years: จำนวนปีที่จ่ายปันผลต่อเนื่อง
            min_roe: ROE ขั้นต่ำ (%)
            max_de: D/E Ratio สูงสุด
        
        Returns:
            รายการหุ้นที่ผ่านเกณฑ์
        """
        # ดึงรายชื่อหุ้นทั้งหมด
        stocks = self.db.get_all_stocks()
        
        if not stocks:
            print("⚠️ ไม่มีข้อมูลหุ้นในฐานข้อมูล")
            return []
        
        results = []
        
        for stock in stocks:
            symbol = stock["symbol"]
            
            try:
                # 🔴 ดึงข้อมูลปันผล
                div_query = """
                    SELECT * FROM dividends 
                    WHERE symbol = ? 
                    ORDER BY xd_date DESC
                """
                dividends = self.db.execute_query(div_query, (symbol,)) or []
                
                if len(dividends) < min_years:
                    continue
                
                # คำนวณปันผลเฉลี่ยย้อนหลัง
                div_yields = []
                for d in dividends[:min_years]:
                    # หาราคา ณ ช่วงนั้น
                    price_query = """
                        SELECT close FROM daily_prices 
                        WHERE symbol = ? AND date <= ? 
                        ORDER BY date DESC LIMIT 1
                    """
                    price_data = self.db.execute_query(price_query, (symbol, d["xd_date"]))
                    
                    if price_data:
                        price = price_data[0]["close"]
                        div_yield = self.calculate_dividend_yield(price, d["dividend_per_share"])
                        div_yields.append(div_yield)
                
                if not div_yields:
                    continue
                
                avg_yield = statistics.mean(div_yields)
                
                # ตรวจสอบเกณฑ์ขั้นต่ำ
                if avg_yield < min_yield:
                    continue
                
                # 🔴 ดึงข้อมูลการเงินล่าสุด
                fin_query = """
                    SELECT * FROM financials 
                    WHERE symbol = ? 
                    ORDER BY year DESC, quarter DESC LIMIT 1
                """
                fin_data = self.db.execute_query(fin_query, (symbol,))
                
                roe = 0
                de = 0
                if fin_data:
                    roe = fin_data[0].get("roe", 0) or 0
                    # ถ้ามี D/E ในข้อมูล
                
                # ตรวจสอบ ROE
                if roe < min_roe:
                    continue
                
                # 🔴 ราคาปัจจุบัน
                price_data = self.db.get_prices(symbol, limit=1)
                current_price = price_data[0]["close"] if price_data else 0
                
                # 🔴 คำนวณ Dividend Yield ปัจจุบัน
                last_dividend = dividends[0]["dividend_per_share"] if dividends else 0
                current_yield = self.calculate_dividend_yield(current_price, last_dividend)
                
                results.append({
                    "symbol": symbol,
                    "name": stock.get("name_th", ""),
                    "sector": stock.get("sector", ""),
                    "avg_dividend_yield_5y": round(avg_yield, 2),
                    "current_dividend_yield": current_yield,
                    "last_dividend": last_dividend,
                    "current_price": current_price,
                    "roe": round(roe, 2),
                    "dividend_years": len(dividends),
                    "score": self._calculate_long_score(avg_yield, current_yield, roe)
                })
                
            except Exception as e:
                print(f"⚠️ วิเคราะห์ {symbol} ไม่สำเร็จ: {e}")
                continue
        
        # เรียงตามคะแนน
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    def _calculate_long_score(self, avg_yield: float, current_yield: float, roe: float) -> float:
        """🔴 คำนวณคะแนนสำหรับหุ้นยาว"""
        score = 0
        
        # คะแนนจากปันผล (สูงสุด 5)
        if avg_yield >= 7:
            score += 5
        elif avg_yield >= 5:
            score += 4
        elif avg_yield >= 4:
            score += 3
        elif avg_yield >= 3:
            score += 2
        else:
            score += 1
        
        # คะแนนจาก ROE (สูงสุด 3)
        if roe >= 20:
            score += 3
        elif roe >= 15:
            score += 2
        elif roe >= 10:
            score += 1
        
        # คะแนนจากโอกาสซื้อ (ปัจจุบัน yield สูงกว่าค่าเฉลี่ย)
        if current_yield > avg_yield * 1.2:
            score += 2  # ซื้อได้ถูกกว่าปกติ
        elif current_yield > avg_yield:
            score += 1  # ราคาปกติ
        
        return round(score, 1)
    
    def find_dca_opportunities(self, 
                              budget_per_month: float = 10000,
                              min_yield: float = 4.0) -> List[Dict]:
        """
        🔴 หาจังหวะ DCA (Dollar Cost Averaging)
        
        Args:
            budget_per_month: งบประมาณต่อเดือน
            min_yield: Dividend Yield ขั้นต่ำ
        
        Returns:
            รายการหุ้นที่เหมาะกับ DCA พร้อมแผน
        """
        # คัดกรองหุ้นปันผลดีก่อน
        good_stocks = self.screen_high_dividend(min_yield=min_yield)
        
        if not good_stocks:
            return []
        
        results = []
        
        for stock in good_stocks[:10]:  # ดูแค่ 10 ตัวแรก
            symbol = stock["symbol"]
            current_price = stock["current_price"]
            
            if current_price <= 0:
                continue
            
            # 🔴 คำนวณจำนวนหุ้นที่ซื้อได้ต่อเดือน
            shares_per_month = int(budget_per_month / current_price)
            
            # 🔴 คำนวณ DCA 12 เดือน
            yearly_investment = budget_per_month * 12
            total_shares = shares_per_month * 12
            
            # 🔴 คำนวณปันผลที่คาดว่าจะได้
            last_dividend = stock["last_dividend"]
            expected_annual_dividend = last_dividend * total_shares
            
            results.append({
                "symbol": symbol,
                "name": stock["name"],
                "current_price": current_price,
                "dividend_yield": stock["current_dividend_yield"],
                "budget_per_month": budget_per_month,
                "shares_per_month": shares_per_month,
                "yearly_investment": yearly_investment,
                "total_shares_year": total_shares,
                "expected_annual_dividend": round(expected_annual_dividend, 2),
                "effective_yield": round((expected_annual_dividend / yearly_investment) * 100, 2),
                "score": stock["score"]
            })
        
        return results
    
    def analyze_xd_timing(self, symbol: str) -> Dict:
        """
        🔴 วิเคราะห์จังหวะซื้อก่อน/หลัง XD
        
        Args:
            symbol: ชื่อหุ้น
        
        Returns:
            ข้อมูล XD และคำแนะนำ
        """
        # ดึงข้อมูลปันผล
        div_query = """
            SELECT * FROM dividends 
            WHERE symbol = ? 
            ORDER BY xd_date DESC
        """
        dividends = self.db.execute_query(div_query, (symbol,)) or []
        
        if len(dividends) < 2:
            return {
                "symbol": symbol,
                "error": "ข้อมูลปันผลไม่พอ"
            }
        
        # ราคาปัจจุบัน
        prices = self.db.get_prices(symbol, limit=30)
        if not prices:
            return {
                "symbol": symbol,
                "error": "ไม่มีข้อมูลราคา"
            }
        
        current_price = prices[0]["close"]
        
        # วิเคราะห์พฤติกรรมราคาก่อน XD
        xd_dates = [d["xd_date"] for d in dividends[:3]]
        price_patterns = []
        
        for xd_date in xd_dates:
            # หาราคา 5 วันก่อน XD
            query = """
                SELECT date, close FROM daily_prices 
                WHERE symbol = ? AND date <= ? 
                ORDER BY date DESC LIMIT 10
            """
            pre_xd_prices = self.db.execute_query(query, (symbol, xd_date))
            
            if pre_xd_prices and len(pre_xd_prices) >= 5:
                price_5d_before = pre_xd_prices[-1]["close"]  # 5 วันก่อน
                price_1d_before = pre_xd_prices[0]["close"]   # 1 วันก่อน
                
                change = ((price_1d_before - price_5d_before) / price_5d_before) * 100
                price_patterns.append(change)
        
        # ค่าเฉลี่ยการขึ้นก่อน XD
        avg_pre_xd_rise = statistics.mean(price_patterns) if price_patterns else 0
        
        # คำนวณปันผลครั้งล่าสุด
        last_dividend = dividends[0]["dividend_per_share"]
        current_yield = self.calculate_dividend_yield(current_price, last_dividend)
        
        # คำแนะนำ
        recommendation = "HOLD"
        reason = ""
        
        if avg_pre_xd_rise > 3:
            recommendation = "BUY_BEFORE_XD"
            reason = f"ราคามักขึ้นก่อน XD เฉลี่ย {round(avg_pre_xd_rise, 2)}%"
        elif current_yield > 5:
            recommendation = "BUY_NOW"
            reason = f"ปันผลสูง {current_yield}%"
        else:
            recommendation = "WAIT_AFTER_XD"
            reason = "รอซื้อหลัง XD ราคาอาจลง"
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "last_dividend": last_dividend,
            "current_yield": current_yield,
            "next_xd_date": dividends[0]["xd_date"] if dividends else None,
            "avg_pre_xd_rise": round(avg_pre_xd_rise, 2),
            "price_patterns": price_patterns,
            "recommendation": recommendation,
            "reason": reason
        }
    
    def get_buy_opportunities(self, min_score: float = 5.0) -> List[Dict]:
        """
        🔴 ดึงโอกาสซื้อสำหรับระยะยาว
        
        Args:
            min_score: คะแนนขั้นต่ำ
        
        Returns:
            รายการหุ้นที่น่าสนใจซื้อ
        """
        # คัดกรองหุ้นปันผลดี
        good_stocks = self.screen_high_dividend()
        
        opportunities = []
        
        for stock in good_stocks:
            if stock["score"] < min_score:
                continue
            
            symbol = stock["symbol"]
            
            # วิเคราะห์จังหวะ XD
            xd_analysis = self.analyze_xd_timing(symbol)
            
            opportunities.append({
                "symbol": symbol,
                "name": stock["name"],
                "current_price": stock["current_price"],
                "dividend_yield": stock["current_dividend_yield"],
                "avg_yield_5y": stock["avg_dividend_yield_5y"],
                "roe": stock["roe"],
                "score": stock["score"],
                "xd_recommendation": xd_analysis.get("recommendation", "HOLD"),
                "next_xd": xd_analysis.get("next_xd_date"),
                "reason": f"ปันผล {stock['current_dividend_yield']}% ROE {stock['roe']}%"
            })
        
        return opportunities
    
    def compare_with_risk_free(self, risk_free_rate: float = 2.5) -> List[Dict]:
        """
        🔴 เปรียบเทียบปันผลกับดอกเบี้ยปลอดภัย
        
        Args:
            risk_free_rate: อัตราดอกเบี้ยปลอดภัย (เช่น พันธบัตรรัฐบาล)
        
        Returns:
            หุ้นที่ให้ผลตอบแทนสูงกว่าดอกเบี้ย
        """
        good_stocks = self.screen_high_dividend(min_yield=risk_free_rate + 1)
        
        result = []
        for stock in good_stocks:
            premium = stock["current_dividend_yield"] - risk_free_rate
            result.append({
                "symbol": stock["symbol"],
                "name": stock["name"],
                "dividend_yield": stock["current_dividend_yield"],
                "risk_free_rate": risk_free_rate,
                "premium": round(premium, 2),
                "attractive": premium > 2.0
            })
        
        return result
