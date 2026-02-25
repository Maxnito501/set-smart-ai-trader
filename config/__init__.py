"""
📁 config/__init__.py
ทำให้โฟลเดอร์ config เป็น Python package
"""

# 🔴 import settings จากไฟล์ settings.py
# เพื่อให้เวลาคนอื่น import จะได้สะดวก: from config import settings
from .settings import settings

# 🔴 กำหนด __all__ ว่าให้ import อะไรได้บ้าง
__all__ = ['settings']

# 🔴 เวอร์ชันของ config package (ถ้าต้องการ)
__version__ = '0.1.0'
