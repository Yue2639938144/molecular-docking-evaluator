"""
辅助函数模块，提供各种通用工具函数
"""

import os
import glob
from typing import List, Dict, Any, Optional, Tuple, Union
import pandas as pd
import logging

logger = logging.getLogger()

def list_csv_files(directory: str) -> List[str]:
    """列出目录中的所有CSV文件
    
    Args:
        directory: 目录路径
        
    Returns:
        CSV文件路径列表
    """
    pattern = os.path.join(directory, "*.csv")
    return glob.glob(pattern)

def get_protein_name_from_file(file_path: str) -> str:
    """从文件路径获取蛋白质名称
    
    Args:
        file_path: 文件路径
        
    Returns:
        蛋白质名称
    """
    # 获取文件名（不含扩展名）作为蛋白质名称
    base_name = os.path.basename(file_path)
    return os.path.splitext(base_name)[0]

def check_required_columns(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """检查DataFrame是否包含所有必需的列
    
    Args:
        df: 待检查的DataFrame
        required_columns: 必需列名列表
        
    Returns:
        如果包含所有必需列则返回True，否则返回False
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"缺少必需列: {', '.join(missing_columns)}")
        return False
    return True

def handle_special_values(df: pd.DataFrame, columns: List[str], 
                          special_value: float = 10000.0) -> pd.DataFrame:
    """处理特殊值（例如10000）
    
    Args:
        df: 待处理的DataFrame
        columns: 需要处理的列名列表
        special_value: 特殊值
        
    Returns:
        处理后的DataFrame
    """
    # 创建DataFrame的副本以避免修改原始数据
    result = df.copy()
    
    # 将特殊值替换为NaN
    for col in columns:
        if col in result.columns:
            result.loc[result[col] == special_value, col] = float('nan')
    
    return result

def ensure_directory_exists(directory: str) -> None:
    """确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
    """
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.info(f"创建目录: {directory}")

def format_float(value: float, precision: int = 4) -> str:
    """格式化浮点数为字符串
    
    Args:
        value: 浮点数
        precision: 小数位数
        
    Returns:
        格式化后的字符串
    """
    if pd.isna(value):
        return "N/A"
    
    format_str = f"{{:.{precision}f}}"
    return format_str.format(value)

def is_valid_directory(path: str) -> bool:
    """检查路径是否为有效目录
    
    Args:
        path: 路径
        
    Returns:
        如果是有效目录则返回True，否则返回False
    """
    return os.path.isdir(path) if path else False 