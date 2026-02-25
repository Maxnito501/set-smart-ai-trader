"""
📁 backtest/engine.py
เครื่องมือทดสอบกลยุทธ์ย้อนหลัง (Backtest)
จำลองการซื้อขายกับข้อมูลในอดีต
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
import json

from database.db_manager import DatabaseManager
from config.settings import settings


@dataclass
class Trade:
    """🔴 บันทึกการซื้อขายแต่ละครั้ง"""
    date: str
    symbol: str
    action: str  # 'BUY' or 'SELL'
    price: float
    shares: int
    value: float
    commission: float = 0.0
    reason: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "date": self.date,
            "symbol": self.symbol,
            "action": self.action,
            "price": self.price,
            "shares": self.shares,
            "value": self.value,
            "commission": self.commission,
            "reason": self.reason
        }


@dataclass
class BacktestResult:
    """🔴 ผลลัพธ์การทดสอบย้อนหลัง"""
    symbol: str
    strategy_name: str
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float
    total_return: float
    total_return_pct: float
    max_drawdown: float
    max_drawdown_pct: float
    win_rate: float
    num_trades: int
    num_wins: int
    num_losses: int
    avg_win: float
    avg_loss: float
    profit_factor: float
    sharpe_ratio: float
    trades: List[Trade] = field(default_factory=list)
    
    def summary(self) -> str:
        """🔴 สรุปผลลัพธ์เป็นข้อความ"""
        return f"""
