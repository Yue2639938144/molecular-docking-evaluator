"""
数据预处理模块，负责数据清洗和标准化
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Optional, Any, Tuple

from src.utils.helpers import handle_special_values
from src.config import REQUIRED_METRICS, OPTIONAL_METRICS, DOCKING_METRICS, ENERGY_METRICS

logger = logging.getLogger()

class DataProcessor:
    """数据预处理类，负责数据清洗和标准化"""
    
    def __init__(self):
        """初始化数据预处理器"""
        self.data = None
        self.normalized_data = None
        self.protein_data = {}
    
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """预处理数据
        
        Args:
            data: 原始数据DataFrame
            
        Returns:
            预处理后的DataFrame
        """
        if data is None or data.empty:
            logger.error("没有数据可供预处理")
            return pd.DataFrame()
        
        # 创建副本以避免修改原始数据
        processed_data = data.copy()
        
        # 处理特殊值（10000）
        special_columns = DOCKING_METRICS  # 对接分数和Glide得分
        processed_data = handle_special_values(processed_data, special_columns)
        
        # 确保数值列为浮点型
        numeric_columns = REQUIRED_METRICS + OPTIONAL_METRICS
        for col in numeric_columns:
            if col in processed_data.columns:
                processed_data[col] = pd.to_numeric(processed_data[col], errors='coerce')
        
        self.data = processed_data
        logger.info(f"预处理完成，处理了 {len(processed_data)} 行数据")
        return processed_data
    
    def normalize_metric(self, values: pd.Series, method: str = 'min-max') -> pd.Series:
        """标准化指标值
        
        Args:
            values: 指标值Series
            method: 标准化方法，可选'min-max'或'z-score'
            
        Returns:
            标准化后的Series
        """
        # 处理空值和异常值
        valid_values = values.dropna()
        
        if valid_values.empty:
            return pd.Series([1.0] * len(values), index=values.index)
        
        if method == 'min-max':
            min_val = valid_values.min()
            max_val = valid_values.max()
            
            # 避免除以零
            if max_val == min_val:
                return pd.Series([0.0 if pd.notna(v) else 1.0 for v in values], index=values.index)
            
            # 标准化，空值处理为最差值1
            normalized = (values - min_val) / (max_val - min_val)
            normalized = normalized.fillna(1.0)
            return normalized
            
        elif method == 'z-score':
            mean = valid_values.mean()
            std = valid_values.std()
            
            # 避免除以零
            if std == 0:
                return pd.Series([0.0 if pd.notna(v) else 1.0 for v in values], index=values.index)
            
            # Z-score标准化，空值处理为最差值（设为3，相当于3个标准差）
            normalized = (values - mean) / std
            normalized = normalized.fillna(3.0)
            
            # 将z-score映射到[0,1]区间，使用sigmoid函数
            normalized = 1 / (1 + np.exp(-normalized))
            return normalized
        
        else:
            logger.warning(f"未知的标准化方法: {method}，使用min-max")
            return self.normalize_metric(values, 'min-max')
    
    def normalize_data(self, data: Optional[pd.DataFrame] = None, 
                      method: str = 'min-max') -> pd.DataFrame:
        """标准化数据
        
        Args:
            data: 待标准化的DataFrame，如果为None则使用self.data
            method: 标准化方法
            
        Returns:
            标准化后的DataFrame
        """
        if data is None:
            data = self.data
            
        if data is None or data.empty:
            logger.error("没有数据可供标准化")
            return pd.DataFrame()
        
        # 创建副本以避免修改原始数据
        normalized_data = data.copy()
        
        # 标准化所有数值指标
        metrics_to_normalize = REQUIRED_METRICS + OPTIONAL_METRICS
        for metric in metrics_to_normalize:
            if metric in data.columns:
                # 按蛋白质分组标准化
                for protein, group in data.groupby('protein_name'):
                    if group[metric].notna().any():  # 只处理有非空值的指标
                        normalized_values = self.normalize_metric(group[metric], method)
                        normalized_column = f"normalized_{metric}"
                        idx = group.index
                        normalized_data.loc[idx, normalized_column] = normalized_values
        
        self.normalized_data = normalized_data
        logger.info(f"数据标准化完成，使用方法: {method}")
        return normalized_data
    
    def get_normalized_data(self) -> Optional[pd.DataFrame]:
        """获取标准化后的数据
        
        Returns:
            标准化后的DataFrame
        """
        return self.normalized_data
    
    def split_data_by_protein(self, data: Optional[pd.DataFrame] = None) -> Dict[str, pd.DataFrame]:
        """按蛋白质拆分数据
        
        Args:
            data: 待拆分的DataFrame，如果为None则使用self.normalized_data
            
        Returns:
            按蛋白质名称索引的DataFrame字典
        """
        if data is None:
            data = self.normalized_data
            
        if data is None or data.empty:
            logger.error("没有数据可供拆分")
            return {}
        
        # 按蛋白质名称分组
        protein_groups = dict(tuple(data.groupby('protein_name')))
        self.protein_data = protein_groups
        
        logger.info(f"数据已按蛋白质拆分，共 {len(protein_groups)} 个蛋白质")
        return protein_groups 