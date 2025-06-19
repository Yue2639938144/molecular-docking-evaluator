"""
排序处理模块，负责对构象和蛋白质进行排序
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Optional, Any, Tuple, Union

from src.core.scorer import Scorer
from src.config import config

logger = logging.getLogger()

class Ranker:
    """排序处理类，负责对构象和蛋白质进行排序"""
    
    def __init__(self):
        """初始化排序处理器"""
        self.scorer = Scorer()
        self.conformation_ranking = []
        self.protein_ranking = []
    
    def rank_conformations(self, data: pd.DataFrame, selected_metrics: List[str], 
                          weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """对构象进行排序
        
        Args:
            data: 标准化后的数据
            selected_metrics: 选择的指标列表
            weights: 权重字典
            
        Returns:
            排序后的构象列表
        """
        if data is None or data.empty:
            logger.error("没有数据可供排序")
            return []
        
        # 计算每个构象与每个蛋白质的评分
        conformations = self.scorer.score_conformation_protein_pairs(
            data, selected_metrics, weights
        )
        
        if not conformations:
            logger.error("评分计算失败，无法进行排序")
            return []
        
        # 找出每个构象的最优蛋白并排序
        result = []
        for conf_id, proteins in conformations.items():
            # 找出评分最低(最优)的蛋白
            best_protein = min(
                proteins.items(), 
                key=lambda x: x[1]['total_score']
            )
            
            result.append({
                'conf_id': conf_id,
                'title': conf_id[0],  # 小分子编号
                'lignum': conf_id[1],  # 构象编号
                'total_score': best_protein[1]['total_score'],
                'docking_score': best_protein[1]['docking_score'],
                'energy_score': best_protein[1]['energy_score'],
                'best_protein': best_protein[0],
                'raw_data': best_protein[1]['raw_data']
            })
        
        # 按总评分排序(升序，因为分数越低越好)
        result.sort(key=lambda x: x['total_score'])
        
        self.conformation_ranking = result
        logger.info(f"构象排序完成，共 {len(result)} 个构象")
        return result
    
    def rank_proteins(self) -> List[Dict[str, Any]]:
        """对蛋白质进行排序
        
        Returns:
            排序后的蛋白质列表
        """
        if not self.conformation_ranking:
            logger.error("没有构象排序结果，无法进行蛋白质排序")
            return []
        
        # 统计每个蛋白质的情况
        protein_stats = {}
        for conf in self.conformation_ranking:
            protein = conf['best_protein']
            
            if protein not in protein_stats:
                protein_stats[protein] = {
                    'best_count': 0,
                    'total_scores': [],
                    'docking_scores': [],
                    'energy_scores': []
                }
            
            protein_stats[protein]['best_count'] += 1
            protein_stats[protein]['total_scores'].append(conf['total_score'])
            protein_stats[protein]['docking_scores'].append(conf['docking_score'])
            protein_stats[protein]['energy_scores'].append(conf['energy_score'])
        
        # 计算平均分数
        result = []
        for protein, stats in protein_stats.items():
            result.append({
                'protein_name': protein,
                'best_count': stats['best_count'],
                'avg_total_score': np.mean(stats['total_scores']),
                'avg_docking_score': np.mean(stats['docking_scores']),
                'avg_energy_score': np.mean(stats['energy_scores'])
            })
        
        # 按最优构象数量排序(降序)，相同时按平均总评分排序(升序)
        result.sort(key=lambda x: (-x['best_count'], x['avg_total_score']))
        
        self.protein_ranking = result
        logger.info(f"蛋白质排序完成，共 {len(result)} 个蛋白质")
        return result
    
    def get_conformation_ranking(self) -> List[Dict[str, Any]]:
        """获取构象排序结果
        
        Returns:
            构象排序结果
        """
        return self.conformation_ranking
    
    def get_protein_ranking(self) -> List[Dict[str, Any]]:
        """获取蛋白质排序结果
        
        Returns:
            蛋白质排序结果
        """
        return self.protein_ranking 