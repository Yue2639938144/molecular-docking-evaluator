"""
命令行界面模块，提供命令行操作
"""

import os
import sys
import argparse
import logging
from typing import List, Dict, Optional, Any, Tuple

from src.config import config, REQUIRED_METRICS, OPTIONAL_METRICS
from src.utils.logger import setup_logger
from src.utils.helpers import ensure_directory_exists, is_valid_directory
from src.data.reader import DataReader
from src.data.processor import DataProcessor
from src.core.scorer import Scorer
from src.core.ranker import Ranker
from src.data.writer import DataWriter

logger = logging.getLogger()

def parse_args():
    """解析命令行参数
    
    Returns:
        解析后的参数
    """
    parser = argparse.ArgumentParser(description='分子对接结果优化排序工具')
    
    parser.add_argument('--input', dest='input_dir', required=True,
                        help='输入文件夹路径，包含蛋白CSV文件')
    
    parser.add_argument('--output', dest='output_dir', default='.',
                        help='输出文件夹路径，默认为当前目录')
    
    parser.add_argument('--metrics', nargs='+', default=[],
                        help='额外选择的指标，例如: r_i_glide_hbond r_i_glide_lipo')
    
    parser.add_argument('--weights', nargs='+', default=[],
                        help='指标权重设置，格式为"指标名:权重"，例如: r_i_docking_score:2.0 r_i_glide_hbond:1.5')
    
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        default='INFO', help='日志级别，默认为INFO')
    
    parser.add_argument('--gui', action='store_true',
                        help='启动图形用户界面模式')
    
    return parser.parse_args()

def parse_weights(weights_args: List[str]) -> Dict[str, float]:
    """解析权重参数
    
    Args:
        weights_args: 权重参数列表，格式为["指标名:权重", ...]
        
    Returns:
        权重字典
    """
    weights = {}
    for arg in weights_args:
        try:
            metric, weight_str = arg.split(':')
            weight = float(weight_str)
            weights[metric] = weight
        except ValueError:
            logger.warning(f"忽略无效的权重参数: {arg}")
    
    return weights

def run_cli():
    """运行命令行界面"""
    # 解析命令行参数
    args = parse_args()
    
    # 如果指定了GUI模式，启动GUI
    if args.gui:
        try:
            from src.ui.gui.main_window import run_gui
            run_gui()
            return
        except ImportError:
            logger.error("无法导入GUI模块，请确保已安装PyQt5")
            sys.exit(1)
    
    # 设置日志
    setup_logger(args.log_level, "docking_evaluator.log", "logs")
    
    # 验证输入目录
    if not is_valid_directory(args.input_dir):
        logger.error(f"输入目录不存在或不是有效目录: {args.input_dir}")
        sys.exit(1)
    
    # 确保输出目录存在
    ensure_directory_exists(args.output_dir)
    
    # 更新配置
    config.set("basic", "input_dir", args.input_dir)
    config.set("basic", "output_dir", args.output_dir)
    config.set("basic", "log_level", args.log_level)
    
    # 解析权重参数
    weights = parse_weights(args.weights)
    for metric, weight in weights.items():
        if metric in REQUIRED_METRICS:
            config.set("metrics", "required", {**config.get("metrics", "required"), metric: weight})
        elif metric in OPTIONAL_METRICS:
            config.set("metrics", "optional", {**config.get("metrics", "optional"), metric: weight})
    
    # 处理选择的指标
    selected_metrics = REQUIRED_METRICS.copy()  # 必选指标
    for metric in args.metrics:
        if metric in OPTIONAL_METRICS and metric not in selected_metrics:
            selected_metrics.append(metric)
    
    # 获取权重
    weights = config.get_metrics_weights()
    
    # 读取数据
    logger.info(f"开始读取数据，输入目录: {args.input_dir}")
    reader = DataReader()
    data, protein_dfs = reader.read_directory(args.input_dir)
    
    if data is None:
        logger.error("数据读取失败")
        sys.exit(1)
    
    # 预处理数据
    logger.info("开始预处理数据")
    processor = DataProcessor()
    processed_data = processor.preprocess_data(data)
    
    # 标准化数据
    logger.info("开始标准化数据")
    normalization_method = config.get("scoring", "normalization_method") or "min-max"
    normalized_data = processor.normalize_data(processed_data, normalization_method)
    
    # 排序构象
    logger.info("开始排序构象")
    ranker = Ranker()
    conformation_ranking = ranker.rank_conformations(normalized_data, selected_metrics, weights)
    
    # 排序蛋白质
    logger.info("开始排序蛋白质")
    protein_ranking = ranker.rank_proteins()
    
    # 输出结果
    logger.info("开始输出结果")
    writer = DataWriter()
    
    # 构象排序结果
    conformation_file = os.path.join(args.output_dir, config.get("output", "conformation_file"))
    writer.write_conformation_ranking(conformation_ranking, conformation_file, selected_metrics)
    
    # 蛋白质排序结果
    protein_file = os.path.join(args.output_dir, config.get("output", "protein_file"))
    writer.write_protein_ranking(protein_ranking, protein_file)
    
    logger.info("处理完成")
    print(f"构象排序结果已保存到: {conformation_file}")
    print(f"蛋白质排序结果已保存到: {protein_file}")

if __name__ == "__main__":
    run_cli() 