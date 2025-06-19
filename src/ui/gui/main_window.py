"""
图形用户界面主窗口模块
"""

import os
import sys
import logging
from typing import List, Dict, Optional, Any, Tuple
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QCheckBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QTabWidget, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QProgressBar, QMessageBox,
    QComboBox, QSpinBox, QSlider, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon

from src.config import config, REQUIRED_METRICS, OPTIONAL_METRICS
from src.utils.logger import setup_logger
from src.utils.helpers import ensure_directory_exists, is_valid_directory
from src.data.reader import DataReader
from src.data.processor import DataProcessor
from src.core.scorer import Scorer
from src.core.ranker import Ranker
from src.data.writer import DataWriter

logger = logging.getLogger()

# 工作线程，用于后台处理数据
class WorkerThread(QThread):
    """工作线程，用于后台处理数据"""
    
    # 信号定义
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    
    def __init__(self, input_dir: str, output_dir: str, selected_metrics: List[str], 
                weights: Dict[str, float]):
        """初始化工作线程
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            selected_metrics: 选择的指标
            weights: 权重字典
        """
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.selected_metrics = selected_metrics
        self.weights = weights
    
    def run(self):
        """运行线程"""
        try:
            # 读取数据
            self.status_signal.emit("正在读取数据...")
            self.progress_signal.emit(10)
            
            reader = DataReader()
            data, protein_dfs = reader.read_directory(self.input_dir)
            
            if data is None:
                self.error_signal.emit("数据读取失败")
                return
            
            # 预处理数据
            self.status_signal.emit("正在预处理数据...")
            self.progress_signal.emit(30)
            
            processor = DataProcessor()
            processed_data = processor.preprocess_data(data)
            
            # 标准化数据
            self.status_signal.emit("正在标准化数据...")
            self.progress_signal.emit(50)
            
            normalization_method = config.get("scoring", "normalization_method") or "min-max"
            normalized_data = processor.normalize_data(processed_data, normalization_method)
            
            # 排序构象
            self.status_signal.emit("正在排序构象...")
            self.progress_signal.emit(70)
            
            ranker = Ranker()
            conformation_ranking = ranker.rank_conformations(
                normalized_data, self.selected_metrics, self.weights
            )
            
            # 排序蛋白质
            self.status_signal.emit("正在排序蛋白质...")
            self.progress_signal.emit(80)
            
            protein_ranking = ranker.rank_proteins()
            
            # 输出结果
            self.status_signal.emit("正在输出结果...")
            self.progress_signal.emit(90)
            
            writer = DataWriter()
            
            # 构象排序结果
            conformation_file = os.path.join(
                self.output_dir, config.get("output", "conformation_file")
            )
            writer.write_conformation_ranking(
                conformation_ranking, conformation_file, self.selected_metrics
            )
            
            # 蛋白质排序结果
            protein_file = os.path.join(
                self.output_dir, config.get("output", "protein_file")
            )
            writer.write_protein_ranking(protein_ranking, protein_file)
            
            self.progress_signal.emit(100)
            self.status_signal.emit("处理完成")
            
            # 发送结果信号
            result = {
                'conformation_ranking': conformation_ranking,
                'protein_ranking': protein_ranking,
                'conformation_file': conformation_file,
                'protein_file': protein_file
            }
            self.finished_signal.emit(result)
            
        except Exception as e:
            logger.exception("处理数据时出错")
            self.error_signal.emit(f"处理数据时出错: {str(e)}")

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("分子对接结果优化排序工具")
        self.setMinimumSize(900, 700)
        
        # 初始化成员变量
        self.input_dir = ""
        self.output_dir = ""
        self.selected_metrics = REQUIRED_METRICS.copy()
        self.weights = config.get_metrics_weights()
        self.worker_thread = None
        self.conformation_ranking = []
        self.protein_ranking = []
        
        # 创建界面
        self.create_ui()
        
        # 更新界面状态
        self.update_ui_state()
    
    def create_ui(self):
        """创建用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 创建选项卡页面
        self.create_input_tab(tab_widget)
        self.create_params_tab(tab_widget)
        self.create_results_tab(tab_widget)
        self.create_log_tab(tab_widget)
        
        # 底部状态区域
        bottom_layout = QHBoxLayout()
        
        # 状态标签
        self.status_label = QLabel("就绪")
        bottom_layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        bottom_layout.addWidget(self.progress_bar)
        
        # 运行按钮
        self.run_button = QPushButton("开始计算")
        self.run_button.clicked.connect(self.run_processing)
        bottom_layout.addWidget(self.run_button)
        
        main_layout.addLayout(bottom_layout)
    
    def create_input_tab(self, tab_widget):
        """创建输入选项卡
        
        Args:
            tab_widget: 选项卡部件
        """
        input_tab = QWidget()
        layout = QVBoxLayout(input_tab)
        
        # 输入目录选择
        input_group = QGroupBox("输入设置")
        input_form = QFormLayout(input_group)
        
        input_layout = QHBoxLayout()
        self.input_dir_label = QLabel("未选择")
        input_layout.addWidget(self.input_dir_label)
        
        input_button = QPushButton("浏览...")
        input_button.clicked.connect(self.browse_input_dir)
        input_layout.addWidget(input_button)
        
        input_form.addRow("输入文件夹:", input_layout)
        
        # 输出目录选择
        output_layout = QHBoxLayout()
        self.output_dir_label = QLabel("未选择")
        output_layout.addWidget(self.output_dir_label)
        
        output_button = QPushButton("浏览...")
        output_button.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(output_button)
        
        input_form.addRow("输出文件夹:", output_layout)
        
        layout.addWidget(input_group)
        
        # 文件预览区域
        preview_group = QGroupBox("文件预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.file_list = QTextEdit()
        self.file_list.setReadOnly(True)
        preview_layout.addWidget(self.file_list)
        
        layout.addWidget(preview_group)
        
        tab_widget.addTab(input_tab, "文件选择")
    
    def create_params_tab(self, tab_widget):
        """创建参数选项卡
        
        Args:
            tab_widget: 选项卡部件
        """
        params_tab = QWidget()
        layout = QVBoxLayout(params_tab)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 必选指标组
        required_group = QGroupBox("必选指标")
        required_layout = QVBoxLayout(required_group)
        
        for metric in REQUIRED_METRICS:
            metric_layout = QHBoxLayout()
            
            # 复选框（禁用，因为是必选的）
            check_box = QCheckBox(metric)
            check_box.setChecked(True)
            check_box.setEnabled(False)
            metric_layout.addWidget(check_box)
            
            # 权重调整
            weight_label = QLabel("权重:")
            metric_layout.addWidget(weight_label)
            
            weight_spin = QDoubleSpinBox()
            weight_spin.setRange(0.1, 10.0)
            weight_spin.setSingleStep(0.1)
            weight_spin.setValue(self.weights.get(metric, 1.0))
            weight_spin.valueChanged.connect(
                lambda value, m=metric: self.update_weight(m, value)
            )
            metric_layout.addWidget(weight_spin)
            
            required_layout.addLayout(metric_layout)
        
        scroll_layout.addWidget(required_group)
        
        # 可选指标组
        optional_group = QGroupBox("可选指标")
        optional_layout = QVBoxLayout(optional_group)
        
        for metric in OPTIONAL_METRICS:
            metric_layout = QHBoxLayout()
            
            # 复选框
            check_box = QCheckBox(metric)
            check_box.setChecked(metric in self.selected_metrics)
            check_box.stateChanged.connect(
                lambda state, m=metric: self.toggle_metric(m, state)
            )
            metric_layout.addWidget(check_box)
            
            # 权重调整
            weight_label = QLabel("权重:")
            metric_layout.addWidget(weight_label)
            
            weight_spin = QDoubleSpinBox()
            weight_spin.setRange(0.1, 10.0)
            weight_spin.setSingleStep(0.1)
            weight_spin.setValue(self.weights.get(metric, 0.5))
            weight_spin.valueChanged.connect(
                lambda value, m=metric: self.update_weight(m, value)
            )
            metric_layout.addWidget(weight_spin)
            
            optional_layout.addLayout(metric_layout)
        
        scroll_layout.addWidget(optional_group)
        
        # 评分配置组
        scoring_group = QGroupBox("评分配置")
        scoring_layout = QFormLayout(scoring_group)
        
        # 对接分数权重
        self.docking_weight_spin = QDoubleSpinBox()
        self.docking_weight_spin.setRange(0.1, 1.0)
        self.docking_weight_spin.setSingleStep(0.1)
        self.docking_weight_spin.setValue(config.get("scoring", "docking_weight") or 0.4)
        self.docking_weight_spin.valueChanged.connect(self.update_scoring_weights)
        scoring_layout.addRow("对接分数权重:", self.docking_weight_spin)
        
        # 能量权重
        self.energy_weight_spin = QDoubleSpinBox()
        self.energy_weight_spin.setRange(0.1, 1.0)
        self.energy_weight_spin.setSingleStep(0.1)
        self.energy_weight_spin.setValue(config.get("scoring", "energy_weight") or 0.4)
        self.energy_weight_spin.valueChanged.connect(self.update_scoring_weights)
        scoring_layout.addRow("能量权重:", self.energy_weight_spin)
        
        # 可选指标权重
        self.optional_weight_spin = QDoubleSpinBox()
        self.optional_weight_spin.setRange(0.0, 1.0)
        self.optional_weight_spin.setSingleStep(0.1)
        self.optional_weight_spin.setValue(config.get("scoring", "optional_weight") or 0.2)
        self.optional_weight_spin.valueChanged.connect(self.update_scoring_weights)
        scoring_layout.addRow("可选指标权重:", self.optional_weight_spin)
        
        # 标准化方法
        self.normalization_combo = QComboBox()
        self.normalization_combo.addItems(["min-max", "z-score"])
        current_method = config.get("scoring", "normalization_method") or "min-max"
        self.normalization_combo.setCurrentText(current_method)
        self.normalization_combo.currentTextChanged.connect(self.update_normalization_method)
        scoring_layout.addRow("标准化方法:", self.normalization_combo)
        
        scroll_layout.addWidget(scoring_group)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        tab_widget.addTab(params_tab, "参数设置")
    
    def create_results_tab(self, tab_widget):
        """创建结果选项卡
        
        Args:
            tab_widget: 选项卡部件
        """
        results_tab = QTabWidget()
        
        # 构象排序结果选项卡
        conf_tab = QWidget()
        conf_layout = QVBoxLayout(conf_tab)
        
        self.conf_table = QTableWidget()
        self.conf_table.setColumnCount(6)  # 基本列
        self.conf_table.setHorizontalHeaderLabels([
            "小分子编号", "构象编号", "总对接效果指数", 
            "对接分数相关指数", "能量相关指数", "最优蛋白"
        ])
        self.conf_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        conf_layout.addWidget(self.conf_table)
        
        results_tab.addTab(conf_tab, "构象排序结果")
        
        # 蛋白质排序结果选项卡
        protein_tab = QWidget()
        protein_layout = QVBoxLayout(protein_tab)
        
        self.protein_table = QTableWidget()
        self.protein_table.setColumnCount(5)
        self.protein_table.setHorizontalHeaderLabels([
            "蛋白质名称", "最优构象数量", "平均总对接效果指数", 
            "平均对接分数相关指数", "平均能量相关指数"
        ])
        self.protein_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        protein_layout.addWidget(self.protein_table)
        
        results_tab.addTab(protein_tab, "蛋白质排序结果")
        
        tab_widget.addTab(results_tab, "结果")
    
    def create_log_tab(self, tab_widget):
        """创建日志选项卡
        
        Args:
            tab_widget: 选项卡部件
        """
        log_tab = QWidget()
        layout = QVBoxLayout(log_tab)
        
        # 日志级别选择
        log_level_layout = QHBoxLayout()
        log_level_label = QLabel("日志级别:")
        log_level_layout.addWidget(log_level_label)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText(config.get("basic", "log_level") or "INFO")
        self.log_level_combo.currentTextChanged.connect(self.update_log_level)
        log_level_layout.addWidget(self.log_level_combo)
        
        log_level_layout.addStretch()
        
        # 清除按钮
        clear_button = QPushButton("清除日志")
        clear_button.clicked.connect(self.clear_log)
        log_level_layout.addWidget(clear_button)
        
        layout.addLayout(log_level_layout)
        
        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        tab_widget.addTab(log_tab, "日志")
    
    def browse_input_dir(self):
        """浏览输入目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择输入文件夹", "", QFileDialog.ShowDirsOnly
        )
        
        if dir_path:
            self.input_dir = dir_path
            self.input_dir_label.setText(dir_path)
            self.update_ui_state()
            self.update_file_preview()
    
    def browse_output_dir(self):
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择输出文件夹", "", QFileDialog.ShowDirsOnly
        )
        
        if dir_path:
            self.output_dir = dir_path
            self.output_dir_label.setText(dir_path)
            self.update_ui_state()
    
    def update_file_preview(self):
        """更新文件预览"""
        if not self.input_dir or not os.path.isdir(self.input_dir):
            self.file_list.setText("未选择有效的输入文件夹")
            return
        
        try:
            files = [f for f in os.listdir(self.input_dir) 
                    if f.endswith('.csv') and os.path.isfile(os.path.join(self.input_dir, f))]
            
            if not files:
                self.file_list.setText("输入文件夹中没有CSV文件")
                return
            
            preview_text = f"找到 {len(files)} 个CSV文件:\n\n"
            for file in files:
                preview_text += f"- {file}\n"
            
            self.file_list.setText(preview_text)
            
        except Exception as e:
            self.file_list.setText(f"读取文件列表时出错: {str(e)}")
    
    def toggle_metric(self, metric: str, state: int):
        """切换指标选择状态
        
        Args:
            metric: 指标名称
            state: 复选框状态
        """
        if state == Qt.Checked:
            if metric not in self.selected_metrics:
                self.selected_metrics.append(metric)
        else:
            if metric in self.selected_metrics:
                self.selected_metrics.remove(metric)
    
    def update_weight(self, metric: str, value: float):
        """更新指标权重
        
        Args:
            metric: 指标名称
            value: 权重值
        """
        self.weights[metric] = value
    
    def update_scoring_weights(self):
        """更新评分权重配置"""
        docking_weight = self.docking_weight_spin.value()
        energy_weight = self.energy_weight_spin.value()
        optional_weight = self.optional_weight_spin.value()
        
        # 确保权重和为1
        total = docking_weight + energy_weight + optional_weight
        if abs(total - 1.0) > 0.01:
            # 归一化
            docking_weight /= total
            energy_weight /= total
            optional_weight /= total
            
            # 更新界面
            self.docking_weight_spin.blockSignals(True)
            self.energy_weight_spin.blockSignals(True)
            self.optional_weight_spin.blockSignals(True)
            
            self.docking_weight_spin.setValue(docking_weight)
            self.energy_weight_spin.setValue(energy_weight)
            self.optional_weight_spin.setValue(optional_weight)
            
            self.docking_weight_spin.blockSignals(False)
            self.energy_weight_spin.blockSignals(False)
            self.optional_weight_spin.blockSignals(False)
        
        # 更新配置
        config.set("scoring", "docking_weight", docking_weight)
        config.set("scoring", "energy_weight", energy_weight)
        config.set("scoring", "optional_weight", optional_weight)
    
    def update_normalization_method(self, method: str):
        """更新标准化方法
        
        Args:
            method: 标准化方法
        """
        config.set("scoring", "normalization_method", method)
    
    def update_log_level(self, level: str):
        """更新日志级别
        
        Args:
            level: 日志级别
        """
        config.set("basic", "log_level", level)
        setup_logger(level, "docking_evaluator.log", "logs")
    
    def clear_log(self):
        """清除日志"""
        self.log_text.clear()
    
    def update_ui_state(self):
        """更新界面状态"""
        has_input = bool(self.input_dir) and os.path.isdir(self.input_dir)
        has_output = bool(self.output_dir) and os.path.isdir(self.output_dir)
        
        self.run_button.setEnabled(has_input and has_output)
    
    def run_processing(self):
        """运行数据处理"""
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, "警告", "处理任务正在进行中")
            return
        
        # 确保目录有效
        if not is_valid_directory(self.input_dir):
            QMessageBox.critical(self, "错误", "输入目录无效")
            return
        
        ensure_directory_exists(self.output_dir)
        
        # 更新配置
        config.set("basic", "input_dir", self.input_dir)
        config.set("basic", "output_dir", self.output_dir)
        
        # 设置日志
        log_level = self.log_level_combo.currentText()
        setup_logger(log_level, "docking_evaluator.log", "logs")
        
        # 创建并启动工作线程
        self.worker_thread = WorkerThread(
            self.input_dir, self.output_dir, 
            self.selected_metrics, self.weights
        )
        
        # 连接信号
        self.worker_thread.progress_signal.connect(self.update_progress)
        self.worker_thread.status_signal.connect(self.update_status)
        self.worker_thread.error_signal.connect(self.show_error)
        self.worker_thread.finished_signal.connect(self.process_finished)
        
        # 禁用运行按钮
        self.run_button.setEnabled(False)
        
        # 启动线程
        self.worker_thread.start()
    
    def update_progress(self, value: int):
        """更新进度条
        
        Args:
            value: 进度值
        """
        self.progress_bar.setValue(value)
    
    def update_status(self, status: str):
        """更新状态标签
        
        Args:
            status: 状态文本
        """
        self.status_label.setText(status)
        self.log_text.append(f"[INFO] {status}")
    
    def show_error(self, error: str):
        """显示错误信息
        
        Args:
            error: 错误文本
        """
        QMessageBox.critical(self, "错误", error)
        self.log_text.append(f"[ERROR] {error}")
        self.run_button.setEnabled(True)
    
    def process_finished(self, result: Dict[str, Any]):
        """处理完成回调
        
        Args:
            result: 处理结果
        """
        # 保存结果
        self.conformation_ranking = result['conformation_ranking']
        self.protein_ranking = result['protein_ranking']
        
        # 更新结果表格
        self.update_result_tables()
        
        # 显示完成消息
        QMessageBox.information(
            self, "完成", 
            f"处理完成！\n\n"
            f"构象排序结果已保存到: {result['conformation_file']}\n"
            f"蛋白质排序结果已保存到: {result['protein_file']}"
        )
        
        # 启用运行按钮
        self.run_button.setEnabled(True)
    
    def update_result_tables(self):
        """更新结果表格"""
        # 更新构象表格
        self.conf_table.setRowCount(len(self.conformation_ranking))
        
        for row, conf in enumerate(self.conformation_ranking):
            self.conf_table.setItem(row, 0, QTableWidgetItem(str(conf['title'])))
            self.conf_table.setItem(row, 1, QTableWidgetItem(str(conf['lignum'])))
            self.conf_table.setItem(row, 2, QTableWidgetItem(f"{conf['total_score']:.4f}"))
            self.conf_table.setItem(row, 3, QTableWidgetItem(f"{conf['docking_score']:.4f}"))
            self.conf_table.setItem(row, 4, QTableWidgetItem(f"{conf['energy_score']:.4f}"))
            self.conf_table.setItem(row, 5, QTableWidgetItem(conf['best_protein']))
        
        # 更新蛋白质表格
        self.protein_table.setRowCount(len(self.protein_ranking))
        
        for row, protein in enumerate(self.protein_ranking):
            self.protein_table.setItem(row, 0, QTableWidgetItem(protein['protein_name']))
            self.protein_table.setItem(row, 1, QTableWidgetItem(str(protein['best_count'])))
            self.protein_table.setItem(row, 2, QTableWidgetItem(f"{protein['avg_total_score']:.4f}"))
            self.protein_table.setItem(row, 3, QTableWidgetItem(f"{protein['avg_docking_score']:.4f}"))
            self.protein_table.setItem(row, 4, QTableWidgetItem(f"{protein['avg_energy_score']:.4f}"))

def run_gui():
    """运行图形用户界面"""
    # 设置日志
    setup_logger("INFO", "docking_evaluator.log", "logs")
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_()) 