#!/usr/bin/env python
"""
分子对接结果优化排序工具批处理示例
"""

import os
import sys
import time
import shutil
import pandas as pd
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.logger import setup_logger
from src.data.reader import DataReader
from src.data.processor import DataProcessor
from src.core.scorer import Scorer
from src.core.ranker import Ranker
from src.data.writer import DataWriter
from src.config import config, REQUIRED_METRICS, OPTIONAL_METRICS

def process_dataset(input_dir, output_dir, dataset_name, selected_metrics, weights):
    """处理单个数据集
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        dataset_name: 数据集名称
        selected_metrics: 选择的指标
        weights: 权重字典
        
    Returns:
        处理是否成功
    """
    logger = logging.getLogger()
    logger.info(f"开始处理数据集: {dataset_name}")
    
    # 创建数据集输出目录
    dataset_output_dir = os.path.join(output_dir, dataset_name)
    os.makedirs(dataset_output_dir, exist_ok=True)
    
    try:
        # 读取数据
        reader = DataReader()
        data, protein_dfs = reader.read_directory(input_dir)
        
        if data is None:
            logger.error(f"数据集 {dataset_name} 读取失败")
            return False
        
        # 预处理数据
        processor = DataProcessor()
        processed_data = processor.preprocess_data(data)
        
        # 标准化数据
        normalization_method = config.get("scoring", "normalization_method") or "min-max"
        normalized_data = processor.normalize_data(processed_data, normalization_method)
        
        # 排序构象
        ranker = Ranker()
        conformation_ranking = ranker.rank_conformations(normalized_data, selected_metrics, weights)
        
        # 排序蛋白质
        protein_ranking = ranker.rank_proteins()
        
        # 输出结果
        writer = DataWriter()
        
        # 构象排序结果
        conformation_file = os.path.join(dataset_output_dir, f"{dataset_name}_conformation_ranking.xlsx")
        writer.write_conformation_ranking(conformation_ranking, conformation_file, selected_metrics)
        
        # 蛋白质排序结果
        protein_file = os.path.join(dataset_output_dir, f"{dataset_name}_protein_ranking.xlsx")
        writer.write_protein_ranking(protein_ranking, protein_file)
        
        # 导出原始数据
        raw_data_file = os.path.join(dataset_output_dir, f"{dataset_name}_raw_data.xlsx")
        writer.export_raw_data(data, raw_data_file)
        
        logger.info(f"数据集 {dataset_name} 处理完成")
        return True
        
    except Exception as e:
        logger.exception(f"处理数据集 {dataset_name} 时出错: {str(e)}")
        return False

def main():
    """主函数"""
    # 设置日志
    global logging
    import logging
    logger = setup_logger("INFO", f"batch_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", "logs")
    logger.info("开始批处理...")
    
    # 设置基本目录
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # 数据集列表（在实际应用中，这可能是不同的数据目录）
    # 这里我们使用同一个数据集，但使用不同的参数进行处理
    datasets = [
        {
            "name": "default_params",
            "input_dir": os.path.join(base_dir, "蛋白"),
            "metrics": REQUIRED_METRICS,
            "weights": {metric: 1.0 for metric in REQUIRED_METRICS},
            "config": {
                "normalization_method": "min-max",
                "docking_weight": 0.4,
                "energy_weight": 0.4,
                "optional_weight": 0.2
            }
        },
        {
            "name": "docking_focused",
            "input_dir": os.path.join(base_dir, "蛋白"),
            "metrics": REQUIRED_METRICS + ["r_i_glide_hbond", "r_i_glide_lipo"],
            "weights": {
                "r_i_docking_score": 2.0,
                "r_i_glide_gscore": 1.5,
                "r_i_glide_emodel": 1.0,
                "r_i_glide_energy": 1.0,
                "r_i_glide_hbond": 0.8,
                "r_i_glide_lipo": 0.6
            },
            "config": {
                "normalization_method": "min-max",
                "docking_weight": 0.6,
                "energy_weight": 0.3,
                "optional_weight": 0.1
            }
        },
        {
            "name": "energy_focused",
            "input_dir": os.path.join(base_dir, "蛋白"),
            "metrics": REQUIRED_METRICS + ["r_i_glide_evdw", "r_i_glide_ecoul"],
            "weights": {
                "r_i_docking_score": 1.0,
                "r_i_glide_gscore": 1.0,
                "r_i_glide_emodel": 2.0,
                "r_i_glide_energy": 1.5,
                "r_i_glide_evdw": 1.2,
                "r_i_glide_ecoul": 1.0
            },
            "config": {
                "normalization_method": "min-max",
                "docking_weight": 0.3,
                "energy_weight": 0.6,
                "optional_weight": 0.1
            }
        },
        {
            "name": "z_score_normalization",
            "input_dir": os.path.join(base_dir, "蛋白"),
            "metrics": REQUIRED_METRICS + OPTIONAL_METRICS,
            "weights": {metric: 1.0 for metric in REQUIRED_METRICS + OPTIONAL_METRICS},
            "config": {
                "normalization_method": "z-score",
                "docking_weight": 0.4,
                "energy_weight": 0.4,
                "optional_weight": 0.2
            }
        }
    ]
    
    # 创建批处理输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_output_dir = os.path.join(base_dir, "结果", f"batch_{timestamp}")
    os.makedirs(batch_output_dir, exist_ok=True)
    
    # 处理每个数据集
    results = {}
    for dataset in datasets:
        logger.info(f"配置数据集: {dataset['name']}")
        
        # 更新配置
        for key, value in dataset["config"].items():
            config.set("scoring", key, value)
        
        # 处理数据集
        start_time = time.time()
        success = process_dataset(
            dataset["input_dir"],
            batch_output_dir,
            dataset["name"],
            dataset["metrics"],
            dataset["weights"]
        )
        end_time = time.time()
        
        # 记录结果
        results[dataset["name"]] = {
            "success": success,
            "time": end_time - start_time
        }
    
    # 输出批处理结果摘要
    logger.info("批处理完成，结果摘要:")
    for name, result in results.items():
        status = "成功" if result["success"] else "失败"
        logger.info(f"数据集 {name}: {status}, 耗时 {result['time']:.2f} 秒")
    
    # 创建批处理报告
    report_file = os.path.join(batch_output_dir, "batch_report.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("分子对接结果优化排序工具批处理报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("处理结果摘要:\n")
        for name, result in results.items():
            status = "成功" if result["success"] else "失败"
            f.write(f"数据集 {name}: {status}, 耗时 {result['time']:.2f} 秒\n")
        
        f.write("\n数据集配置详情:\n")
        for dataset in datasets:
            f.write(f"\n数据集名称: {dataset['name']}\n")
            f.write(f"  输入目录: {dataset['input_dir']}\n")
            f.write(f"  选择指标: {', '.join(dataset['metrics'])}\n")
            f.write("  指标权重:\n")
            for metric, weight in dataset["weights"].items():
                f.write(f"    {metric}: {weight}\n")
            f.write("  配置参数:\n")
            for key, value in dataset["config"].items():
                f.write(f"    {key}: {value}\n")
    
    print(f"批处理完成，结果保存在: {batch_output_dir}")
    print(f"批处理报告: {report_file}")

if __name__ == "__main__":
    main() 