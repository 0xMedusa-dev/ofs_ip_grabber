import json
import webbrowser
from datetime import datetime, date
from PyQt5.QtWidgets import QApplication
from typing import Dict, List, Any

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, 
    QTabWidget, QSplitter, QLineEdit, QComboBox, QProgressBar,
    QMessageBox, QGroupBox, QRadioButton, QButtonGroup, QFileDialog
)
from PyQt5.QtCore import Qt, QSettings, QUrl
from PyQt5.QtGui import QDesktopServices, QIcon

from core.logger import Logger
from core.styles import DEFAULT_STYLES
from core.worker import IPGrabberWorker
from ui.widgets.dark_button import DarkButton
from ui.widgets.filter_panel import FilterPanel
from ui.widgets.visitor_details import VisitorDetailsDialog

class IPGrabberTool(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.visitors = []
        self.tracking_url = ""
        self.ip_worker = None
        self.settings = QSettings("SecureHackers", "IPGrabberTool")
        
        self._setup_ui()
        self._load_settings()
        
    def _setup_ui(self):
        self.setWindowTitle("OFS IP Grabber")
        self.setMinimumSize(1000, 700)
        
        self._setup_dark_theme()
        
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        header = QLabel("OFS IP Grabber")
        header.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #8a2be2;
            padding: 10px;
        """)
        main_layout.addWidget(header)
        
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)
        
        tracking_control = QGroupBox("Tracking Control")
        tracking_control.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {DEFAULT_STYLES['DARK_BORDER']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {DEFAULT_STYLES['PRIMARY_COLOR']};
            }}
        """)
        tracking_layout = QVBoxLayout(tracking_control)
        
        service_layout = QHBoxLayout()
        service_layout.addWidget(QLabel("Tunnel Service:"))
        
        self.service_combo = QComboBox()
        self.service_combo.addItem("Serveo.net")
        self.service_combo.addItem("localhost.run")
        service_layout.addWidget(self.service_combo)
        
        tracking_layout.addLayout(service_layout)
        
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Tracking URL:"))
        
        self.url_display = QLineEdit()
        self.url_display.setReadOnly(True)
        self.url_display.setPlaceholderText("URL will appear here when tracking starts")
        url_layout.addWidget(self.url_display)
        
        self.copy_button = QPushButton()
        self.copy_button.setIcon(QIcon.fromTheme("edit-copy"))
        self.copy_button.setToolTip("Copy URL to clipboard")
        self.copy_button.setEnabled(False)
        url_layout.addWidget(self.copy_button)
        
        tracking_layout.addLayout(url_layout)
        
        button_layout = QHBoxLayout()
        
        self.start_button = DarkButton("Start Tracking", DEFAULT_STYLES["SUCCESS_COLOR"])
        button_layout.addWidget(self.start_button)
        
        self.stop_button = DarkButton("Stop Tracking", DEFAULT_STYLES["ERROR_COLOR"])
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.open_url_button = DarkButton("Open URL", DEFAULT_STYLES["INFO_COLOR"])
        self.open_url_button.setEnabled(False)
        button_layout.addWidget(self.open_url_button)
        
        tracking_layout.addLayout(button_layout)
        
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)  
        self.progress_bar.hide()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)
        
        tracking_layout.addLayout(progress_layout)
        control_layout.addWidget(tracking_control)
        
        main_splitter = QSplitter(Qt.Horizontal)
        
        data_tabs = QTabWidget()
        
        visitors_tab = QWidget()
        visitors_layout = QVBoxLayout(visitors_tab)
        
        visitors_toolbar = QHBoxLayout()
        
        self.export_button = DarkButton("Export Data", DEFAULT_STYLES["INFO_COLOR"])
        visitors_toolbar.addWidget(self.export_button)
        
        self.clear_button = DarkButton("Clear All", DEFAULT_STYLES["WARNING_COLOR"])
        visitors_toolbar.addWidget(self.clear_button)
        
        visitors_toolbar.addStretch()
        
        visitors_layout.addLayout(visitors_toolbar)
        
        self.visitors_table = QTableWidget()
        self.visitors_table.setColumnCount(6)
        self.visitors_table.setHorizontalHeaderLabels(["IP Address", "Timestamp", "Country", "City", "ISP", "Details"])
        self.visitors_table.horizontalHeader().setStretchLastSection(True)
        self.visitors_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.visitors_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.visitors_table.setAlternatingRowColors(True)
        self.visitors_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252525;
                gridline-color: #333333;
            }
            QHeaderView::section {
                background-color: #252525;
                padding: 5px;
                border: 1px solid #333333;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        
        visitors_layout.addWidget(self.visitors_table)
        
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #121212;
                color: #e0e0e0;
                border: 1px solid #333333;
                font-family: monospace;
            }
        """)
        
        log_layout.addWidget(self.log_display)
        
        data_tabs.addTab(visitors_tab, "Visitors")
        data_tabs.addTab(log_tab, "Log")
        
        self.filter_panel = FilterPanel()
        
        main_splitter.addWidget(self.filter_panel)
        main_splitter.addWidget(data_tabs)
        
        main_splitter.setSizes([200, 800])
        
        control_layout.addStretch()
        main_layout.addWidget(control_panel)
        main_layout.addWidget(main_splitter, 1)  
        
        self.setCentralWidget(central_widget)
        
        self.statusBar().showMessage("Ready")
        
        self.start_button.clicked.connect(self._start_tracking)
        self.stop_button.clicked.connect(self._stop_tracking)
        self.copy_button.clicked.connect(self._copy_url)
        self.open_url_button.clicked.connect(self._open_url)
        self.export_button.clicked.connect(self._export_data)
        self.clear_button.clicked.connect(self._clear_data)
        self.filter_panel.filter_changed.connect(self._apply_filters)
        self.visitors_table.cellDoubleClicked.connect(self._show_visitor_details)
        
    def _setup_dark_theme(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {DEFAULT_STYLES['DARK_BG']};
                color: #e0e0e0;
            }}
            QSplitter::handle {{
                background-color: {DEFAULT_STYLES['DARK_BORDER']};
            }}
            QGroupBox, QTabWidget::pane {{
                border: 1px solid {DEFAULT_STYLES['DARK_BORDER']};
            }}
            QTabBar::tab {{
                background-color: {DEFAULT_STYLES['DARK_WIDGET_BG']};
                border: none;
                padding: 8px 15px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {DEFAULT_STYLES['PRIMARY_COLOR']};
                color: white;
            }}
        """)
        
    def _start_tracking(self):
        self.progress_bar.show()
        self.start_button.setEnabled(False)
        self.status_label.setText("Connecting...")
        self.log_display.append(Logger.format_message("Starting IP tracking service...", Logger.INFO))
        
        tunnel_type = "serveo" if self.service_combo.currentText() == "Serveo.net" else "localhost.run"
        
        self.ip_worker = IPGrabberWorker(tunnel_type=tunnel_type)
        self.ip_worker.url_ready.connect(self._on_url_ready)
        self.ip_worker.ip_detected.connect(self._on_ip_detected)
        self.ip_worker.log_message.connect(self._log_message)
        self.ip_worker.connection_error.connect(self._on_connection_error)
        
        self.ip_worker.start()
        
    def _stop_tracking(self):
        if self.ip_worker and self.ip_worker.running:
            self.log_display.append(Logger.format_message("Stopping IP tracking service...", Logger.INFO))
            self.ip_worker.stop()
            
        self._reset_tracking_ui()
        
    def _reset_tracking_ui(self):
        self.progress_bar.hide()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.open_url_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        self.url_display.clear()
        self.tracking_url = ""
        self.status_label.setText("Ready")
        
    def _on_url_ready(self, url: str):
        self.tracking_url = url
        self.url_display.setText(url)
        self.progress_bar.hide()
        self.stop_button.setEnabled(True)
        self.open_url_button.setEnabled(True)
        self.copy_button.setEnabled(True)
        self.status_label.setText("Tracking Active")
        
    def _on_ip_detected(self, visitor_info: Dict[str, Any]):
        self.visitors.append(visitor_info)
        
        self._add_visitor_to_table(visitor_info)
        
        countries = set(v["country"] for v in self.visitors if "country" in v)
        self.filter_panel.update_countries(list(countries))
        
        self._save_data()
        
    def _add_visitor_to_table(self, visitor_info: Dict[str, Any]):
        row = self.visitors_table.rowCount()
        self.visitors_table.insertRow(row)
    
        self.visitors_table.setItem(row, 0, QTableWidgetItem(visitor_info["ip"]))
    
        self.visitors_table.setItem(row, 1, QTableWidgetItem(visitor_info["timestamp"]))
    
        self.visitors_table.setItem(row, 2, QTableWidgetItem(visitor_info["country"]))
    
        self.visitors_table.setItem(row, 3, QTableWidgetItem(visitor_info["city"]))
    
        self.visitors_table.setItem(row, 4, QTableWidgetItem(visitor_info["isp"]))
    
        details_button = QPushButton("View")
        details_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {DEFAULT_STYLES['INFO_COLOR']};
                border: none;
                font-weight: bold;
            }}
            QPushButton:hover {{
               text-decoration: underline;
            }}
        """)
        details_button.clicked.connect(lambda _, r=row: self._show_visitor_details(r))
        self.visitors_table.setCellWidget(row, 5, details_button)
    
        self.visitors_table.scrollToBottom()
        
    def _show_visitor_details(self, row: int):
        if row < len(self.visitors):
            dialog = VisitorDetailsDialog(self.visitors[row], self)
            dialog.exec_()
        
    def _log_message(self, message: str, level: str = Logger.INFO):
        self.log_display.append(Logger.format_message(message, level))
        
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def _on_connection_error(self, error_message: str):
        self._log_message(error_message, Logger.ERROR)
        self._reset_tracking_ui()
        
        QMessageBox.warning(self, "Connection Error", error_message)
        
    def _copy_url(self):
        if self.tracking_url:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.tracking_url)
            self._log_message("URL copied to clipboard", Logger.SUCCESS)
            
    def _open_url(self):
        if self.tracking_url:
            webbrowser.open(self.tracking_url)
            self._log_message("Opening URL in browser", Logger.INFO)
            
    def _export_data(self):
        if not self.visitors:
            QMessageBox.information(self, "Export Data", "No data to export")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)"
        )
        
        if not filename:
            return
            
        try:
            if filename.endswith(".json"):
                with open(filename, "w") as f:
                    json.dump(self.visitors, f, indent=2)
            elif filename.endswith(".csv"):
                with open(filename, "w") as f:
                    header = ["ip", "timestamp", "country", "countryCode", "region", "city", 
                             "zip", "lat", "lon", "timezone", "isp", "as", "userAgent", 
                             "platform", "browser", "referrer"]
                    f.write(",".join(header) + "\n")
                    
                    for visitor in self.visitors:
                        row = [str(visitor.get(key, "")) for key in header]
                        f.write(",".join(row) + "\n")
            else:
                with open(filename, "w") as f:
                    json.dump(self.visitors, f, indent=2)
                    
            self._log_message(f"Data exported to {filename}", Logger.SUCCESS)
            
        except Exception as e:
            self._log_message(f"Error exporting data: {str(e)}", Logger.ERROR)
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")
            
    def _clear_data(self):
        if not self.visitors:
            return
            
        confirm = QMessageBox.question(
            self, "Clear Data", 
            "Are you sure you want to clear all visitor data?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.visitors = []
            self.visitors_table.setRowCount(0)
            self.filter_panel.update_countries([])
            self._log_message("All visitor data cleared", Logger.WARNING)
            self._save_data()
            
    def _apply_filters(self, filters: Dict[str, str]):
        self.visitors_table.setRowCount(0)
        
        filtered_visitors = self.visitors.copy()
        
        if filters["date_filter"] == "today":
            today = datetime.now().strftime("%Y-%m-%d")
            filtered_visitors = [v for v in filtered_visitors if v["timestamp"].startswith(today)]
        elif filters["date_filter"] == "custom":
            from_date = datetime.strptime(filters["date_from"], "%Y-%m-%d")
            to_date = datetime.strptime(filters["date_to"], "%Y-%m-%d")
            
            filtered_visitors = [
                v for v in filtered_visitors 
                if from_date <= datetime.strptime(v["timestamp"].split()[0], "%Y-%m-%d") <= to_date
            ]
            
        if filters["country"] != "all":
            filtered_visitors = [v for v in filtered_visitors if v["country"] == filters["country"]]
            
        for visitor in filtered_visitors:
            self._add_visitor_to_table(visitor)
            
        self._log_message(f"Applied filters: {len(filtered_visitors)} visitors shown", Logger.INFO)
        
    def _save_data(self):
        self.settings.setValue("visitors", json.dumps(self.visitors))
        
    def _load_settings(self):
        visitors_data = self.settings.value("visitors", "[]")
        try:
            self.visitors = json.loads(visitors_data)
            
            for visitor in self.visitors:
                self._add_visitor_to_table(visitor)
                
            countries = set(v["country"] for v in self.visitors if "country" in v)
            self.filter_panel.update_countries(list(countries))
            
            self._log_message(f"Loaded {len(self.visitors)} visitor records", Logger.INFO)
            
        except json.JSONDecodeError:
            self._log_message("Error loading saved data", Logger.ERROR)
            
        service_index = self.settings.value("service_index", 0, int)
        if 0 <= service_index < self.service_combo.count():
            self.service_combo.setCurrentIndex(service_index)
            
    def closeEvent(self, event):
        self.settings.setValue("service_index", self.service_combo.currentIndex())
        
        if self.ip_worker and self.ip_worker.running:
            self.ip_worker.stop()
            
        super().closeEvent(event)