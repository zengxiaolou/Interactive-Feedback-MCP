"""
Data Visualization Components for Interactive Feedback MCP
数据可视化组件 - 支持反馈数据的图表展示和统计分析
"""

import sys
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QGridLayout, QPushButton, QComboBox,
    QDateEdit, QSpinBox, QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, QTimer, Signal, QDate
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPixmap
from PySide6.QtCharts import (
    QChart, QChartView, QPieSeries, QBarSeries, QBarSet,
    QLineSeries, QScatterSeries, QValueAxis, QBarCategoryAxis,
    QLegend
)

@dataclass
class FeedbackData:
    """反馈数据结构"""
    timestamp: datetime
    user_id: str
    message: str
    selected_options: List[str]
    custom_input: str
    response_time: float
    satisfaction_score: int = 0  # 1-5分
    category: str = "general"

@dataclass
class AnalyticsMetrics:
    """分析指标数据"""
    total_feedback: int = 0
    avg_response_time: float = 0.0
    avg_satisfaction: float = 0.0
    most_selected_option: str = ""
    peak_usage_hour: int = 0
    daily_growth_rate: float = 0.0
    user_retention_rate: float = 0.0

class ChartWidget(QWidget):
    """图表基础组件"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.chart = QChart()
        self.chart_view = QChartView(self.chart)
        self.setup_ui()
        self.apply_glassmorphism_style()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题
        if self.title:
            title_label = QLabel(self.title)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #FFFFFF;
                    margin-bottom: 10px;
                }
            """)
            layout.addWidget(title_label)
        
        # 图表视图
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(self.chart_view)
        
        # 设置图表样式
        self.chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        self.chart.setBackgroundBrush(QBrush(QColor(0, 0, 0, 0)))  # 透明背景
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
    
    def apply_glassmorphism_style(self):
        """应用毛玻璃样式"""
        self.setStyleSheet("""
            ChartWidget {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                backdrop-filter: blur(10px);
            }
        """)
        
        # 图表视图样式
        self.chart_view.setStyleSheet("""
            QChartView {
                background: transparent;
                border: none;
            }
        """)

class PieChartWidget(ChartWidget):
    """饼图组件"""
    
    def __init__(self, title: str = "饼图", parent=None):
        super().__init__(title, parent)
        self.pie_series = QPieSeries()
        self.chart.addSeries(self.pie_series)
    
    def update_data(self, data: Dict[str, int]):
        """更新饼图数据"""
        self.pie_series.clear()
        
        total = sum(data.values())
        if total == 0:
            return
        
        # 添加数据片段
        colors = [
            QColor("#2196F3"), QColor("#4CAF50"), QColor("#FF9800"),
            QColor("#F44336"), QColor("#9C27B0"), QColor("#00BCD4")
        ]
        
        for i, (label, value) in enumerate(data.items()):
            slice_obj = self.pie_series.append(f"{label}\n({value})", value)
            percentage = (value / total) * 100
            slice_obj.setLabelVisible(True)
            slice_obj.setLabel(f"{label}\n{percentage:.1f}%")
            
            # 设置颜色
            slice_obj.setBrush(QBrush(colors[i % len(colors)]))

class BarChartWidget(ChartWidget):
    """柱状图组件"""
    
    def __init__(self, title: str = "柱状图", parent=None):
        super().__init__(title, parent)
        self.bar_series = QBarSeries()
        self.chart.addSeries(self.bar_series)
        
        # 设置坐标轴
        self.axis_x = QBarCategoryAxis()
        self.axis_y = QValueAxis()
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        self.bar_series.attachAxis(self.axis_x)
        self.bar_series.attachAxis(self.axis_y)
    
    def update_data(self, categories: List[str], data: Dict[str, List[int]]):
        """更新柱状图数据"""
        self.bar_series.clear()
        
        # 设置类别
        self.axis_x.clear()
        self.axis_x.append(categories)
        
        # 添加数据集
        colors = [QColor("#2196F3"), QColor("#4CAF50"), QColor("#FF9800")]
        for i, (series_name, values) in enumerate(data.items()):
            bar_set = QBarSet(series_name)
            bar_set.append(values)
            bar_set.setColor(colors[i % len(colors)])
            self.bar_series.append(bar_set)
        
        # 设置Y轴范围
        if data:
            max_value = max(max(values) for values in data.values())
            self.axis_y.setRange(0, max_value * 1.1)

