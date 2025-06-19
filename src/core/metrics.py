"""
指标处理模块，负责处理各项评价指标
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Optional, Any, Tuple, Union

from src.config import REQUIRED_METRICS, OPTIONAL_METRICS, DOCKING_METRICS, ENERGY_METRICS

logger = logging.getLogger()

class MetricsProcessor:
    """指标处理类，负责处理各项评价指标"""
    
    def __init__(self):
        """初始化指标处理器"""
        pass
    
    def get_normalized_column_name(self, metric: str) -> str:
        """获取标准化后的列名
        
        Args:
            metric: 原始指标名
            
        Returns:
            标准化后的列名
        """
        return f"normalized_{metric}"
    
    def get_normalized_value(self, row: pd.Series, metric: str) -> float:
        """获取标准化后的指标值
        
        Args:
            row: 数据行
            metric: 指标名
            
        Returns:
            标准化后的值，如果不存在则返回1.0（最差值）
        """
        normalized_column = self.get_normalized_column_name(metric)
        if normalized_column in row:
            return row[normalized_column]
        return 1.0
    
    def calculate_weighted_score(self, row: pd.Series, metrics: List[str], 
                                weights: Dict[str, float]) -> float:
        """计算加权评分
        
        Args:
            row: 数据行
            metrics: 指标列表
            weights: 权重字典
            
        Returns:
            加权评分
        """
        # 筛选存在的指标
        valid_metrics = [m for m in metrics if self.get_normalized_column_name(m) in row]
        
        if not valid_metrics:
            return 1.0  # 最差分数
        
        # 计算加权和
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric in valid_metrics:
            weight = weights.get(metric, 1.0)
            normalized_value = self.get_normalized_value(row, metric)
            weighted_sum += weight * normalized_value
            total_weight += weight
        
        # 避免除以零
        if total_weight == 0:
            return 1.0
        
        return weighted_sum / total_weight
    
    def calculate_docking_score(self, row: pd.Series, weights: Dict[str, float]) -> float:
        """计算对接分数相关指数
        
        Args:
            row: 数据行
            weights: 权重字典
            
        Returns:
            对接分数相关指数
        """
        return self.calculate_weighted_score(row, DOCKING_METRICS, weights)
    
    def calculate_energy_score(self, row: pd.Series, weights: Dict[str, float]) -> float:
        """计算能量相关指数
        
        Args:
            row: 数据行
            weights: 权重字典
            
        Returns:
            能量相关指数
        """
        return self.calculate_weighted_score(row, ENERGY_METRICS, weights)
    
    def calculate_optional_score(self, row: pd.Series, selected_metrics: List[str], 
                                weights: Dict[str, float]) -> Tuple[float, bool]:
        """计算可选指标评分
        
        Args:
            row: 数据行
            selected_metrics: 选择的指标列表
            weights: 权重字典
            
        Returns:
            可选指标评分和是否有可选指标的元组
        """
        # 筛选可选指标
        optional_metrics = [m for m in selected_metrics 
                           if m in OPTIONAL_METRICS]
        
        if not optional_metrics:
            return 0.0, False
        
        return self.calculate_weighted_score(row, optional_metrics, weights), True
    
    def calculate_composite_score(self, row: pd.Series, selected_metrics: List[str], 
                                 weights: Dict[str, float], 
                                 docking_weight: float = 0.4,
                                 energy_weight: float = 0.4,
                                 optional_weight: float = 0.2) -> Tuple[float, float, float]:
        """计算综合评分
        
        Args:
            row: 数据行
            selected_metrics: 选择的指标列表
            weights: 权重字典
            docking_weight: 对接分数权重
            energy_weight: 能量分数权重
            optional_weight: 可选指标权重
            
        Returns:
            综合评分、对接分数相关指数和能量相关指数的元组
        """
        # 计算对接分数相关指数
        docking_score = self.calculate_docking_score(row, weights)
        
        # 计算能量相关指数
        energy_score = self.calculate_energy_score(row, weights)
        
        # 计算可选指标评分
        optional_score, has_optional = self.calculate_optional_score(
            row, selected_metrics, weights
        )
        
        # 计算综合评分
        if has_optional:
            total_score = (
                docking_weight * docking_score + 
                energy_weight * energy_score + 
                optional_weight * optional_score
            )
        else:
            # 如果没有可选指标，调整权重
            adjusted_docking_weight = docking_weight / (docking_weight + energy_weight)
            adjusted_energy_weight = energy_weight / (docking_weight + energy_weight)
            total_score = (
                adjusted_docking_weight * docking_score + 
                adjusted_energy_weight * energy_score
            )
        
        return total_score, docking_score, energy_score 