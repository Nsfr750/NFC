"""
Statistics dialog for the NFC Reader/Writer application.

This module provides a dialog to display statistics about read/write operations.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, 
                             QHeaderView, QTabWidget, QWidget, QFormLayout)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtCharts import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis
from PySide6.QtGui import QPainter, QColor, QPalette

class StatisticsDialog(QDialog):
    """Dialog to display statistics about NFC operations."""
    
    def __init__(self, stats_manager, parent=None):
        """Initialize the statistics dialog.
        
        Args:
            stats_manager: StatisticsManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.stats_manager = stats_manager
        self.setWindowTitle("Statistics")
        self.setMinimumSize(800, 600)
        
        # Set up the UI
        self.init_ui()
        
        # Update the display
        self.update_stats()
        
        # Set up a timer to refresh the stats periodically
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_stats)
        self.refresh_timer.start(5000)  # Update every 5 seconds
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Summary tab
        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)
        
        # Summary labels
        self.summary_labels = {}
        summary_form = QFormLayout()
        
        for field in ['total_operations', 'read_operations', 'write_operations', 
                     'success_rate', 'average_duration', 'data_processed']:
            self.summary_labels[field] = QLabel("-")
            summary_form.addRow(field.replace('_', ' ').title() + ":", self.summary_labels[field])
        
        summary_layout.addLayout(summary_form)
        
        # Add chart for operation distribution
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        summary_layout.addWidget(QLabel("<b>Operation Distribution</b>"))
        summary_layout.addWidget(self.chart_view)
        
        self.tabs.addTab(summary_tab, "Summary")
        
        # Recent operations tab
        recent_tab = QWidget()
        recent_layout = QVBoxLayout(recent_tab)
        
        # Recent operations table
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(5)
        self.recent_table.setHorizontalHeaderLabels([
            "Time", "Operation", "Tag Type", "Status", "Duration (ms)"
        ])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        recent_layout.addWidget(self.recent_table)
        
        self.tabs.addTab(recent_tab, "Recent Operations")
        
        # Tag types tab
        types_tab = QWidget()
        types_layout = QVBoxLayout(types_tab)
        
        self.types_table = QTableWidget()
        self.types_table.setColumnCount(2)
        self.types_table.setHorizontalHeaderLabels(["Tag Type", "Count"])
        self.types_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        types_layout.addWidget(self.types_table)
        
        self.tabs.addTab(types_tab, "Tag Types")
        
        # Add tabs to layout
        layout.addWidget(self.tabs)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        
        self.clear_button = QPushButton("Clear Statistics")
        self.clear_button.clicked.connect(self.clear_statistics)
        self.clear_button.setStyleSheet("color: red;")
        
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def update_stats(self):
        """Update the statistics display."""
        summary = self.stats_manager.get_summary()
        
        # Update summary labels
        if summary:
            self.summary_labels['total_operations'].setText(str(summary.get('total_operations', 0)))
            self.summary_labels['read_operations'].setText(str(summary.get('read_operations', 0)))
            self.summary_labels['write_operations'].setText(str(summary.get('write_operations', 0)))
            
            success_rate = summary.get('success_rate', 0)
            self.summary_labels['success_rate'].setText(f"{success_rate:.1f}%")
            
            avg_duration = summary.get('average_duration', 0) * 1000  # Convert to ms
            self.summary_labels['average_duration'].setText(f"{avg_duration:.1f} ms")
            
            data_processed = summary.get('data_processed', 0)
            self.summary_labels['data_processed'].setText(self.format_data_size(data_processed))
            
            # Update operation distribution chart
            self.update_chart(summary)
            
            # Update tag types distribution
            self.update_tag_types(summary.get('tag_type_distribution', {}))
        
        # Update recent operations
        self.update_recent_operations()
    
    def format_data_size(self, size_bytes):
        """Format data size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0 or unit == 'GB':
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
    
    def update_chart(self, summary):
        """Update the operation distribution chart."""
        # Create a new chart
        chart = QChart()
        chart.setTitle("Operation Distribution")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Create bar sets
        read_set = QBarSet("Read")
        write_set = QBarSet("Write")
        
        read_set.setColor(QColor(65, 105, 225))  # Royal Blue
        write_set.setColor(QColor(50, 205, 50))  # Lime Green
        
        # Add data
        read_set.append(summary.get('read_operations', 0))
        write_set.append(summary.get('write_operations', 0))
        
        # Create series and add bars
        series = QBarSeries()
        series.append(read_set)
        series.append(write_set)
        
        chart.addSeries(series)
        
        # Customize the chart appearance
        chart.setTheme(QChart.ChartThemeLight)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        # Set up the axes
        axis = QBarCategoryAxis()
        axis.append([""])
        chart.createDefaultAxes()
        chart.setAxisX(axis, series)
        
        # Set the chart to the view
        self.chart_view.setChart(chart)
    
    def update_recent_operations(self):
        """Update the recent operations table."""
        recent_ops = self.stats_manager.get_recent_operations(limit=20)
        
        self.recent_table.setRowCount(len(recent_ops))
        
        for row, op in enumerate(recent_ops):
            # Format time
            time_str = datetime.fromtimestamp(op['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            
            # Create items
            time_item = QTableWidgetItem(time_str)
            op_item = QTableWidgetItem(op['operation_type'].capitalize())
            type_item = QTableWidgetItem(op['tag_type'])
            
            # Set status item with color
            status_item = QTableWidgetItem("Success" if op['success'] else "Failed")
            if op['success']:
                status_item.setForeground(QColor(0, 128, 0))  # Green
            else:
                status_item.setForeground(QColor(255, 0, 0))  # Red
            
            # Format duration
            duration_ms = op.get('duration', 0) * 1000
            duration_item = QTableWidgetItem(f"{duration_ms:.1f} ms")
            
            # Add items to the table
            self.recent_table.setItem(row, 0, time_item)
            self.recent_table.setItem(row, 1, op_item)
            self.recent_table.setItem(row, 2, type_item)
            self.recent_table.setItem(row, 3, status_item)
            self.recent_table.setItem(row, 4, duration_item)
    
    def update_tag_types(self, tag_types):
        """Update the tag types distribution table."""
        if not tag_types:
            self.types_table.setRowCount(0)
            return
        
        # Convert to list of tuples and sort by count (descending)
        types_list = sorted(tag_types.items(), key=lambda x: x[1], reverse=True)
        
        self.types_table.setRowCount(len(types_list))
        
        for row, (tag_type, count) in enumerate(types_list):
            type_item = QTableWidgetItem(tag_type)
            count_item = QTableWidgetItem(str(count))
            
            self.types_table.setItem(row, 0, type_item)
            self.types_table.setItem(row, 1, count_item)
    
    def clear_statistics(self):
        """Clear all statistics after confirmation."""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, 'Clear Statistics',
            'Are you sure you want to clear all statistics?\nThis action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.stats_manager.clear_statistics()
            self.update_stats()  # Refresh the display
