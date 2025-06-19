"""
数据读取模块，负责读取CSV文件并进行初步处理
"""

import os
import pandas as pd
import logging
from typing import List, Dict, Optional, Any, Tuple

from src.utils.helpers import list_csv_files, get_protein_name_from_file, check_required_columns
from src.config import REQUIRED_METRICS, DOCKING_METRICS

logger = logging.getLogger()

class DataReader:
    """数据读取类，负责读取和初步处理CSV文件"""
    
    def __init__(self):
        """初始化数据读取器"""
        self.data = None
        self.protein_files = {}
    
    def read_csv_file(self, file_path: str, encoding: str = 'utf-8') -> Optional[pd.DataFrame]:
        """读取单个CSV文件
        
        Args:
            file_path: CSV文件路径
            encoding: 文件编码
            
        Returns:
            读取的DataFrame，如果读取失败则返回None
        """
        try:
            # 尝试使用指定编码读取
            df = pd.read_csv(file_path, encoding=encoding)
            
            # 检查必需列
            required_columns = ['title', 'i_i_glide_lignum'] + REQUIRED_METRICS
            if not check_required_columns(df, required_columns):
                logger.error(f"文件 {file_path} 缺少必需列")
                return None
            
            # 添加蛋白质名称列
            protein_name = get_protein_name_from_file(file_path)
            df['protein_name'] = protein_name
            
            logger.info(f"成功读取文件 {file_path}，包含 {len(df)} 行数据")
            return df
            
        except UnicodeDecodeError:
            # 如果UTF-8编码失败，尝试其他编码
            for enc in ['gbk', 'gb2312', 'latin1']:
                try:
                    df = pd.read_csv(file_path, encoding=enc)
                    
                    # 检查必需列
                    required_columns = ['title', 'i_i_glide_lignum'] + REQUIRED_METRICS
                    if not check_required_columns(df, required_columns):
                        logger.error(f"文件 {file_path} 缺少必需列")
                        return None
                    
                    # 添加蛋白质名称列
                    protein_name = get_protein_name_from_file(file_path)
                    df['protein_name'] = protein_name
                    
                    logger.info(f"成功读取文件 {file_path}（使用 {enc} 编码），包含 {len(df)} 行数据")
                    return df
                except Exception:
                    continue
            
            logger.error(f"无法读取文件 {file_path}，尝试了多种编码")
            return None
            
        except Exception as e:
            logger.error(f"读取文件 {file_path} 时出错: {str(e)}")
            return None
    
    def read_directory(self, directory: str) -> Tuple[Optional[pd.DataFrame], Dict[str, pd.DataFrame]]:
        """读取目录中的所有CSV文件
        
        Args:
            directory: 目录路径
            
        Returns:
            合并后的DataFrame和每个蛋白质的DataFrame字典，如果读取失败则返回(None, {})
        """
        if not os.path.isdir(directory):
            logger.error(f"目录不存在: {directory}")
            return None, {}
        
        # 获取目录中的所有CSV文件
        csv_files = list_csv_files(directory)
        if not csv_files:
            logger.error(f"目录 {directory} 中没有CSV文件")
            return None, {}
        
        # 读取每个CSV文件
        dataframes = []
        protein_dfs = {}
        
        for file_path in csv_files:
            df = self.read_csv_file(file_path)
            if df is not None:
                protein_name = get_protein_name_from_file(file_path)
                dataframes.append(df)
                protein_dfs[protein_name] = df
                self.protein_files[protein_name] = file_path
        
        if not dataframes:
            logger.error("没有成功读取任何CSV文件")
            return None, {}
        
        # 合并所有DataFrame
        merged_df = pd.concat(dataframes, ignore_index=True)
        logger.info(f"合并了 {len(dataframes)} 个文件，共 {len(merged_df)} 行数据")
        
        self.data = merged_df
        return merged_df, protein_dfs
    
    def get_protein_names(self) -> List[str]:
        """获取所有蛋白质名称
        
        Returns:
            蛋白质名称列表
        """
        if self.data is None:
            return []
        
        return self.data['protein_name'].unique().tolist()
    
    def get_unique_conformations(self) -> List[Tuple[int, int]]:
        """获取所有唯一的构象标识
        
        Returns:
            构象标识列表，每个元素为(title, i_i_glide_lignum)
        """
        if self.data is None:
            return []
        
        # 获取唯一的(title, i_i_glide_lignum)组合
        unique_pairs = self.data[['title', 'i_i_glide_lignum']].drop_duplicates()
        return list(zip(unique_pairs['title'], unique_pairs['i_i_glide_lignum']))
    
    def get_data_for_protein(self, protein_name: str) -> Optional[pd.DataFrame]:
        """获取特定蛋白质的数据
        
        Args:
            protein_name: 蛋白质名称
            
        Returns:
            该蛋白质的DataFrame，如果不存在则返回None
        """
        if self.data is None:
            return None
        
        filtered = self.data[self.data['protein_name'] == protein_name]
        return filtered if not filtered.empty else None 