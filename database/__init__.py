"""
📁 database/__init__.py
ทำให้โฟลเดอร์ database เป็น Python package
"""

from .db_manager import DatabaseManager

__all__ = ['DatabaseManager']
__version__ = '0.1.0'
