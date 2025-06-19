"""
测试数据读取模块
"""

import os
import unittest
import pandas as pd
from src.data.reader import DataReader
from src.utils.logger import setup_logger

class TestDataReader(unittest.TestCase):
    """测试DataReader类"""
    
    def setUp(self):
        """测试前准备"""
        # 设置日志
        setup_logger("INFO")
        
        # 创建数据读取器
        self.reader = DataReader()
        
        # 测试数据目录
        self.test_dir = os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_data')
        self.protein_dir = os.path.join(os.path.dirname(__file__), '..', '蛋白')
    
    def test_read_csv_file(self):
        """测试读取单个CSV文件"""
        # 使用实际的蛋白质文件进行测试
        if os.path.exists(self.protein_dir):
            csv_files = [f for f in os.listdir(self.protein_dir) 
                        if f.endswith('.csv') and os.path.isfile(os.path.join(self.protein_dir, f))]
            
            if csv_files:
                test_file = os.path.join(self.protein_dir, csv_files[0])
                df = self.reader.read_csv_file(test_file)
                
                # 验证返回的是DataFrame
                self.assertIsInstance(df, pd.DataFrame)
                
                # 验证包含必需列
                required_columns = ['title', 'i_i_glide_lignum', 'r_i_docking_score', 
                                   'r_i_glide_gscore', 'r_i_glide_emodel', 'r_i_glide_energy']
                for col in required_columns:
                    self.assertIn(col, df.columns)
                
                # 验证添加了蛋白质名称列
                self.assertIn('protein_name', df.columns)
    
    def test_read_directory(self):
        """测试读取目录中的所有CSV文件"""
        # 使用实际的蛋白质目录进行测试
        if os.path.exists(self.protein_dir):
            data, protein_dfs = self.reader.read_directory(self.protein_dir)
            
            # 验证返回的是DataFrame和字典
            self.assertIsInstance(data, pd.DataFrame)
            self.assertIsInstance(protein_dfs, dict)
            
            # 验证字典的键是蛋白质名称
            for key in protein_dfs.keys():
                self.assertIsInstance(key, str)
                self.assertGreater(len(key), 0)
            
            # 验证合并后的数据包含所有蛋白质的数据
            total_rows = sum(len(df) for df in protein_dfs.values())
            self.assertEqual(len(data), total_rows)

if __name__ == '__main__':
    unittest.main() 