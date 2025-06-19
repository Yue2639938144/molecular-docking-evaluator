"""
测试运行脚本
"""

import unittest
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入测试模块
from tests.test_reader import TestDataReader
from tests.test_processor import TestDataProcessor
from tests.test_scorer import TestScorer
from tests.test_ranker import TestRanker
from tests.test_writer import TestDataWriter

def run_all_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_suite.addTest(unittest.makeSuite(TestDataReader))
    test_suite.addTest(unittest.makeSuite(TestDataProcessor))
    test_suite.addTest(unittest.makeSuite(TestScorer))
    test_suite.addTest(unittest.makeSuite(TestRanker))
    test_suite.addTest(unittest.makeSuite(TestDataWriter))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)

if __name__ == '__main__':
    run_all_tests() 