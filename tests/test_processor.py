"""
测试数据预处理模块
"""

import unittest
import pandas as pd
import numpy as np
from src.data.processor import DataProcessor
from src.utils.logger import setup_logger

class TestDataProcessor(unittest.TestCase):
    """测试DataProcessor类"""
    
    def setUp(self):
        """测试前准备"""
        # 设置日志
        setup_logger("INFO")
        
        # 创建数据处理器
        self.processor = DataProcessor()
        
        # 创建测试数据
        self.create_test_data()
    
    def create_test_data(self):
        """创建测试数据"""
        # 创建一个简单的测试数据框
        self.test_data = pd.DataFrame({
            'title': [1, 1, 2, 2],
            'i_i_glide_lignum': [1, 1, 2, 2],
            'protein_name': ['CCND1', 'KDR', 'CCND1', 'KDR'],
            'r_i_docking_score': [-10.0, -8.0, 10000.0, -7.5],
            'r_i_glide_gscore': [-9.5, 10000.0, -8.0, -7.0],
            'r_i_glide_emodel': [-50.0, -45.0, -40.0, -35.0],
            'r_i_glide_energy': [-30.0, -25.0, -20.0, -15.0],
            'r_i_glide_hbond': [-2.5, -2.0, -1.5, -1.0],
            'r_i_glide_lipo': [-3.0, -2.5, -2.0, -1.5]
        })
    
    def test_preprocess_data(self):
        """测试数据预处理"""
        processed_data = self.processor.preprocess_data(self.test_data)
        
        # 验证返回的是DataFrame
        self.assertIsInstance(processed_data, pd.DataFrame)
        
        # 验证处理了特殊值
        self.assertTrue(pd.isna(processed_data.loc[2, 'r_i_docking_score']))
        self.assertTrue(pd.isna(processed_data.loc[1, 'r_i_glide_gscore']))
    
    def test_normalize_metric(self):
        """测试指标标准化"""
        # 测试min-max标准化
        values = pd.Series([-10.0, -5.0, 0.0, 5.0, 10.0])
        normalized = self.processor.normalize_metric(values, 'min-max')
        
        # 验证标准化后的范围在[0,1]之间
        self.assertTrue((normalized >= 0).all() and (normalized <= 1).all())
        
        # 验证最小值标准化为0，最大值标准化为1
        self.assertAlmostEqual(normalized.min(), 0.0)
        self.assertAlmostEqual(normalized.max(), 1.0)
        
        # 测试z-score标准化
        normalized = self.processor.normalize_metric(values, 'z-score')
        
        # 验证标准化后的范围在(0,1)之间（sigmoid变换后）
        self.assertTrue((normalized > 0).all() and (normalized < 1).all())
    
    def test_normalize_data(self):
        """测试数据标准化"""
        # 预处理数据
        processed_data = self.processor.preprocess_data(self.test_data)
        
        # 标准化数据
        normalized_data = self.processor.normalize_data(processed_data)
        
        # 验证返回的是DataFrame
        self.assertIsInstance(normalized_data, pd.DataFrame)
        
        # 验证包含标准化后的列
        for metric in ['r_i_docking_score', 'r_i_glide_gscore', 'r_i_glide_emodel', 'r_i_glide_energy']:
            normalized_column = f"normalized_{metric}"
            self.assertIn(normalized_column, normalized_data.columns)
        
        # 验证标准化后的值在[0,1]范围内
        for metric in ['r_i_docking_score', 'r_i_glide_gscore', 'r_i_glide_emodel', 'r_i_glide_energy']:
            normalized_column = f"normalized_{metric}"
            values = normalized_data[normalized_column].dropna()
            self.assertTrue((values >= 0).all() and (values <= 1).all())
    
    def test_split_data_by_protein(self):
        """测试按蛋白质拆分数据"""
        # 预处理和标准化数据
        processed_data = self.processor.preprocess_data(self.test_data)
        normalized_data = self.processor.normalize_data(processed_data)
        
        # 按蛋白质拆分数据
        protein_data = self.processor.split_data_by_protein(normalized_data)
        
        # 验证返回的是字典
        self.assertIsInstance(protein_data, dict)
        
        # 验证包含所有蛋白质
        self.assertEqual(set(protein_data.keys()), {'CCND1', 'KDR'})
        
        # 验证每个蛋白质的数据行数正确
        self.assertEqual(len(protein_data['CCND1']), 2)
        self.assertEqual(len(protein_data['KDR']), 2)

if __name__ == '__main__':
    unittest.main() 