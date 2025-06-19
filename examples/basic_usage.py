#!/usr/bin/env python
"""
分子对接结果优化排序工具基本使用示例
"""

import os
import sys
import pandas as pd

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.logger import setup_logger
from src.data.reader import DataReader
from src.data.processor import DataProcessor
from src.core.scorer import Scorer
from src.core.ranker import Ranker
from src.data.writer import DataWriter
from src.config import REQUIRED_METRICS, OPTIONAL_METRICS

def main():
    """主函数"""
    # 设置日志
    logger = setup_logger("INFO")
    logger.info("开始示例...")
    
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
    
    # 3. 标准化数据
    logger.info("3. 标准化数据...")
    normalized_data = processor.normalize_data(processed_data)
    
    # 4. 选择指标和设置权重
    logger.info("4. 选择指标和设置权重...")
    # 选择必选指标和两个可选指标
    selected_metrics = REQUIRED_METRICS + ["r_i_glide_hbond", "r_i_glide_lipo"]
    
    # 设置权重
    weights = {metric: 1.0 for metric in REQUIRED_METRICS}  # 必选指标权重为1.0
    weights.update({
        "r_i_glide_hbond": 0.8,  # 氢键得分权重为0.8
        "r_i_glide_lipo": 0.6    # 疏水作用得分权重为0.6
    })
    
    # 5. 计算评分
    logger.info("5. 计算评分...")
    scorer = Scorer()
    scored_data = scorer.score_data(normalized_data, selected_metrics, weights)
    
    # 6. 排序构象
    logger.info("6. 排序构象...")
    ranker = Ranker()
    conformation_ranking = ranker.rank_conformations(normalized_data, selected_metrics, weights)
    
    # 7. 排序蛋白质
    logger.info("7. 排序蛋白质...")
    protein_ranking = ranker.rank_proteins()
    
    # 8. 输出结果
    logger.info("8. 输出结果...")
    writer = DataWriter()
    
    # 构象排序结果
    conformation_file = os.path.join(output_dir, "example_conformation_ranking.xlsx")
    writer.write_conformation_ranking(conformation_ranking, conformation_file, selected_metrics)
    
    # 蛋白质排序结果
    protein_file = os.path.join(output_dir, "example_protein_ranking.xlsx")
    writer.write_protein_ranking(protein_ranking, protein_file)
    
    # 9. 分析结果
    logger.info("9. 分析结果...")
    # 打印前5个最优构象
    print("\n前5个最优构象:")
    for i, conf in enumerate(conformation_ranking[:5]):
        print(f"排名 {i+1}:")
        print(f"  小分子编号: {conf['title']}")
        print(f"  构象编号: {conf['lignum']}")
        print(f"  总对接效果指数: {conf['total_score']:.4f}")
        print(f"  最优蛋白: {conf['best_protein']}")
    
    # 打印蛋白质排名
    print("\n蛋白质排名:")
    for i, protein in enumerate(protein_ranking):
        print(f"排名 {i+1}: {protein['protein_name']} (最优构象数量: {protein['best_count']})")
    
    logger.info("示例完成")
    print(f"\n构象排序结果已保存到: {conformation_file}")
    print(f"蛋白质排序结果已保存到: {protein_file}")

if __name__ == "__main__":
    main() 