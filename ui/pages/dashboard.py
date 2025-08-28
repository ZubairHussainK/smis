"""Dashboard page UI implementation."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class DashboardPage(QWidget):
    """Dashboard page showing overview and statistics."""

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """Initialize the dashboard UI components."""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Dashboard")
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Metrics and Charts
        metrics_layout = QHBoxLayout()
        
        # Metrics Cards
        metrics_frame = QFrame()
        metrics_frame_layout = QVBoxLayout()
        
        # Total Students Card
        total_students = QFrame()
        total_layout = QVBoxLayout()
        total_layout.addWidget(QLabel("Total Students"))
        self.total_count = QLabel("0")
        total_layout.addWidget(self.total_count)
        total_students.setLayout(total_layout)
        
        # Attendance Rate Card
        attendance_rate = QFrame()
        attendance_layout = QVBoxLayout()
        attendance_layout.addWidget(QLabel("Attendance Rate"))
        self.attendance_percent = QLabel("0%")
        attendance_layout.addWidget(self.attendance_percent)
        attendance_rate.setLayout(attendance_layout)
        
        # Active Classes Card
        active_classes = QFrame()
        classes_layout = QVBoxLayout()
        classes_layout.addWidget(QLabel("Active Classes"))
        self.class_count = QLabel("0")
        classes_layout.addWidget(self.class_count)
        active_classes.setLayout(classes_layout)
        
        metrics_frame_layout.addWidget(total_students)
        metrics_frame_layout.addWidget(attendance_rate)
        metrics_frame_layout.addWidget(active_classes)
        metrics_frame.setLayout(metrics_frame_layout)
        metrics_layout.addWidget(metrics_frame)
        
        # Charts Frame
        charts_frame = QFrame()
        charts_layout = QHBoxLayout()
        
        # Attendance Distribution Chart
        attendance_chart = QFrame()
        attendance_chart_layout = QVBoxLayout()
        attendance_chart_layout.addWidget(QLabel("Attendance Distribution"))
        # Placeholder for chart
        attendance_chart.setLayout(attendance_chart_layout)
        
        # Class Enrollment Chart
        enrollment_chart = QFrame()
        enrollment_chart_layout = QVBoxLayout()
        enrollment_chart_layout.addWidget(QLabel("Class Enrollment"))
        # Placeholder for chart
        enrollment_chart.setLayout(enrollment_chart_layout)
        
        charts_layout.addWidget(attendance_chart)
        charts_layout.addWidget(enrollment_chart)
        charts_frame.setLayout(charts_layout)
        metrics_layout.addWidget(charts_frame)
        
        layout.addLayout(metrics_layout)
        self.setLayout(layout)

    def refresh_data(self):
        """Update dashboard with latest data."""
        pass  # Will be implemented in DashboardController
