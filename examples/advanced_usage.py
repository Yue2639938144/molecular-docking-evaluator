#!/usr/bin/env python
"""
分子对接结果优化排序工具高级使用示例
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.logger import setup_logger
from src.data.reader import DataReader
from src.data.processor import DataProcessor
from src.core.scorer import Scorer
from src.core.ranker import Ranker
from src.data.writer import DataWriter
from src.config import config, REQUIRED_METRICS, OPTIONAL_METRICS

def main():
    """主函数"""
    # 设置日志
    logger = setup_logger("INFO")
    logger.info("开始高级示例...")
    
    # 设置输入和输出目录
    input_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "蛋白")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "结果")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 读取数据
    logger.info("1. 读取数据...")
    reader = DataReader()
    data, protein_dfs = reader.read_directory(input_dir)
    
    if data is None:
        logger.error("数据读取失败")
        return
    
    logger.info(f"成功读取 {len(data)} 行数据，包含 {len(protein_dfs)} 个蛋白质")
    
    # 2. 预处理数据
    logger.info("2. 预处理数据...")
    processor = DataProcessor()
    processed_data = processor.preprocess_data(data)
    
    # 3. 自定义标准化方法
    logger.info("3. 使用自定义标准化方法...")
    # 使用z-score标准化
    config.set("scoring", "normalization_method", "z-score")
    normalized_data = processor.normalize_data(processed_data, "z-score")
    
    # 4. 自定义指标选择和权重
    logger.info("4. 自定义指标选择和权重...")
    # 选择所有可用指标
    selected_metrics = REQUIRED_METRICS + OPTIONAL_METRICS
    
    # 设置自定义权重
    weights = {
        # 必选指标权重
        "r_i_docking_score": 2.0,    # 对接分数权重加倍
        "r_i_glide_gscore": 1.5,     # Glide得分权重增加50%
        "r_i_glide_emodel": 1.0,     # 模型能量保持默认权重
        "r_i_glide_energy": 1.0,     # 总能量保持默认权重
        
        # 可选指标权重
        "r_i_glide_hbond": 1.2,      # 氢键得分权重增加20%
        "r_i_glide_lipo": 1.0,       # 疏水作用得分保持默认权重
        "r_i_glide_metal": 0.8,      # 金属键得分权重降低20%
        "r_i_glide_rewards": 0.5,    # 奖励得分权重降低50%
        "r_i_glide_evdw": 0.7,       # 范德华能量权重降低30%
        "r_i_glide_ecoul": 0.7,      # 库仑相互作用能量权重降低30%
        "r_i_glide_erotb": 0.4,      # 旋转键能量权重降低60%
        "r_i_glide_esite": 0.6,      # 结合位点能量权重降低40%
        "r_i_glide_einternal": 0.3   # 配体内部能量权重降低70%
    }
    
    # 5. 自定义评分配置
    logger.info("5. 自定义评分配置...")
    # 调整对接分数、能量和可选指标的权重比例
    config.set("scoring", "docking_weight", 0.5)    # 对接分数权重增加到50%
    config.set("scoring", "energy_weight", 0.3)     # 能量权重降低到30%
    config.set("scoring", "optional_weight", 0.2)   # 可选指标权重保持20%
    
    # 6. 计算评分
    logger.info("6. 计算评分...")
    scorer = Scorer()
    scored_data = scorer.score_data(normalized_data, selected_metrics, weights)
    
    # 7. 排序构象
    logger.info("7. 排序构象...")
    ranker = Ranker()
    conformation_ranking = ranker.rank_conformations(normalized_data, selected_metrics, weights)
    
    # 8. 排序蛋白质
    logger.info("8. 排序蛋白质...")
    protein_ranking = ranker.rank_proteins()
    
    # 9. 输出结果
    logger.info("9. 输出结果...")
    writer = DataWriter()
    
    # 构象排序结果
    conformation_file = os.path.join(output_dir, "advanced_conformation_ranking.xlsx")
    writer.write_conformation_ranking(conformation_ranking, conformation_file, selected_metrics)
    
    # 蛋白质排序结果
    protein_file = os.path.join(output_dir, "advanced_protein_ranking.xlsx")
    writer.write_protein_ranking(protein_ranking, protein_file)
    
    # 10. 高级分析
    logger.info("10. 高级分析...")
    
    # 分析前10个构象的指标分布
    top_conformations = conformation_ranking[:10]
    
    # 提取关键指标
    metrics_to_analyze = ["r_i_docking_score", "r_i_glide_gscore", "r_i_glide_emodel", "r_i_glide_energy"]
    metrics_data = {}
    
    for metric in metrics_to_analyze:
        metrics_data[metric] = [conf['raw_data'].get(metric, 0) for conf in top_conformations]
    
    # 打印统计信息
    print("\n前10个构象的指标统计:")
    for metric, values in metrics_data.items():
        print(f"{metric}:")
        print(f"  平均值: {np.mean(values):.4f}")
        print(f"  标准差: {np.std(values):.4f}")
        print(f"  最小值: {np.min(values):.4f}")
        print(f"  最大值: {np.max(values):.4f}")
    
    # 打印蛋白质分布
    protein_counts = {}
    for conf in top_conformations:
        protein = conf['best_protein']
        protein_counts[protein] = protein_counts.get(protein, 0) + 1
    
    print("\n前10个构象的蛋白质分布:")
    for protein, count in protein_counts.items():
        print(f"{protein}: {count} 个构象")
    
    logger.info("高级示例完成")
    print(f"\n构象排序结果已保存到: {conformation_file}")
    print(f"蛋白质排序结果已保存到: {protein_file}")

if __name__ == "__main__":
    main() 