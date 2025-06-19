"""
数据写入模块，负责将结果输出到Excel文件
"""

import os
import pandas as pd
import logging
from typing import List, Dict, Optional, Any, Union

from src.utils.helpers import ensure_directory_exists, format_float
from src.config import REQUIRED_METRICS, OPTIONAL_METRICS

logger = logging.getLogger()

class DataWriter:
    """数据写入类，负责将结果输出到Excel文件"""
    
    def __init__(self):
        """初始化数据写入器"""
        pass
    
    def write_conformation_ranking(self, data: List[Dict[str, Any]], 
                                  output_file: str, 
                                  selected_metrics: List[str]) -> bool:
        """将构象排序结果写入Excel文件
        
        Args:
            data: 构象排序结果列表
            output_file: 输出文件路径
            selected_metrics: 选择的指标列表
            
        Returns:
            是否成功写入
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            ensure_directory_exists(output_dir)
            
            # 创建DataFrame
            df = pd.DataFrame()
            
            # 添加基本列
            df['小分子编号'] = [item['title'] for item in data]
            df['构象编号'] = [item['lignum'] for item in data]
            df['总对接效果指数'] = [item['total_score'] for item in data]
            df['对接分数相关指数'] = [item['docking_score'] for item in data]
            df['能量相关指数'] = [item['energy_score'] for item in data]
            df['最优蛋白'] = [item['best_protein'] for item in data]
            
            # 添加原始指标值
            for metric in selected_metrics:
                if metric in REQUIRED_METRICS or metric in OPTIONAL_METRICS:
                    df[metric] = [item['raw_data'].get(metric, None) for item in data]
            
            # 创建Excel写入器
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='构象排序结果')
                
                # 设置列宽
                worksheet = writer.sheets['构象排序结果']
                for i, column in enumerate(df.columns):
                    max_length = max(
                        df[column].astype(str).map(len).max(),
                        len(str(column))
                    ) + 2
                    worksheet.column_dimensions[chr(65 + i)].width = max_length
            
            logger.info(f"构象排序结果已写入文件: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"写入构象排序结果时出错: {str(e)}")
            return False
    
    def write_protein_ranking(self, data: List[Dict[str, Any]], output_file: str) -> bool:
        """将蛋白质排序结果写入Excel文件
        
        Args:
            data: 蛋白质排序结果列表
            output_file: 输出文件路径
            
        Returns:
            是否成功写入
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            ensure_directory_exists(output_dir)
            
            # 创建DataFrame
            df = pd.DataFrame()
            
            # 添加列
            df['蛋白质名称'] = [item['protein_name'] for item in data]
            df['最优构象数量'] = [item['best_count'] for item in data]
            df['平均总对接效果指数'] = [item['avg_total_score'] for item in data]
            df['平均对接分数相关指数'] = [item['avg_docking_score'] for item in data]
            df['平均能量相关指数'] = [item['avg_energy_score'] for item in data]
            
            # 创建Excel写入器
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='蛋白质排序结果')
                
                # 设置列宽
                worksheet = writer.sheets['蛋白质排序结果']
                for i, column in enumerate(df.columns):
                    max_length = max(
                        df[column].astype(str).map(len).max(),
                        len(str(column))
                    ) + 2
                    worksheet.column_dimensions[chr(65 + i)].width = max_length
            
            logger.info(f"蛋白质排序结果已写入文件: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"写入蛋白质排序结果时出错: {str(e)}")
            return False
    
    def export_raw_data(self, data: pd.DataFrame, output_file: str) -> bool:
        """导出原始数据到Excel文件
        
        Args:
            data: 原始数据DataFrame
            output_file: 输出文件路径
            
        Returns:
            是否成功写入
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            ensure_directory_exists(output_dir)
            
            # 导出到Excel
            data.to_excel(output_file, index=False)
            
            logger.info(f"原始数据已导出到文件: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"导出原始数据时出错: {str(e)}")
            return False 