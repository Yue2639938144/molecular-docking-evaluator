"""
评分计算模块，负责计算综合评分
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Optional, Any, Tuple, Union

from src.core.metrics import MetricsProcessor
from src.config import config

logger = logging.getLogger()

class Scorer:
    """评分计算类，负责计算综合评分"""
    
    def __init__(self):
        """初始化评分计算器"""
        self.metrics_processor = MetricsProcessor()
    
    def score_data(self, data: pd.DataFrame, selected_metrics: List[str], 
                  weights: Dict[str, float]) -> pd.DataFrame:
        """计算数据的评分
        
        Args:
            data: 标准化后的数据
            selected_metrics: 选择的指标列表
            weights: 权重字典
            
        Returns:
            添加了评分列的DataFrame
        """
        if data is None or data.empty:
            logger.error("没有数据可供评分")
            return pd.DataFrame()
        
        # 创建副本以避免修改原始数据
        scored_data = data.copy()
        
        # 获取评分配置
        docking_weight = config.get("scoring", "docking_weight") or 0.4
        energy_weight = config.get("scoring", "energy_weight") or 0.4
        optional_weight = config.get("scoring", "optional_weight") or 0.2
        
        # 计算每行的评分
        scores = []
        for _, row in scored_data.iterrows():
            total_score, docking_score, energy_score = self.metrics_processor.calculate_composite_score(
                row, selected_metrics, weights, 
                docking_weight, energy_weight, optional_weight
            )
            scores.append({
                'total_score': total_score,
                'docking_score': docking_score,
                'energy_score': energy_score
            })
        
        # 添加评分列
        scored_data['total_score'] = [s['total_score'] for s in scores]
        scored_data['docking_score'] = [s['docking_score'] for s in scores]
        scored_data['energy_score'] = [s['energy_score'] for s in scores]
        
        logger.info(f"评分计算完成，处理了 {len(scored_data)} 行数据")
        return scored_data
    
    def score_conformation_protein_pairs(self, data: pd.DataFrame, 
                                        selected_metrics: List[str], 
                                        weights: Dict[str, float]) -> Dict[Tuple[int, int], Dict[str, Any]]:
        """计算每个构象与每个蛋白质的评分
        
        Args:
            data: 标准化后的数据
            selected_metrics: 选择的指标列表
            weights: 权重字典
            
        Returns:
            构象-蛋白质评分字典，格式为 {(title, lignum): {protein_name: {scores...}}}
        """
        if data is None or data.empty:
            logger.error("没有数据可供评分")
            return {}
        
        # 获取评分配置
        docking_weight = config.get("scoring", "docking_weight") or 0.4
        energy_weight = config.get("scoring", "energy_weight") or 0.4
        optional_weight = config.get("scoring", "optional_weight") or 0.2
        
        # 按构象分组
        conformations = {}
        for _, row in data.iterrows():
            conf_id = (row['title'], row['i_i_glide_lignum'])
            protein = row['protein_name']
            
            if conf_id not in conformations:
                conformations[conf_id] = {}
            
            # 计算该构象与当前蛋白的评分
            total_score, docking_score, energy_score = self.metrics_processor.calculate_composite_score(
                row, selected_metrics, weights, 
                docking_weight, energy_weight, optional_weight
            )
            
            conformations[conf_id][protein] = {
                'total_score': total_score,
                'docking_score': docking_score,
                'energy_score': energy_score,
                'raw_data': row
            }
        
        logger.info(f"构象-蛋白质评分计算完成，共 {len(conformations)} 个构象")
        return conformations 