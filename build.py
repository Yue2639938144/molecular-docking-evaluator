#!/usr/bin/env python
"""
分子对接结果优化排序工具打包脚本
"""

import os
import sys
import shutil
import subprocess
import platform

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 检查PyInstaller是否已安装
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
    
    # 清理旧的构建文件
    for path in ["build", "dist"]:
        if os.path.exists(path):
            print(f"清理 {path} 目录...")
            shutil.rmtree(path)
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--name=分子对接结果优化排序工具",
        "--onefile",
        "--windowed",
        "--add-data=蛋白:蛋白",
        "--add-data=docs:docs",
        "--add-data=resources:resources",
        "--icon=resources/icon.ico" if os.path.exists("resources/icon.ico") else "",
        "run.py"
    ]
    
    # 根据平台调整命令
    if platform.system() == "Windows":
        cmd[4] = "--add-data=蛋白;蛋白"
        cmd[5] = "--add-data=docs;docs"
        cmd[6] = "--add-data=resources;resources"
    
    # 过滤掉空字符串
    cmd = [item for item in cmd if item]
    
    print("执行构建命令:", " ".join(cmd))
    subprocess.check_call(cmd)
    
    print("构建完成!")
    
    # 输出可执行文件路径
    if platform.system() == "Windows":
        exe_path = os.path.join("dist", "分子对接结果优化排序工具.exe")
    else:
        exe_path = os.path.join("dist", "分子对接结果优化排序工具")
    
    if os.path.exists(exe_path):
        print(f"可执行文件已生成: {exe_path}")
    else:
        print("构建失败，未找到可执行文件")

if __name__ == "__main__":
    build_executable() 