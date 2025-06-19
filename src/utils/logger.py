"""
日志工具模块
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

from src.config import LOG_LEVELS

def setup_logger(log_level: str = "INFO", log_file: Optional[str] = None, 
                 log_dir: Optional[str] = None) -> logging.Logger:
    """设置日志记录器
    
    Args:
        log_level: 日志级别，可选值为DEBUG, INFO, WARNING, ERROR, CRITICAL
        log_file: 日志文件名，如果为None则只输出到控制台
        log_dir: 日志文件目录，如果为None则使用当前目录
        
    Returns:
        配置好的日志记录器
    """
    # 获取根日志记录器
    logger = logging.getLogger()
    
    # 清除现有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 设置日志级别
    level = LOG_LEVELS.get(log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(module)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日志文件，创建文件处理器
    if log_file:
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, log_file)
        else:
            log_path = log_file
        
        # 使用RotatingFileHandler，限制文件大小为10MB，最多保留5个备份
        file_handler = RotatingFileHandler(
            log_path, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger() -> logging.Logger:
    """获取已配置的日志记录器
    
    Returns:
        日志记录器
    """
    return logging.getLogger() 