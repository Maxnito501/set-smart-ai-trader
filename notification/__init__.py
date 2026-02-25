"""
📁 notification/__init__.py
ทำให้โฟลเดอร์ notification เป็น Python package
"""

from .line_messaging import LineMessaging  # 🔴 เปลี่ยนชื่อ

__all__ = ['LineMessaging']  # 🔴 เปลี่ยนชื่อ
__version__ = '0.1.0'
