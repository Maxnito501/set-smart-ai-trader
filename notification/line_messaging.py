"""
📁 notification/line_messaging.py
ส่งการแจ้งเตือนผ่าน LINE Messaging API
ใช้ channel access token (long-lived) และ user ID
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Optional, Any, Union

from config.settings import settings


class LineMessaging:
    """
    ส่งข้อความแจ้งเตือนผ่าน LINE Messaging API
    
    วิธีใช้:
        line = LineMessaging()
        line.send("สวัสดี")
        line.send_buy_signal(buy_signals)
    
    หมายเหตุ:
        - ต้องมี channel access token (long-lived) จาก LINE Developers Console
        - ต้องมี user ID ของผู้รับ (ดูได้จาก webhook หรือ LINE Developers Console)
    """
    
    def __init__(self, 
                 channel_access_token: Optional[str] = None,
                 user_id: Optional[str] = None):
        """
        🔴 เริ่มต้น LINE Messaging API
        
        Args:
            channel_access_token: LINE Channel Access Token (long-lived)
            user_id: LINE User ID ของผู้รับ
        """
        self.channel_access_token = channel_access_token or settings.LINE_CHANNEL_ACCESS_TOKEN
        self.user_id = user_id or settings.LINE_USER_ID
        self.api_url = "https://api.line.me/v2/bot/message/push"
        
        # 🔴 ตรวจสอบค่าที่จำเป็น
        self._check_config()
        
        print("✅ สร้าง LineMessaging แล้ว")
    
    def _check_config(self):
        """🔴 ตรวจสอบ LINE configuration"""
        missing = []
        
        if not self.channel_access_token:
            missing.append("LINE_CHANNEL_ACCESS_TOKEN")
        elif self.channel_access_token == "YOUR_CHANNEL_ACCESS_TOKEN_HERE":
            print("⚠️ Warning: กรุณาใส่ Channel Access Token จริงใน .env")
        
        if not self.user_id:
            missing.append("LINE_USER_ID")
        elif self.user_id == "YOUR_USER_ID_HERE":
            print("⚠️ Warning: กรุณาใส่ User ID จริงใน .env")
        
        if missing:
            print(f"⚠️ Missing LINE config: {', '.join(missing)}")
            print("   ดูวิธีขอ Token และ User ID ได้ที่:")
            print("   https://developers.line.biz/console/")
            self.enabled = False
        else:
            self.enabled = True
    
    def send(self, 
             message: str, 
             user_id: Optional[str] = None) -> bool:
        """
        🔴 ส่งข้อความธรรมดา
        
        Args:
            message: ข้อความที่จะส่ง
            user_id: LINE User ID (ถ้าไม่ใส่ ใช้ค่าเริ่มต้น)
        
        Returns:
            True ถ้าสำเร็จ, False ถ้าไม่สำเร็จ
        """
        if not self.enabled:
            print(f"📝 [LINE ทดสอบ] {message}")
            return False
        
        target_user = user_id or self.user_id
        
        headers = {
            "Authorization": f"Bearer {self.channel_access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": target_user,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ ส่ง LINE สำเร็จ")
                return True
            else:
                print(f"❌ ส่ง LINE ไม่สำเร็จ: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            return False
    
    def send_with_emoji(self, 
                        message: str,
                        emojis: Optional[List[Dict]] = None,
                        user_id: Optional[str] = None) -> bool:
        """
        🔴 ส่งข้อความพร้อม emoji
        
        Args:
            message: ข้อความ (ใส่ $ สำหรับตำแหน่ง emoji)
            emojis: รายการ emoji [{"index": 0, "productId": "...", "emojiId": "..."}]
            user_id: LINE User ID
        
        Returns:
            True ถ้าสำเร็จ
        
        ตัวอย่าง:
            line.send_with_emoji(
                "$ สวัสดี $",
                [
                    {"index": 0, "productId": "5ac2213e040ab15980c9b447", "emojiId": "001"},
                    {"index": 10, "productId": "5ac2213e040ab15980c9b447", "emojiId": "002"}
                ]
            )
        """
        if not self.enabled:
            return False
        
        target_user = user_id or self.user_id
        
        headers = {
            "Authorization": f"Bearer {self.channel_access_token}",
            "Content-Type": "application/json"
        }
        
        message_obj = {
            "type": "text",
            "text": message
        }
        
        if emojis:
            message_obj["emojis"] = emojis
        
        payload = {
            "to": target_user,
            "messages": [message_obj]
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def send_sticker(self,
                    sticker_id: str,
                    package_id: str,
                    text: Optional[str] = None,
                    user_id: Optional[str] = None) -> bool:
        """
        🔴 ส่งสติกเกอร์
        
        Args:
            sticker_id: ID สติกเกอร์
            package_id: ID ชุดสติกเกอร์
            text: ข้อความเพิ่มเติม (optional)
            user_id: LINE User ID
        
        Returns:
            True ถ้าสำเร็จ
        """
        if not self.enabled:
            return False
        
        target_user = user_id or self.user_id
        
        headers = {
            "Authorization": f"Bearer {self.channel_access_token}",
            "Content-Type": "application/json"
        }
        
        messages = [
            {
                "type": "sticker",
                "stickerId": sticker_id,
                "packageId": package_id
            }
        ]
        
        if text:
            messages.insert(0, {
                "type": "text",
                "text": text
            })
        
        payload = {
            "to": target_user,
            "messages": messages
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    # ---------- ฟังก์ชันส่งข้อความเฉพาะ (เหมือนเดิม แต่ปรับเป็น LINE Messaging API) ----------
    
    def send_daily_summary(self, 
                          short_signals: List[Dict],
                          long_opportunities: List[Dict],
                          smart_money: List[Dict]) -> bool:
        """
        🔴 ส่งสรุปประจำวัน
        """
        today = datetime.now().strftime("%d/%m/%Y")
        
        message = f"📊 สรุปประจำวัน {today}\n"
        message += "════════════════════\n\n"
        
        # 🔴 เล่นสั้น
        message += "⚡ เล่นสั้น:\n"
        if short_signals:
            for s in short_signals[:5]:
                symbol = s.get("symbol", "")
                score = s.get("score", 0)
                rec = s.get("recommendation", "")
                
                if score >= 7:
                    emoji = "🟢"
                elif score >= 5:
                    emoji = "🟡"
                else:
                    emoji = "⚪"
                
                message += f"  {emoji} {symbol}: {rec} (คะแนน {score})\n"
                
                if "technical" in s:
                    price = s["technical"].get("current_price", 0)
                    message += f"     ราคา {price:.2f}\n"
        else:
            message += "  ไม่มีสัญญาณวันนี้\n"
        
        message += "\n"
        
        # 🔴 เล่นยาว
        message += "💰 เล่นยาว (ปันผล):\n"
        if long_opportunities:
            for o in long_opportunities[:3]:
                symbol = o.get("symbol", "")
                div = o.get("dividend_yield", 0)
                score = o.get("score", 0)
                
                message += f"  📈 {symbol}: {div}% (คะแนน {score})\n"
        else:
            message += "  ไม่มีโอกาสน่าสนใจ\n"
        
        message += "\n"
        
        # 🔴 รายใหญ่
        message += "🕵️ รายใหญ่:\n"
        if smart_money:
            for sm in smart_money[:3]:
                symbol = sm.get("symbol", "")
                score = sm.get("score", 0)
                rec = sm.get("recommendation", "")
                
                if score >= 3:
                    emoji = "🐳"
                elif score >= 0:
                    emoji = "🐟"
                else:
                    emoji = "🦐"
                
                message += f"  {emoji} {symbol}: {rec}\n"
        else:
            message += "  ไม่มีข้อมูลรายใหญ่\n"
        
        message += "\n"
        message += "📌 รายละเอียดเพิ่มเติม: https://github.com/yourname/set-smart-ai-trader"
        
        return self.send(message)
    
    def send_buy_signal(self, signal: Dict) -> bool:
        """
        🔴 ส่งสัญญาณซื้อ
        """
        symbol = signal.get("symbol", "???")
        score = signal.get("score", 0)
        rec = signal.get("recommendation", "BUY")
        
        # เลือก emoji ตามคะแนน
        if score >= 7:
            main_emoji = "🟢🟢🟢"
        elif score >= 5:
            main_emoji = "🟡"
        else:
            main_emoji = "⚪"
        
        message = f"{main_emoji} สัญญาณซื้อ: {symbol}\n"
        message += "════════════════════\n"
        
        # ราคา
        if "technical" in signal:
            tech = signal["technical"]
            price = tech.get("current_price", 0)
            rsi = tech.get("rsi", 50)
            message += f"💰 ราคา: {price:.2f} บาท\n"
            message += f"📊 RSI: {rsi:.1f}\n"
        
        # ปริมาณ
        if "volume" in signal:
            vol = signal["volume"]
            if isinstance(vol, dict):
                ratio = vol.get("volume_ratio", 1)
                if ratio > 2:
                    message += f"📈 Volume: {ratio:.1f} เท่า (สูงกว่าปกติ)\n"
        
        # NVDR
        if "nvdr" in signal:
            nvdr = signal["nvdr"]
            if isinstance(nvdr, dict):
                net = nvdr.get("net_total", 0)
                if net > 0:
                    message += f"🌏 NVDR: ซื้อสุทธิ {net:,.0f} บาท\n"
        
        # คะแนนและสัญญาณ
        message += f"\n🎯 คะแนน: {score}/10\n"
        message += f"💡 คำแนะนำ: {rec}\n"
        
        if "signals" in signal:
            message += f"🔔 สัญญาณ: {', '.join(signal['signals'][:3])}\n"
        
        message += f"\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        return self.send(message)
    
    def send_smart_money_alert(self, analysis: Dict) -> bool:
        """
        🔴 ส่งแจ้งเตือนเมื่อรายใหญ่เคลื่อนไหวผิดปกติ
        """
        symbol = analysis.get("symbol", "???")
        score = analysis.get("score", 0)
        
        if score >= 5:
            emoji = "🐳🐳🐳"
        elif score >= 2:
            emoji = "🐳"
        elif score <= -5:
            emoji = "🦈🦈🦈"
        elif score <= -2:
            emoji = "🦈"
        else:
            emoji = "🐟"
        
        message = f"{emoji} รายใหญ่: {symbol}\n"
        message += "════════════════════\n"
        
        message += f"คะแนน: {score}\n"
        message += f"คำแนะนำ: {analysis.get('recommendation', '')}\n\n"
        
        # NVDR
        if "nvdr" in analysis:
            nvdr = analysis["nvdr"]
            message += f"🌏 NVDR: {nvdr.get('trend', '')}\n"
        
        # Big Lot
        if "big_lot" in analysis:
            big = analysis["big_lot"]
            signal = big.get('signal', '')
            net = big.get('net', 0)
            if net != 0:
                message += f"📦 Big Lot: {signal} ({net:,.0f} บาท)\n"
        
        # A/D Line
        if "ad_line" in analysis:
            ad = analysis["ad_line"]
            signal = ad.get('signal', '')
            message += f"📉 A/D: {signal}\n"
        
        if "signals" in analysis:
            message += f"\n🔔 {', '.join(analysis['signals'])}"
        
        return self.send(message)
    
    def send_dca_plan(self, dca_opportunities: List[Dict]) -> bool:
        """
        🔴 ส่งแผน DCA ประจำเดือน
        """
        if not dca_opportunities:
            return False
        
        message = f"📅 แผน DCA {datetime.now().strftime('%B %Y')}\n"
        message += "════════════════════\n\n"
        
        total_budget = 0
        total_dividend = 0
        
        for d in dca_opportunities[:5]:
            symbol = d.get("symbol", "")
            shares = d.get("shares_per_month", 0)
            price = d.get("current_price", 0)
            div = d.get("expected_annual_dividend", 0)
            budget = shares * price
            
            message += f"📈 {symbol}: {shares} หุ้น @ {price:.2f} = {budget:,.0f} บาท\n"
            message += f"   ปันผลคาดปีละ {div:,.0f} บาท\n"
            
            total_budget += budget
            total_dividend += div
        
        message += f"\n💰 รวมลงทุนเดือนนี้: {total_budget:,.0f} บาท"
        message += f"\n💵 คาดปันผลปีหน้า: {total_dividend:,.0f} บาท"
        
        return self.send(message)
    
    def send_backtest_result(self, result) -> bool:
        """
        🔴 ส่งผล backtest
        """
        message = f"📊 ผล Backtest: {result.symbol}\n"
        message += "════════════════════\n"
        message += f"กลยุทธ์: {result.strategy_name}\n"
        message += f"ระยะเวลา: {result.start_date} ถึง {result.end_date}\n"
        message += f"เงินต้น: {result.initial_capital:,.0f} บาท\n"
        message += f"มูลค่าสุดท้าย: {result.final_value:,.0f} บาท\n"
        
        if result.total_return > 0:
            message += f"✅ กำไร: +{result.total_return:,.0f} บาท ({result.total_return_pct:+.2f}%)\n"
        else:
            message += f"❌ ขาดทุน: {result.total_return:,.0f} บาท ({result.total_return_pct:+.2f}%)\n"
        
        message += f"📉 Max Drawdown: {result.max_drawdown_pct:.2f}%\n"
        message += f"🎯 Win Rate: {result.win_rate:.2f}% ({result.num_wins}/{result.num_trades})\n"
        message += f"📊 Sharpe Ratio: {result.sharpe_ratio:.2f}\n"
        
        return self.send(message)
    
    def send_error(self, error_message: str, source: str = "ระบบ") -> bool:
        """
        🔴 ส่งแจ้งเตือน error
        """
        message = f"❌ Error จาก {source}\n"
        message += "════════════════════\n"
        message += error_message
        message += f"\n\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        return self.send(message)
