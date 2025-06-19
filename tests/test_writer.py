"""
测试数据写入模块
"""

import os
import unittest
import tempfile
import pandas as pd
from src.data.writer import DataWriter
from src.utils.logger import setup_logger
from src.config import REQUIRED_METRICS

class TestDataWriter(unittest.TestCase):
    """测试DataWriter类"""
    
    def setUp(self):
        """测试前准备"""
        # 设置日志
        setup_logger("INFO")
        
        # 创建数据写入器
        self.writer = DataWriter()
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试数据
        self.create_test_data()
    
    def tearDown(self):
        """测试后清理"""
        # 删除测试过程中创建的临时文件
        for file in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        
        # 删除临时目录
        os.rmdir(self.temp_dir)
    
    def create_test_data(self):
        """创建测试数据"""
        # 构象排序结果
        self.conformation_ranking = [
            {
                'conf_id': (1, 1),
                'title': 1,
                'lignum': 1,
                'total_score': 0.1,
                'docking_score': 0.2,
                'energy_score': 0.3,
                'best_protein': 'CCND1',
                'raw_data': {
                    'r_i_docking_score': -10.0,
                    'r_i_glide_gscore': -9.5,
                    'r_i_glide_emodel': -50.0,
                    'r_i_glide_energy': -30.0,
                    'r_i_glide_hbond': -2.5,
                    'r_i_glide_lipo': -3.0
                }
            },
            {
                'conf_id': (2, 2),
                'title': 2,
                'lignum': 2,
                'total_score': 0.2,
                'docking_score': 0.3,
                'energy_score': 0.4,
                'best_protein': 'KDR',
                'raw_data': {
                    'r_i_docking_score': -9.0,
                    'r_i_glide_gscore': -8.0,
                    'r_i_glide_emodel': -40.0,
                    'r_i_glide_energy': -20.0,
                    'r_i_glide_hbond': -1.5,
                    'r_i_glide_lipo': -2.0
                }
            }
        ]
        
        # 蛋白质排序结果
        self.protein_ranking = [
            {
                'protein_name': 'CCND1',
                'best_count': 3,
                'avg_total_score': 0.15,
                'avg_docking_score': 0.25,
                'avg_energy_score': 0.35
            },
            {
                'protein_name': 'KDR',
                'best_count': 2,
                'avg_total_score': 0.25,
                'avg_docking_score': 0.35,
                'avg_energy_score': 0.45
            }
        ]
        
        # 原始数据
        self.raw_data = pd.DataFrame({
            'title': [1, 1, 2, 2],
            'i_i_glide_lignum': [1, 1, 2, 2],
            'protein_name': ['CCND1', 'KDR', 'CCND1', 'KDR'],
            'r_i_docking_score': [-10.0, -8.0, -9.0, -7.5],
            'r_i_glide_gscore': [-9.5, -8.5, -8.0, -7.0],
            'r_i_glide_emodel': [-50.0, -45.0, -40.0, -35.0],
            'r_i_glide_energy': [-30.0, -25.0, -20.0, -15.0]
        })
    
    def test_write_conformation_ranking(self):
        """测试写入构象排序结果"""
        # 输出文件路径
        output_file = os.path.join(self.temp_dir, 'conformation_ranking.xlsx')
        
        # 写入构象排序结果
        result = self.writer.write_conformation_ranking(
            self.conformation_ranking, output_file, REQUIRED_METRICS
        )
        
        # 验证写入成功
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))
        
        # 读取写入的Excel文件
        df = pd.read_excel(output_file)
        
        # 验证行数正确
        self.assertEqual(len(df), len(self.conformation_ranking))
        
        # 验证包含必要的列
        self.assertIn('小分子编号', df.columns)
        self.assertIn('构象编号', df.columns)
        self.assertIn('总对接效果指数', df.columns)
        self.assertIn('对接分数相关指数', df.columns)
        self.assertIn('能量相关指数', df.columns)
        self.assertIn('最优蛋白', df.columns)
    
    def test_write_protein_ranking(self):
        """测试写入蛋白质排序结果"""
        # 输出文件路径
        output_file = os.path.join(self.temp_dir, 'protein_ranking.xlsx')
        
        # 写入蛋白质排序结果
        result = self.writer.write_protein_ranking(self.protein_ranking, output_file)
        
        # 验证写入成功
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))
        
        # 读取写入的Excel文件
        df = pd.read_excel(output_file)
        
        # 验证行数正确
        self.assertEqual(len(df), len(self.protein_ranking))
        
        # 验证包含必要的列
        self.assertIn('蛋白质名称', df.columns)
        self.assertIn('最优构象数量', df.columns)
        self.assertIn('平均总对接效果指数', df.columns)
        self.assertIn('平均对接分数相关指数', df.columns)
        self.assertIn('平均能量相关指数', df.columns)
    
    def test_export_raw_data(self):
        """测试导出原始数据"""
        # 输出文件路径
        output_file = os.path.join(self.temp_dir, 'raw_data.xlsx')
        
        # 导出原始数据
        result = self.writer.export_raw_data(self.raw_data, output_file)
        
        # 验证导出成功
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))
        
        # 读取导出的Excel文件
        df = pd.read_excel(output_file)
        
        # 验证行数和列数正确
        self.assertEqual(len(df), len(self.raw_data))
        self.assertEqual(len(df.columns), len(self.raw_data.columns))

if __name__ == '__main__':
    unittest.main() 