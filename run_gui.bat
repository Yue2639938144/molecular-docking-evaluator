@echo off
echo 正在启动分子对接结果优化排序工具图形界面...
python run.py --gui
if errorlevel 1 (
    echo 程序运行出错，按任意键退出...
    pause > nul
) 