class LineChartWidget(ChartWidget):
    """折线图组件"""
    
    def __init__(self, title: str = "折线图", parent=None):
        super().__init__(title, parent)
        self.line_series = QLineSeries()
        self.chart.addSeries(self.line_series)
        
        # 设置坐标轴
        self.axis_x = QValueAxis()
        self.axis_y = QValueAxis()
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        self.line_series.attachAxis(self.axis_x)
        self.line_series.attachAxis(self.axis_y)
    
    def update_data(self, data_points: List[Tuple[float, float]]):
        """更新折线图数据"""
        self.line_series.clear()
        
        if not data_points:
            return
        
        # 添加数据点
        for x, y in data_points:
            self.line_series.append(x, y)
        
        # 设置坐标轴范围
        x_values = [point[0] for point in data_points]
        y_values = [point[1] for point in data_points]
        
        self.axis_x.setRange(min(x_values), max(x_values))
        self.axis_y.setRange(min(y_values) * 0.9, max(y_values) * 1.1)
        
        # 设置线条样式
        pen = QPen(QColor("#2196F3"))
        pen.setWidth(3)
        self.line_series.setPen(pen)

class MetricsWidget(QWidget):
    """指标展示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.metrics = AnalyticsMetrics()
        self.setup_ui()
        self.apply_glassmorphism_style()
    
    def setup_ui(self):
        """设置UI"""
        layout = QGridLayout(self)
        layout.setSpacing(15)
        
        # 创建指标卡片
        self.metric_cards = {}
        metrics_config = [
            ("total_feedback", "📊 总反馈数", "0", "#2196F3"),
            ("avg_response_time", "⏱️ 平均响应时间", "0ms", "#4CAF50"),
            ("avg_satisfaction", "😊 平均满意度", "0.0", "#FF9800"),
            ("most_selected_option", "🎯 热门选项", "无", "#F44336"),
            ("peak_usage_hour", "📈 使用高峰", "0时", "#9C27B0"),
            ("daily_growth_rate", "📊 日增长率", "0%", "#00BCD4")
        ]
        
        for i, (key, title, default_value, color) in enumerate(metrics_config):
            card = self.create_metric_card(title, default_value, color)
            self.metric_cards[key] = card
            row, col = divmod(i, 3)
            layout.addWidget(card, row, col)
    
    def create_metric_card(self, title: str, value: str, color: str) -> QFrame:
        """创建指标卡片"""
        card = QFrame()
        card.setFixedHeight(120)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
        """)
        
        # 数值
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        
        # 应用卡片样式
        card.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid {color}40;
                border-radius: 12px;
                backdrop-filter: blur(10px);
            }}
            QFrame:hover {{
                background: rgba(255, 255, 255, 0.15);
                border-color: {color}80;
            }}
        """)
        
        return card
    
    def update_metrics(self, metrics: AnalyticsMetrics):
        """更新指标数据"""
        self.metrics = metrics
        
        # 更新各个指标卡片
        updates = {
            "total_feedback": str(metrics.total_feedback),
            "avg_response_time": f"{metrics.avg_response_time:.0f}ms",
            "avg_satisfaction": f"{metrics.avg_satisfaction:.1f}",
            "most_selected_option": metrics.most_selected_option or "无",
            "peak_usage_hour": f"{metrics.peak_usage_hour}时",
            "daily_growth_rate": f"{metrics.daily_growth_rate:+.1f}%"
        }
        
        for key, value in updates.items():
            if key in self.metric_cards:
                card = self.metric_cards[key]
                value_label = card.findChild(QLabel)
                if value_label:
                    # 找到数值标签（第二个QLabel）
                    labels = card.findChildren(QLabel)
                    if len(labels) >= 2:
                        labels[1].setText(value)
    
    def apply_glassmorphism_style(self):
        """应用毛玻璃样式"""
        self.setStyleSheet("""
            MetricsWidget {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
            }
        """)

class DataVisualizationWidget(QWidget):
    """数据可视化主组件"""
    
    data_updated = Signal(dict)  # 数据更新信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.feedback_data: List[FeedbackData] = []
        self.setup_ui()
        self.setup_timer()
        self.load_sample_data()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题和控制面板
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📊 数据可视化分析")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #FFFFFF;
                margin-bottom: 10px;
            }
        """)
        
        # 控制按钮
        self.refresh_btn = QPushButton("🔄 刷新数据")
        self.export_btn = QPushButton("📁 导出报告")
        self.settings_btn = QPushButton("⚙️ 设置")
        
        for btn in [self.refresh_btn, self.export_btn, self.settings_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(33, 150, 243, 0.8);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgba(33, 150, 243, 1.0);
                }
                QPushButton:pressed {
                    background: rgba(21, 101, 192, 1.0);
                }
            """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_btn)
        header_layout.addWidget(self.export_btn)
        header_layout.addWidget(self.settings_btn)
        
        layout.addLayout(header_layout)
        
        # 指标面板
        self.metrics_widget = MetricsWidget()
        layout.addWidget(self.metrics_widget)
        
        # 图表区域
        charts_layout = QGridLayout()
        charts_layout.setSpacing(15)
        
        # 创建各种图表
        self.pie_chart = PieChartWidget("📊 选项分布")
        self.bar_chart = BarChartWidget("📈 时间趋势")
        self.line_chart = LineChartWidget("📉 响应时间趋势")
        self.satisfaction_chart = PieChartWidget("😊 满意度分布")
        
        # 布局图表
        charts_layout.addWidget(self.pie_chart, 0, 0)
        charts_layout.addWidget(self.bar_chart, 0, 1)
        charts_layout.addWidget(self.line_chart, 1, 0)
        charts_layout.addWidget(self.satisfaction_chart, 1, 1)
        
        layout.addLayout(charts_layout)
        
        # 连接信号
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.export_btn.clicked.connect(self.export_report)
        self.settings_btn.clicked.connect(self.show_settings)
    
    def setup_timer(self):
        """设置定时器"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.start(30000)  # 30秒更新一次
    
    def load_sample_data(self):
        """加载示例数据"""
        import random
        from datetime import datetime, timedelta
        
        # 生成示例反馈数据
        options = [
            "🎨 切换到现代毛玻璃主题",
            "🌟 切换到经典毛玻璃主题", 
            "🌐 切换语言设置",
            "📁 导出当前配置",
            "📂 导入配置文件",
            "🔄 重置为默认配置"
        ]
        
        base_time = datetime.now() - timedelta(days=7)
        
        for i in range(100):
            feedback = FeedbackData(
                timestamp=base_time + timedelta(
                    days=random.randint(0, 7),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                ),
                user_id=f"user_{random.randint(1, 50)}",
                message="示例反馈消息",
                selected_options=random.sample(options, random.randint(1, 3)),
                custom_input=f"自定义输入 {i}",
                response_time=random.uniform(50, 500),
                satisfaction_score=random.randint(1, 5),
                category=random.choice(["ui", "performance", "feature", "bug"])
            )
            self.feedback_data.append(feedback)
        
        # 初始更新
        self.refresh_data()
    
    def add_feedback_data(self, feedback: FeedbackData):
        """添加反馈数据"""
        self.feedback_data.append(feedback)
        self.data_updated.emit({"action": "add", "data": feedback})
    
    def refresh_data(self):
        """刷新数据显示"""
        if not self.feedback_data:
            return
        
        # 计算指标
        metrics = self.calculate_metrics()
        self.metrics_widget.update_metrics(metrics)
        
        # 更新图表
        self.update_charts()
        
        print(f"📊 数据已刷新 - 共 {len(self.feedback_data)} 条反馈")
    
    def calculate_metrics(self) -> AnalyticsMetrics:
        """计算分析指标"""
        if not self.feedback_data:
            return AnalyticsMetrics()
        
        # 基础指标
        total_feedback = len(self.feedback_data)
        avg_response_time = sum(f.response_time for f in self.feedback_data) / total_feedback
        avg_satisfaction = sum(f.satisfaction_score for f in self.feedback_data) / total_feedback
        
        # 最热门选项
        option_counts = {}
        for feedback in self.feedback_data:
            for option in feedback.selected_options:
                option_counts[option] = option_counts.get(option, 0) + 1
        
        most_selected_option = max(option_counts.items(), key=lambda x: x[1])[0] if option_counts else ""
        
        # 使用高峰时间
        hour_counts = {}
        for feedback in self.feedback_data:
            hour = feedback.timestamp.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_usage_hour = max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else 0
        
        # 日增长率（简化计算）
        recent_data = [f for f in self.feedback_data if f.timestamp > datetime.now() - timedelta(days=2)]
        older_data = [f for f in self.feedback_data if f.timestamp <= datetime.now() - timedelta(days=2)]
        
        daily_growth_rate = 0.0
        if older_data:
            daily_growth_rate = ((len(recent_data) - len(older_data)) / len(older_data)) * 100
        
        return AnalyticsMetrics(
            total_feedback=total_feedback,
            avg_response_time=avg_response_time,
            avg_satisfaction=avg_satisfaction,
            most_selected_option=most_selected_option,
            peak_usage_hour=peak_usage_hour,
            daily_growth_rate=daily_growth_rate,
            user_retention_rate=85.0  # 示例值
        )
    
    def update_charts(self):
        """更新所有图表"""
        # 选项分布饼图
        option_counts = {}
        for feedback in self.feedback_data:
            for option in feedback.selected_options:
                # 简化选项名称
                short_name = option.split()[0] if option else "其他"
                option_counts[short_name] = option_counts.get(short_name, 0) + 1
        
        self.pie_chart.update_data(option_counts)
        
        # 时间趋势柱状图
        daily_counts = {}
        for feedback in self.feedback_data:
            date_key = feedback.timestamp.strftime("%m-%d")
            daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
        
        # 取最近7天
        recent_dates = sorted(daily_counts.keys())[-7:]
        categories = recent_dates
        data = {"反馈数量": [daily_counts.get(date, 0) for date in recent_dates]}
        
        self.bar_chart.update_data(categories, data)
        
        # 响应时间趋势折线图
        time_data = []
        for i, feedback in enumerate(sorted(self.feedback_data, key=lambda x: x.timestamp)[-20:]):
            time_data.append((i, feedback.response_time))
        
        self.line_chart.update_data(time_data)
        
        # 满意度分布饼图
        satisfaction_counts = {}
        for feedback in self.feedback_data:
            score = feedback.satisfaction_score
            label = f"{score}星"
            satisfaction_counts[label] = satisfaction_counts.get(label, 0) + 1
        
        self.satisfaction_chart.update_data(satisfaction_counts)
    
    def export_report(self):
        """导出报告"""
        try:
            report_data = {
                "generated_at": datetime.now().isoformat(),
                "metrics": self.calculate_metrics().__dict__,
                "total_records": len(self.feedback_data),
                "date_range": {
                    "start": min(f.timestamp for f in self.feedback_data).isoformat() if self.feedback_data else None,
                    "end": max(f.timestamp for f in self.feedback_data).isoformat() if self.feedback_data else None
                }
            }
            
            filename = f"feedback_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"📁 报告已导出: {filename}")
            
        except Exception as e:
            print(f"❌ 报告导出失败: {e}")
    
    def show_settings(self):
        """显示设置"""
        print("⚙️ 设置面板（待实现）")
    
    def apply_glassmorphism_style(self):
        """应用毛玻璃样式"""
        self.setStyleSheet("""
            DataVisualizationWidget {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 16px;
            }
        """)

def create_demo_visualization():
    """创建演示可视化组件"""
    from PySide6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    widget = DataVisualizationWidget()
    widget.setWindowTitle("📊 Interactive Feedback MCP - 数据可视化")
    widget.resize(1200, 800)
    widget.show()
    
    return widget, app

if __name__ == "__main__":
    widget, app = create_demo_visualization()
    sys.exit(app.exec()) 