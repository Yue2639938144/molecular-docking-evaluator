"""
测试评分计算模块
"""

import unittest
import pandas as pd
import numpy as np
from src.core.scorer import Scorer
from src.data.processor import DataProcessor
from src.utils.logger import setup_logger
from src.config import REQUIRED_METRICS, OPTIONAL_METRICS

class TestScorer(unittest.TestCase):
    """测试Scorer类"""
    
    def setUp(self):
        """测试前准备"""
        # 设置日志
        setup_logger("INFO")
        
        # 创建评分计算器
        self.scorer = Scorer()
        
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
            'r_i_docking_score': [-10.0, -8.0, -9.0, -7.5],
            'r_i_glide_gscore': [-9.5, -8.5, -8.0, -7.0],
            'r_i_glide_emodel': [-50.0, -45.0, -40.0, -35.0],
            'r_i_glide_energy': [-30.0, -25.0, -20.0, -15.0],
            'r_i_glide_hbond': [-2.5, -2.0, -1.5, -1.0],
            'r_i_glide_lipo': [-3.0, -2.5, -2.0, -1.5]
        })
        
        # 预处理数据
        self.processed_data = self.processor.preprocess_data(self.test_data)
        
        # 标准化数据
        self.normalized_data = self.processor.normalize_data(self.processed_data)
        
        # 添加标准化后的列（模拟）
        for metric in REQUIRED_METRICS + OPTIONAL_METRICS[:2]:  # 只使用前两个可选指标
            if metric in self.normalized_data.columns:
                normalized_column = f"normalized_{metric}"
                if normalized_column not in self.normalized_data.columns:
                    # 简单地模拟标准化结果
                    self.normalized_data[normalized_column] = np.linspace(0, 1, len(self.normalized_data))
    
    def test_score_data(self):
        """测试数据评分"""
        # 选择指标
        selected_metrics = REQUIRED_METRICS + ['r_i_glide_hbond', 'r_i_glide_lipo']
        
        # 设置权重
        weights = {metric: 1.0 for metric in REQUIRED_METRICS}
        weights.update({
            'r_i_glide_hbond': 0.8,
            'r_i_glide_lipo': 0.6
        })
        
        # 计算评分
        scored_data = self.scorer.score_data(self.normalized_data, selected_metrics, weights)
        
        # 验证返回的是DataFrame
        self.assertIsInstance(scored_data, pd.DataFrame)
        
        # 验证包含评分列
        self.assertIn('total_score', scored_data.columns)
        self.assertIn('docking_score', scored_data.columns)
        self.assertIn('energy_score', scored_data.columns)
        
        # 验证评分在[0,1]范围内
        self.assertTrue((scored_data['total_score'] >= 0).all() and (scored_data['total_score'] <= 1).all())
        self.assertTrue((scored_data['docking_score'] >= 0).all() and (scored_data['docking_score'] <= 1).all())
        self.assertTrue((scored_data['energy_score'] >= 0).all() and (scored_data['energy_score'] <= 1).all())
    
    def test_score_conformation_protein_pairs(self):
        """测试构象-蛋白质对评分"""
        # 选择指标
        selected_metrics = REQUIRED_METRICS + ['r_i_glide_hbond', 'r_i_glide_lipo']
        
        # 设置权重
        weights = {metric: 1.0 for metric in REQUIRED_METRICS}
        weights.update({
            'r_i_glide_hbond': 0.8,
            'r_i_glide_lipo': 0.6
        })
        
        # 计算构象-蛋白质对评分
        conf_protein_scores = self.scorer.score_conformation_protein_pairs(
            self.normalized_data, selected_metrics, weights
        )
        
        # 验证返回的是字典
        self.assertIsInstance(conf_protein_scores, dict)
        
        # 验证包含所有构象
        self.assertEqual(len(conf_protein_scores), 2)  # 2个唯一的(title, lignum)组合
        
        # 验证每个构象包含所有蛋白质
        for conf_id, proteins in conf_protein_scores.items():
            self.assertEqual(len(proteins), 2)  # 2个蛋白质
            self.assertIn('CCND1', proteins)
            self.assertIn('KDR', proteins)
            
            # 验证每个蛋白质的评分包含必要的键
            for protein, scores in proteins.items():
                self.assertIn('total_score', scores)
                self.assertIn('docking_score', scores)
                self.assertIn('energy_score', scores)
                self.assertIn('raw_data', scores)

if __name__ == '__main__':
    unittest.main() 