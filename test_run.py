#!/usr/bin/env python
"""
分子对接结果优化排序工具测试脚本
"""

import os
import sys
import logging
import pandas as pd

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.utils.logger import setup_logger
from src.data.reader import DataReader
from src.data.processor import DataProcessor
from src.core.scorer import Scorer
from src.core.ranker import Ranker
from src.data.writer import DataWriter
from src.config import REQUIRED_METRICS, OPTIONAL_METRICS

def run_test():
    """运行测试"""
    # 设置日志
    logger = setup_logger("INFO")
    logger.info("开始测试...")
    
    # 设置输入和输出目录
    input_dir = os.path.join(os.path.dirname(__file__), "蛋白")
    output_dir = os.path.join(os.path.dirname(__file__), "结果")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 选择指标和权重
    selected_metrics = REQUIRED_METRICS + ["r_i_glide_hbond", "r_i_glide_lipo"]
    weights = {metric: 1.0 for metric in REQUIRED_METRICS}
    weights.update({
        "r_i_glide_hbond": 0.8,
        "r_i_glide_lipo": 0.6
    })
    
    try:
        # 读取数据
        logger.info(f"读取数据，输入目录: {input_dir}")
        reader = DataReader()
        data, protein_dfs = reader.read_directory(input_dir)
        
        if data is None:
            logger.error("数据读取失败")
            return False
        
        logger.info(f"成功读取 {len(data)} 行数据，包含 {len(protein_dfs)} 个蛋白质")
        
        # 预处理数据
        logger.info("预处理数据...")
        processor = DataProcessor()
        processed_data = processor.preprocess_data(data)
        
        # 标准化数据
        logger.info("标准化数据...")
        normalized_data = processor.normalize_data(processed_data)
        
        # 排序构象
        logger.info("排序构象...")
        ranker = Ranker()
        conformation_ranking = ranker.rank_conformations(normalized_data, selected_metrics, weights)
        
        # 排序蛋白质
        logger.info("排序蛋白质...")
        protein_ranking = ranker.rank_proteins()
        
        # 输出结果
        logger.info("输出结果...")
        writer = DataWriter()
        
        # 构象排序结果
        conformation_file = os.path.join(output_dir, "test_conformation_ranking.xlsx")
        writer.write_conformation_ranking(conformation_ranking, conformation_file, selected_metrics)
        
        # 蛋白质排序结果
        protein_file = os.path.join(output_dir, "test_protein_ranking.xlsx")
        writer.write_protein_ranking(protein_ranking, protein_file)
        
        logger.info("测试完成")
        logger.info(f"构象排序结果已保存到: {conformation_file}")
        logger.info(f"蛋白质排序结果已保存到: {protein_file}")
        
        return True
        
    except Exception as e:
        logger.exception(f"测试过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1) 