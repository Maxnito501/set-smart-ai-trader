#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ทดสอบ Backtest Engine
"""

from backtest import BacktestEngine
from database import DatabaseManager
import pandas as pd

def main():
    print("🚀 กำลังทดสอบ BacktestEngine...")
    
    try:
        with BacktestEngine() as engine:
            
            # 🔴 1. ทดสอบกลยุทธ์ MA Crossover
            print("\n📈 ทดสอบกลยุทธ์ MA Crossover (SCC)...")
            
            result = engine.run(
                symbol="SCC",
                strategy_func=BacktestEngine.strategy_ma_crossover,
                start_date="2025-01-01",
                end_date="2025-12-31",
                initial_capital=100000,
                commission_rate=0.001,
                slippage=0.001,
                short_ma=5,
                long_ma=20
            )
            
            print(result.summary())
            
            # 🔴 2. ทดสอบกลยุทธ์ RSI
            print("\n📊 ทดสอบกลยุทธ์ RSI...")
            
            result2 = engine.run(
                symbol="SCC",
                strategy_func=BacktestEngine.strategy_rsi,
                start_date="2025-01-01",
                end_date="2025-12-31",
                initial_capital=100000,
                rsi_period=14,
                oversold=30,
                overbought=70
            )
            
            print(result2.summary())
            
            # 🔴 3. ทดสอบ Buy & Hold (สำหรับเทียบ)
            print("\n💼 ทดสอบ Buy & Hold...")
            
            result3 = engine.run(
                symbol="SCC",
                strategy_func=BacktestEngine.strategy_buy_and_hold,
                start_date="2025-01-01",
                end_date="2025-12-31",
                initial_capital=100000
            )
            
            print(result3.summary())
            
            # 🔴 4. เปรียบเทียบหลายกลยุทธ์
            print("\n🏆 เปรียบเทียบกลยุทธ์...")
            
            strategies = [
                ("MA Crossover (5,20)", BacktestEngine.strategy_ma_crossover, {"short_ma": 5, "long_ma": 20}),
                ("MA Crossover (10,30)", BacktestEngine.strategy_ma_crossover, {"short_ma": 10, "long_ma": 30}),
                ("RSI (14,30,70)", BacktestEngine.strategy_rsi, {"rsi_period": 14, "oversold": 30, "overbought": 70}),
                ("RSI (14,20,80)", BacktestEngine.strategy_rsi, {"rsi_period": 14, "oversold": 20, "overbought": 80}),
                ("Buy & Hold", BacktestEngine.strategy_buy_and_hold, {})
            ]
            
            comparisons = engine.compare_strategies(
                symbol="SCC",
                strategies=strategies,
                start_date="2025-01-01",
                end_date="2025-12-31",
                initial_capital=100000
            )
            
            print("\n📊 สรุปการเปรียบเทียบ:")
            for i, r in enumerate(comparisons, 1):
                print(f"  {i}. {r.strategy_name}: กำไร {r.total_return_pct:+.2f}%, Sharpe {r.sharpe_ratio:.2f}, Win Rate {r.win_rate:.1f}%")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main()
