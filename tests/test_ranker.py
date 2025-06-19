"""
测试排序处理模块
"""

import unittest
import pandas as pd
import numpy as np
from src.core.ranker import Ranker
from src.data.processor import DataProcessor
from src.utils.logger import setup_logger
from src.config import REQUIRED_METRICS, OPTIONAL_METRICS

class TestRanker(unittest.TestCase):
    """测试Ranker类"""
    
    def setUp(self):
        """测试前准备"""
        # 设置日志
        setup_logger("INFO")
        
        # 创建排序处理器
        self.ranker = Ranker()
        
        # 创建数据处理器
        self.processor = DataProcessor()
        
        # 创建测试数据
        self.create_test_data()
    
    def create_test_data(self):
        """创建测试数据"""
        # 创建一个简单的测试数据框
        self.test_data = pd.DataFrame({
            'title': [1, 1, 2, 2, 3, 3],
            'i_i_glide_lignum': [1, 1, 2, 2, 3, 3],
            'protein_name': ['CCND1', 'KDR', 'CCND1', 'KDR', 'CCND1', 'KDR'],
            'r_i_docking_score': [-10.0, -8.0, -9.0, -7.5, -8.5, -9.5],
            'r_i_glide_gscore': [-9.5, -8.5, -8.0, -7.0, -7.5, -9.0],
            'r_i_glide_emodel': [-50.0, -45.0, -40.0, -35.0, -42.0, -48.0],
            'r_i_glide_energy': [-30.0, -25.0, -20.0, -15.0, -22.0, -28.0],
            'r_i_glide_hbond': [-2.5, -2.0, -1.5, -1.0, -1.8, -2.2],
            'r_i_glide_lipo': [-3.0, -2.5, -2.0, -1.5, -2.2, -2.8]
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
        
        # 添加评分列（模拟）
        self.normalized_data['total_score'] = np.linspace(0, 0.9, len(self.normalized_data))
        self.normalized_data['docking_score'] = np.linspace(0, 0.8, len(self.normalized_data))
        self.normalized_data['energy_score'] = np.linspace(0, 0.7, len(self.normalized_data))
    
    def test_rank_conformations(self):
        """测试构象排序"""
        # 选择指标
        selected_metrics = REQUIRED_METRICS + ['r_i_glide_hbond', 'r_i_glide_lipo']
        
        # 设置权重
        weights = {metric: 1.0 for metric in REQUIRED_METRICS}
        weights.update({
            'r_i_glide_hbond': 0.8,
            'r_i_glide_lipo': 0.6
        })
        
        # 排序构象
        conformation_ranking = self.ranker.rank_conformations(
            self.normalized_data, selected_metrics, weights
        )
        
        # 验证返回的是列表
        self.assertIsInstance(conformation_ranking, list)
        
        # 验证包含所有构象
        self.assertEqual(len(conformation_ranking), 3)  # 3个唯一的构象
        
        # 验证每个构象包含必要的键
        for conf in conformation_ranking:
            self.assertIn('title', conf)
            self.assertIn('lignum', conf)
            self.assertIn('total_score', conf)
            self.assertIn('docking_score', conf)
            self.assertIn('energy_score', conf)
            self.assertIn('best_protein', conf)
            self.assertIn('raw_data', conf)
        
        # 验证排序正确（按总评分升序）
        for i in range(len(conformation_ranking) - 1):
            self.assertLessEqual(
                conformation_ranking[i]['total_score'],
                conformation_ranking[i + 1]['total_score']
            )
    
    def test_rank_proteins(self):
        """测试蛋白质排序"""
        # 首先排序构象
        selected_metrics = REQUIRED_METRICS + ['r_i_glide_hbond', 'r_i_glide_lipo']
        weights = {metric: 1.0 for metric in REQUIRED_METRICS}
        weights.update({
            'r_i_glide_hbond': 0.8,
            'r_i_glide_lipo': 0.6
        })
        
        self.ranker.rank_conformations(self.normalized_data, selected_metrics, weights)
        
        # 排序蛋白质
        protein_ranking = self.ranker.rank_proteins()
        
        # 验证返回的是列表
        self.assertIsInstance(protein_ranking, list)
        
        # 验证包含所有蛋白质
        self.assertEqual(len(protein_ranking), 2)  # 2个蛋白质
        
        # 验证每个蛋白质包含必要的键
        for protein in protein_ranking:
            self.assertIn('protein_name', protein)
            self.assertIn('best_count', protein)
            self.assertIn('avg_total_score', protein)
            self.assertIn('avg_docking_score', protein)
            self.assertIn('avg_energy_score', protein)
        
        # 验证排序正确（按最优构象数量降序，相同时按平均总评分升序）
        for i in range(len(protein_ranking) - 1):
            if protein_ranking[i]['best_count'] == protein_ranking[i + 1]['best_count']:
                self.assertLessEqual(
                    protein_ranking[i]['avg_total_score'],
                    protein_ranking[i + 1]['avg_total_score']
                )
            else:
                self.assertGreaterEqual(
                    protein_ranking[i]['best_count'],
                    protein_ranking[i + 1]['best_count']
                )

if __name__ == '__main__':
    unittest.main()