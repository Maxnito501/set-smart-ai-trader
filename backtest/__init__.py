"""
📁 backtest/__init__.py
ทำให้โฟลเดอร์ backtest เป็น Python package
"""

from .engine import BacktestEngine, Trade, BacktestResult

__all__ = ['BacktestEngine', 'Trade', 'BacktestResult']
__version__ = '0.1.0'