📊 ผลการทดสอบย้อนหลัง: {self.symbol} ({self.strategy_name})
   ระยะเวลา: {self.start_date} ถึง {self.end_date}
   เงินต้น: {self.initial_capital:,.2f} บาท
   มูลค่าสุดท้าย: {self.final_value:,.2f} บาท
   กำไรขาดทุน: {self.total_return:+,.2f} บาท ({self.total_return_pct:+.2f}%)
   Max Drawdown: {self.max_drawdown_pct:.2f}%
   จำนวนเทรด: {self.num_trades} ครั้ง (ชนะ {self.num_wins} / แพ้ {self.num_losses})
   Win Rate: {self.win_rate:.2f}%
   กำไรเฉลี่ยต่อครั้งที่ชนะ: {self.avg_win:+,.2f} บาท
   ขาดทุนเฉลี่ยต่อครั้งที่แพ้: {self.avg_loss:+,.2f} บาท
   Profit Factor: {self.profit_factor:.2f}
   Sharpe Ratio: {self.sharpe_ratio:.2f}
        """
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "strategy_name": self.strategy_name,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "initial_capital": self.initial_capital,
            "final_value": self.final_value,
            "total_return": self.total_return,
            "total_return_pct": self.total_return_pct,
            "max_drawdown": self.max_drawdown,
            "max_drawdown_pct": self.max_drawdown_pct,
            "win_rate": self.win_rate,
            "num_trades": self.num_trades,
            "num_wins": self.num_wins,
            "num_losses": self.num_losses,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "profit_factor": self.profit_factor,
            "sharpe_ratio": self.sharpe_ratio,
            "trades": [t.to_dict() for t in self.trades]
        }


class BacktestEngine:
    """
    เครื่องมือทดสอบกลยุทธ์ย้อนหลัง
    
    วิธีใช้:
        engine = BacktestEngine()
        result = engine.run(
            symbol="SCC",
            strategy=my_strategy_function,
            start_date="2025-01-01",
            end_date="2025-12-31"
        )
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        🔴 เริ่มต้น backtest engine
        
        Args:
            db_manager: ตัวจัดการฐานข้อมูล (ถ้าไม่มี จะสร้างใหม่)
        """
        self.db = db_manager or DatabaseManager()
        print("✅ สร้าง BacktestEngine แล้ว")
    
    def close(self):
        """🔴 ปิดการเชื่อมต่อฐานข้อมูล"""
        self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ---------- ฟังก์ชันคำนวณ ----------
    
    def calculate_drawdown(self, equity_curve: List[float]) -> Tuple[float, float]:
        """
        🔴 คำนวณ Maximum Drawdown
        
        Args:
            equity_curve: รายการมูลค่าพอร์ตตามเวลา
        
        Returns:
            (max_drawdown_value, max_drawdown_percentage)
        """
        peak = equity_curve[0]
        max_drawdown = 0
        max_drawdown_pct = 0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            
            drawdown = peak - value
            drawdown_pct = (drawdown / peak) * 100 if peak > 0 else 0
            
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_drawdown_pct = drawdown_pct
        
        return max_drawdown, max_drawdown_pct
    
    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """
        🔴 คำนวณ Sharpe Ratio
        
        Args:
            returns: รายการผลตอบแทนรายวัน (%)
            risk_free_rate: อัตราดอกเบี้ยปลอดภัยต่อปี (default 2%)
        
        Returns:
            Sharpe Ratio
        """
        if len(returns) < 2:
            return 0
        
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0
        
        # ปรับเป็น annualized (สมมติ 252 วันทำการ)
        annualized_return = avg_return * 252
        annualized_std = std_return * np.sqrt(252)
        
        sharpe = (annualized_return - risk_free_rate) / annualized_std
        
        return sharpe
    
    # ---------- ฟังก์ชันหลัก ----------
    
    def run(self,
            symbol: str,
            strategy_func: Callable,
            start_date: str,
            end_date: str,
            initial_capital: float = 100000.0,
            commission_rate: float = 0.001,  # 0.1% ค่าคอม
            slippage: float = 0.001,  # 0.1% slippage
            **kwargs) -> BacktestResult:
        """
        🔴 ทดสอบกลยุทธ์ย้อนหลัง
        
        Args:
            symbol: ชื่อหุ้น
            strategy_func: ฟังก์ชันกลยุทธ์ ที่รับ (date, prices, position, capital) และคืน ('BUY'/'SELL'/'HOLD', reason)
            start_date: วันที่เริ่มต้น (YYYY-MM-DD)
            end_date: วันที่สิ้นสุด (YYYY-MM-DD)
            initial_capital: เงินต้น
            commission_rate: อัตราค่าคอมมิชชัน (0.001 = 0.1%)
            slippage: Slippage (ราคาที่ได้จริงอาจต่างจากราคาที่ขอ)
            **kwargs: พารามิเตอร์อื่นๆ ส่งต่อให้กลยุทธ์
        
        Returns:
            BacktestResult
        """
        
        # 🔴 ดึงข้อมูลราคาย้อนหลัง
        prices = self.db.get_prices(symbol, limit=1000)
        
        if not prices:
            raise ValueError(f"ไม่มีข้อมูลราคาของ {symbol}")
        
        # กรองตามช่วงวันที่
        df_prices = pd.DataFrame(prices)
        df_prices['date'] = pd.to_datetime(df_prices['date'])
        df_prices = df_prices[(df_prices['date'] >= start_date) & (df_prices['date'] <= end_date)]
        df_prices = df_prices.sort_values('date')
        
        if len(df_prices) < 10:
            raise ValueError(f"ข้อมูลในช่วง {start_date} ถึง {end_date} ไม่เพียงพอ")
        
        # 🔴 เตรียมตัวแปรสำหรับจำลองการเทรด
        capital = initial_capital
        position = 0  # จำนวนหุ้นที่ถือ
        trades = []
        equity_curve = [initial_capital]
        daily_returns = []
        
        # สำหรับคำนวณ win rate
        wins = 0
        losses = 0
        win_amounts = []
        loss_amounts = []
        
        # ราคาซื้อล่าสุด (สำหรับคำนวณกำไร/ขาดทุน)
        last_buy_price = 0
        
        # 🔴 วนลูปตามวัน
        for i, row in df_prices.iterrows():
            date = row['date'].strftime('%Y-%m-%d')
            close = row['close']
            open_price = row['open']
            high = row['high']
            low = row['low']
            volume = row['volume']
            
            # ข้อมูลจนถึงวันนี้ (สำหรับส่งให้กลยุทธ์)
            current_data = df_prices.iloc[:i+1]
            
            # 🔴 เรียกกลยุทธ์
            try:
                signal, reason = strategy_func(
                    date=date,
                    prices=current_data,
                    position=position,
                    capital=capital,
                    **kwargs
                )
            except Exception as e:
                print(f"⚠️ กลยุทธ์ error ที่ {date}: {e}")
                signal = "HOLD"
                reason = "ERROR"
            
            # 🔴 ประมวลผลสัญญาณ
            if signal == "BUY" and capital > close * (1 + slippage):
                # ซื้อ
                max_shares = int(capital / (close * (1 + slippage)))
                
                if max_shares > 0:
                    buy_price = close * (1 + slippage)
                    buy_value = buy_price * max_shares
                    commission = buy_value * commission_rate
                    total_cost = buy_value + commission
                    
                    if total_cost <= capital:
                        position += max_shares
                        capital -= total_cost
                        last_buy_price = buy_price
                        
                        trades.append(Trade(
                            date=date,
                            symbol=symbol,
                            action="BUY",
                            price=buy_price,
                            shares=max_shares,
                            value=buy_value,
                            commission=commission,
                            reason=reason or "BUY signal"
                        ))
                        
                        print(f"  ✅ BUY {max_shares} shares @ {buy_price:.2f} on {date}")
            
            elif signal == "SELL" and position > 0:
                # ขายทั้งหมด
                sell_price = close * (1 - slippage)
                sell_value = sell_price * position
                commission = sell_value * commission_rate
                total_income = sell_value - commission
                
                capital += total_income
                
                # คำนวณกำไร/ขาดทุน
                profit_loss = total_income - (last_buy_price * position)
                
                if profit_loss > 0:
                    wins += 1
                    win_amounts.append(profit_loss)
                else:
                    losses += 1
                    loss_amounts.append(profit_loss)
                
                trades.append(Trade(
                    date=date,
                    symbol=symbol,
                    action="SELL",
                    price=sell_price,
                    shares=position,
                    value=sell_value,
                    commission=commission,
                    reason=reason or f"SELL signal (P/L: {profit_loss:+,.2f})"
                ))
                
                print(f"  ✅ SELL {position} shares @ {sell_price:.2f} on {date} (P/L: {profit_loss:+,.2f})")
                
                position = 0
                last_buy_price = 0
            
            # 🔴 คำนวณมูลค่าพอร์ต ณ สิ้นวัน
            portfolio_value = capital + (position * close)
            equity_curve.append(portfolio_value)
            
            if i > 0:
                daily_return = (portfolio_value - equity_curve[-2]) / equity_curve[-2] * 100
                daily_returns.append(daily_return)
        
        # 🔴 ขายหุ้นที่เหลืออยู่ ณ สิ้นงวด
        if position > 0:
            last_row = df_prices.iloc[-1]
            last_date = last_row['date'].strftime('%Y-%m-%d')
            last_close = last_row['close']
            
            sell_price = last_close * (1 - slippage)
            sell_value = sell_price * position
            commission = sell_value * commission_rate
            total_income = sell_value - commission
            
            capital += total_income
            
            profit_loss = total_income - (last_buy_price * position)
            
            if profit_loss > 0:
                wins += 1
                win_amounts.append(profit_loss)
            else:
                losses += 1
                loss_amounts.append(profit_loss)
            
            trades.append(Trade(
                date=last_date,
                symbol=symbol,
                action="SELL",
                price=sell_price,
                shares=position,
                value=sell_value,
                commission=commission,
                reason="End of period"
            ))
            
            position = 0
            equity_curve[-1] = capital
        
        # 🔴 คำนวณผลลัพธ์
        final_value = capital
        total_return = final_value - initial_capital
        total_return_pct = (total_return / initial_capital) * 100
        
        # Max Drawdown
        max_dd, max_dd_pct = self.calculate_drawdown(equity_curve)
        
        # Win Rate
        num_trades = len([t for t in trades if t.action == "SELL"])
        num_wins = wins
        num_losses = losses
        win_rate = (wins / num_trades * 100) if num_trades > 0 else 0
        
        # Average Win/Loss
        avg_win = sum(win_amounts) / len(win_amounts) if win_amounts else 0
        avg_loss = sum(loss_amounts) / len(loss_amounts) if loss_amounts else 0
        
        # Profit Factor
        total_wins = sum(win_amounts) if win_amounts else 0
        total_losses = abs(sum(loss_amounts)) if loss_amounts else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Sharpe Ratio
        sharpe = self.calculate_sharpe_ratio(daily_returns)
        
        return BacktestResult(
            symbol=symbol,
            strategy_name=strategy_func.__name__,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            final_value=final_value,
            total_return=total_return,
            total_return_pct=total_return_pct,
            max_drawdown=max_dd,
            max_drawdown_pct=max_dd_pct,
            win_rate=win_rate,
            num_trades=num_trades,
            num_wins=num_wins,
            num_losses=num_losses,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe,
            trades=trades
        )
    
    # ---------- กลยุทธ์ตัวอย่าง ----------
    
    @staticmethod
    def strategy_ma_crossover(date: str, prices: pd.DataFrame, 
                              position: int, capital: float,
                              short_ma: int = 5, long_ma: int = 20) -> Tuple[str, str]:
        """
        🔴 กลยุทธ์ตัวอย่าง: Moving Average Crossover
        
        ซื้อเมื่อ MA สั้นตัดขึ้นเหนือ MA ยาว
        ขายเมื่อ MA สั้นตัดลงใต้ MA ยาว
        """
        if len(prices) < long_ma + 1:
            return "HOLD", "ข้อมูลไม่พอ"
        
        # คำนวณ MA
        prices['ma_short'] = prices['close'].rolling(window=short_ma).mean()
        prices['ma_long'] = prices['close'].rolling(window=long_ma).mean()
        
        last = prices.iloc[-1]
        prev = prices.iloc[-2]
        
        # ตรวจสอบสัญญาณ
        if prev['ma_short'] <= prev['ma_long'] and last['ma_short'] > last['ma_long']:
            return "BUY", f"MA {short_ma} ตัดขึ้นเหนือ MA {long_ma}"
        
        elif prev['ma_short'] >= prev['ma_long'] and last['ma_short'] < last['ma_long']:
            return "SELL", f"MA {short_ma} ตัดลงใต้ MA {long_ma}"
        
        return "HOLD", "ไม่มีสัญญาณ"
    
    @staticmethod
    def strategy_rsi(date: str, prices: pd.DataFrame,
                     position: int, capital: float,
                     rsi_period: int = 14, oversold: int = 30, overbought: int = 70) -> Tuple[str, str]:
        """
        🔴 กลยุทธ์ตัวอย่าง: RSI
        
        ซื้อเมื่อ RSI < oversold
        ขายเมื่อ RSI > overbought
        """
        if len(prices) < rsi_period + 1:
            return "HOLD", "ข้อมูลไม่พอ"
        
        # คำนวณ RSI
        close_prices = prices['close'].values
        deltas = np.diff(close_prices)
        
        gains = deltas.copy()
        gains[gains < 0] = 0
        losses = -deltas.copy()
        losses[losses < 0] = 0
        
        avg_gain = np.mean(gains[-rsi_period:])
        avg_loss = np.mean(losses[-rsi_period:])
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        if rsi < oversold:
            return "BUY", f"RSI {rsi:.1f} < {oversold} (oversold)"
        
        elif rsi > overbought:
            return "SELL", f"RSI {rsi:.1f} > {overbought} (overbought)"
        
        return "HOLD", f"RSI {rsi:.1f}"
    
    @staticmethod
    def strategy_buy_and_hold(date: str, prices: pd.DataFrame,
                              position: int, capital: float,
                              **kwargs) -> Tuple[str, str]:
        """
        🔴 กลยุทธ์ตัวอย่าง: Buy and Hold
        
        ซื้อวันแรก ขายวันสุดท้าย
        """
        if len(prices) == 0:
            return "HOLD", ""
        
        if position == 0 and capital > 0:
            return "BUY", "Buy and hold"
        
        return "HOLD", ""
    
    # ---------- เปรียบเทียบหลายกลยุทธ์ ----------
    
    def compare_strategies(self,
                          symbol: str,
                          strategies: List[Tuple[str, Callable, Dict]],
                          start_date: str,
                          end_date: str,
                          initial_capital: float = 100000) -> List[BacktestResult]:
        """
        🔴 เปรียบเทียบหลายกลยุทธ์
        
        Args:
            symbol: ชื่อหุ้น
            strategies: list of (name, function, params)
            start_date: วันที่เริ่มต้น
            end_date: วันที่สิ้นสุด
            initial_capital: เงินต้น
        
        Returns:
            รายการผลลัพธ์ เรียงตาม Sharpe Ratio
        """
        results = []
        
        for name, func, params in strategies:
            print(f"\n🔍 ทดสอบกลยุทธ์: {name}")
            
            try:
                result = self.run(
                    symbol=symbol,
                    strategy_func=func,
                    start_date=start_date,
                    end_date=end_date,
                    initial_capital=initial_capital,
                    **params
                )
                
                result.strategy_name = name
                results.append(result)
                
                print(f"  ✅ กำไร: {result.total_return_pct:+.2f}%, Sharpe: {result.sharpe_ratio:.2f}")
                
            except Exception as e:
                print(f"  ❌ error: {e}")
        
        # เรียงตาม Sharpe Ratio
        results.sort(key=lambda x: x.sharpe_ratio, reverse=True)
        
        return results
