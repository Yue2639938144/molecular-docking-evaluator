# 分子对接结果优化排序工具使用说明

## 1. 软件概述

本工具用于处理Schrodinger Maestro软件Glide模块SP等级的多个蛋白分子对接结果文件，通过综合各评价指标，对小分子构象进行优度排序，并输出排序结果。工具支持命令行和图形界面两种操作模式，可以灵活选择参与排序的指标和调整各指标权重。

## 2. 安装方法

### 2.1 环境要求

- Python 3.8+
- 依赖包：pandas, numpy, scipy, openpyxl, PyQt5, matplotlib, pyyaml

### 2.2 安装步骤

1. 下载本软件包并解压
2. 打开命令行，进入解压后的目录
3. 安装依赖包：

```bash
pip install -r requirements.txt
```

## 3. 使用方法

### 3.1 图形界面模式

1. 运行以下命令启动图形界面：

```bash
python -m src.main --gui
```

2. 在"文件选择"选项卡中：
   - 点击"浏览..."按钮选择输入文件夹（包含蛋白CSV文件）
   - 点击"浏览..."按钮选择输出文件夹
   - 文件预览区域将显示输入文件夹中的CSV文件列表

3. 在"参数设置"选项卡中：
   - 必选指标（对接分数、Glide得分、模型能量、总能量）默认已选择，可调整权重
   - 可选指标可通过勾选复选框选择，并调整权重
   - 评分配置区域可设置对接分数、能量和可选指标的权重比例
   - 可选择标准化方法（min-max或z-score）

4. 点击底部的"开始计算"按钮开始处理数据
   - 处理过程中可在底部状态栏查看进度
   - 处理完成后会弹出提示窗口

5. 在"结果"选项卡中查看处理结果：
   - "构象排序结果"显示小分子构象的排序
   - "蛋白质排序结果"显示蛋白质的排序

6. 在"日志"选项卡中查看处理过程的日志信息

### 3.2 命令行模式

基本用法：

```bash
python -m src.main --input <输入文件夹> --output <输出文件夹> [--metrics <可选指标列表>] [--weights <权重设置>] [--log-level <日志级别>]
```

参数说明：

- `--input`：输入文件夹路径，包含蛋白CSV文件（必需）
- `--output`：输出文件夹路径，默认为当前目录
- `--metrics`：额外选择的指标，例如：r_i_glide_hbond r_i_glide_lipo
- `--weights`：指标权重设置，格式为"指标名:权重"，例如：r_i_docking_score:2.0 r_i_glide_hbond:1.5
- `--log-level`：日志级别，可选值为DEBUG、INFO、WARNING、ERROR，默认为INFO

示例：

```bash
# 基本用法
python -m src.main --input ./蛋白 --output ./结果

# 选择额外指标
python -m src.main --input ./蛋白 --output ./结果 --metrics r_i_glide_hbond r_i_glide_lipo

# 设置权重
python -m src.main --input ./蛋白 --output ./结果 --weights r_i_docking_score:2.0 r_i_glide_gscore:1.5

# 设置日志级别
python -m src.main --input ./蛋白 --output ./结果 --log-level DEBUG
```

## 4. 输入文件格式

输入文件为一个文件夹，其中包含若干个以蛋白质缩写命名的CSV文件。每个CSV文件应包含以下必要列：

- title：小分子编号
- i_i_glide_lignum：构象编号
- docking_status：对接状态
- r_i_docking_score：对接分数
- r_i_glide_gscore：Glide得分
- r_i_glide_emodel：模型能量
- r_i_glide_energy：总能量

此外，还可以包含以下可选列：

- r_i_glide_lipo：疏水作用得分
- r_i_glide_hbond：氢键得分
- r_i_glide_metal：金属键得分
- r_i_glide_rewards：奖励得分
- r_i_glide_evdw：范德华能量
- r_i_glide_ecoul：库仑相互作用能量
- r_i_glide_erotb：旋转键能量
- r_i_glide_esite：结合位点能量
- r_i_glide_einternal：配体内部能量

## 5. 输出文件

工具会生成两个Excel文件：

1. **构象排序结果**（默认文件名：conformation_ranking.xlsx）：
   - 小分子编号
   - 构象编号
   - 总对接效果指数
   - 对接分数相关指数
   - 能量相关指数
   - 最优蛋白
   - 各指标原始值

2. **蛋白质排序结果**（默认文件名：protein_ranking.xlsx）：
   - 蛋白质名称
   - 最优构象数量
   - 平均总对接效果指数
   - 平均对接分数相关指数
   - 平均能量相关指数

## 6. 评分规则

- 所有指标均为数值越低越优
- 排序优先级：负值 > 0 > 正值 > 空值
- 对接分数和Glide得分有任一等于10000的，认定为空值
- 综合评分由三部分组成：对接分数相关指数、能量相关指数和可选指标评分
- 默认权重配置：对接分数40%、能量40%、可选指标20%

## 7. 常见问题

1. **问题**：程序无法启动图形界面
   **解决方法**：确保已安装PyQt5库，可通过`pip install PyQt5`安装

2. **问题**：读取CSV文件失败
   **解决方法**：检查CSV文件编码格式，程序会尝试使用utf-8、gbk、gb2312和latin1编码读取

3. **问题**：处理数据时出现错误
   **解决方法**：查看日志文件（默认为logs/docking_evaluator.log）了解详细错误信息

4. **问题**：如何调整评分权重
   **解决方法**：在图形界面的"参数设置"选项卡中调整，或在命令行模式中使用--weights参数

## 8. 技术支持

如有问题或建议，请联系开发团队。 
