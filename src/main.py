"""
主程序入口模块
"""

import sys
import os
import logging
import argparse

from src.config import config
from src.utils.logger import setup_logger
from src.ui.cli import run_cli

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='分子对接结果优化排序工具')
    
    parser.add_argument('--gui', action='store_true',
                        help='启动图形用户界面模式')
    
    args, remaining_args = parser.parse_known_args()
    
    # 设置日志
    setup_logger("INFO", "docking_evaluator.log", "logs")
    
    # 根据模式选择启动GUI或CLI
    if args.gui:
        try:
            from src.ui.gui.main_window import run_gui
            run_gui()
        except ImportError:
            logging.error("无法导入GUI模块，请确保已安装PyQt5")
            sys.exit(1)
    else:
        # 将剩余参数传递给CLI
        sys.argv = [sys.argv[0]] + remaining_args
        run_cli()

if __name__ == "__main__":
    main() 