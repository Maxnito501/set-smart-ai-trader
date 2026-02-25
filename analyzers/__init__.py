"""
📁 analyzers/__init__.py
ทำให้โฟลเดอร์ analyzers เป็น Python package
"""

from .short_term import ShortTermAnalyzer
from .long_term import LongTermAnalyzer  # 🔴 เพิ่มบรรทัดนี้

__all__ = ['ShortTermAnalyzer', 'LongTermAnalyzer']  # 🔴 แก้ไข
__version__ = '0.1.0'
