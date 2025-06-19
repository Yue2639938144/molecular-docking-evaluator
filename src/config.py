"""
配置文件，存储默认参数和配置选项
"""

import os
import logging
from typing import Dict, List, Any, Optional

# 默认配置
DEFAULT_CONFIG = {
    # 基本配置
    "basic": {
        "input_dir": "",
        "output_dir": "",
        "log_level": "INFO",
        "log_file": "docking_evaluator.log"
    },
    
    # 指标选择
    "metrics": {
        # 必选指标权重
        "required": {
            "r_i_docking_score": 1.0,
            "r_i_glide_gscore": 1.0,
            "r_i_glide_emodel": 1.0,
            "r_i_glide_energy": 1.0
        },
        
        # 可选指标及权重
        "optional": {
            "r_i_glide_lipo": 0.5,
            "r_i_glide_hbond": 0.7,
            "r_i_glide_metal": 0.3,
            "r_i_glide_rewards": 0.5,
            "r_i_glide_evdw": 0.5,
            "r_i_glide_ecoul": 0.5,
            "r_i_glide_erotb": 0.3,
            "r_i_glide_esite": 0.5,
            "r_i_glide_einternal": 0.3
        }
    },
    
    # 评分配置
    "scoring": {
        # 对接分数、能量分数和可选指标的权重比例
        "docking_weight": 0.4,
        "energy_weight": 0.4,
        "optional_weight": 0.2,
        
        # 标准化方法: min-max 或 z-score
        "normalization_method": "min-max"
    },
    
    # 输出配置
    "output": {
        "conformation_file": "conformation_ranking.xlsx",
        "protein_file": "protein_ranking.xlsx"
    }
}

# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# 必选指标列表
REQUIRED_METRICS = [
    "r_i_docking_score",
    "r_i_glide_gscore",
    "r_i_glide_emodel",
    "r_i_glide_energy"
]

# 可选指标列表
OPTIONAL_METRICS = [
    "r_i_glide_lipo",
    "r_i_glide_hbond",
    "r_i_glide_metal",
    "r_i_glide_rewards",
    "r_i_glide_evdw",
    "r_i_glide_ecoul",
    "r_i_glide_erotb",
    "r_i_glide_esite",
    "r_i_glide_einternal"
]

# 对接分数相关指标
DOCKING_METRICS = [
    "r_i_docking_score",
    "r_i_glide_gscore"
]

# 能量相关指标
ENERGY_METRICS = [
    "r_i_glide_emodel",
    "r_i_glide_energy"
]

# 配置类
class Config:
    """配置类，用于加载和管理配置"""
    
    def __init__(self):
        """初始化默认配置"""
        self.config = DEFAULT_CONFIG.copy()
    
    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """从字典更新配置
        
        Args:
            config_dict: 包含配置的字典
        """
        for section, values in config_dict.items():
            if section in self.config:
                if isinstance(values, dict) and isinstance(self.config[section], dict):
                    self.config[section].update(values)
                else:
                    self.config[section] = values
    
    def update_from_yaml(self, yaml_file: str) -> None:
        """从YAML文件加载配置
        
        Args:
            yaml_file: YAML配置文件路径
        """
        try:
            import yaml
            with open(yaml_file, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
                if config_dict:
                    self.update_from_dict(config_dict)
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
    
    def get(self, section: str, key: Optional[str] = None) -> Any:
        """获取配置值
        
        Args:
            section: 配置节
            key: 配置键，如果为None则返回整个节
            
        Returns:
            配置值
        """
        if section not in self.config:
            return None
        
        if key is None:
            return self.config[section]
        
        if key in self.config[section]:
            return self.config[section][key]
        
        return None
    
    def set(self, section: str, key: str, value: Any) -> None:
        """设置配置值
        
        Args:
            section: 配置节
            key: 配置键
            value: 配置值
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    def save_to_yaml(self, yaml_file: str) -> None:
        """保存配置到YAML文件
        
        Args:
            yaml_file: YAML配置文件路径
        """
        try:
            import yaml
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")
    
    def get_selected_metrics(self) -> List[str]:
        """获取选中的指标列表
        
        Returns:
            选中的指标列表
        """
        # 必选指标总是包含
        selected = REQUIRED_METRICS.copy()
        
        # 检查可选指标
        optional_metrics = self.get("metrics", "optional")
        if optional_metrics:
            for metric, weight in optional_metrics.items():
                if weight > 0 and metric not in selected:
                    selected.append(metric)
        
        return selected
    
    def get_metrics_weights(self) -> Dict[str, float]:
        """获取指标权重字典
        
        Returns:
            指标权重字典
        """
        weights = {}
        
        # 必选指标权重
        required_metrics = self.get("metrics", "required")
        if required_metrics:
            weights.update(required_metrics)
        
        # 可选指标权重
        optional_metrics = self.get("metrics", "optional")
        if optional_metrics:
            weights.update(optional_metrics)
        
        return weights

# 全局配置实例
config = Config() 