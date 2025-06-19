#!/usr/bin/env python
"""
分子对接结果优化排序工具运行脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.main import main

if __name__ == "__main__":
    main() 