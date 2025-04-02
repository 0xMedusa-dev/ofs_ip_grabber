from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGroupBox, QRadioButton, 
    QButtonGroup, QHBoxLayout, QDateEdit, QComboBox
)
from PyQt5.QtCore import pyqtSignal, Qt

from datetime import date
from core.styles import DEFAULT_STYLES
from ui.widgets.dark_button import DarkButton

class FilterPanel(QWidget):
    filter_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Filter Options")
        title.setStyleSheet(f"color: {DEFAULT_STYLES['PRIMARY_COLOR']}; font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        date_box = QGroupBox("Date Range")
        date_box.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {DEFAULT_STYLES['DARK_BORDER']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        date_layout = QVBoxLayout(date_box)
        
        self.date_all = QRadioButton("All")
        self.date_today = QRadioButton("Today")
        self.date_custom = QRadioButton("Custom")
        self.date_all.setChecked(True)
        
        date_group = QButtonGroup(self)
        date_group.addButton(self.date_all)
        date_group.addButton(self.date_today)
        date_group.addButton(self.date_custom)
        
        date_layout.addWidget(self.date_all)
        date_layout.addWidget(self.date_today)
        date_layout.addWidget(self.date_custom)
        
        custom_date_layout = QHBoxLayout()
        custom_date_layout.setContentsMargins(20, 0, 0, 0)
        
        custom_date_layout.addWidget(QLabel("From:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(date.today())
        self.date_from.setEnabled(False)
        custom_date_layout.addWidget(self.date_from)
        
        custom_date_layout.addWidget(QLabel("To:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(date.today())
        self.date_to.setEnabled(False)
        custom_date_layout.addWidget(self.date_to)
        
        date_layout.addLayout(custom_date_layout)
        layout.addWidget(date_box)
        
        country_box = QGroupBox("Location")
        country_box.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {DEFAULT_STYLES['DARK_BORDER']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        country_layout = QVBoxLayout(country_box)
        
        country_layout.addWidget(QLabel("Country:"))
        self.country_combo = QComboBox()
        self.country_combo.addItem("All Countries")
        country_layout.addWidget(self.country_combo)
        
        layout.addWidget(country_box)
        
        self.apply_button = DarkButton("Apply Filters")
        layout.addWidget(self.apply_button)
        
        self.reset_button = DarkButton("Reset Filters", DEFAULT_STYLES["WARNING_COLOR"])
        layout.addWidget(self.reset_button)
        
        layout.addStretch()
        
        self.date_custom.toggled.connect(self._toggle_date_fields)
        self.apply_button.clicked.connect(self._apply_filters)
        self.reset_button.clicked.connect(self._reset_filters)
        
    def _toggle_date_fields(self, checked: bool):
        self.date_from.setEnabled(checked)
        self.date_to.setEnabled(checked)
        
    def _apply_filters(self):
        filters = {"date_filter": "all", "country": "all"}
        
        if self.date_today.isChecked():
            filters["date_filter"] = "today"
        elif self.date_custom.isChecked():
            filters["date_filter"] = "custom"
            filters["date_from"] = self.date_from.date().toString("yyyy-MM-dd")
            filters["date_to"] = self.date_to.date().toString("yyyy-MM-dd")
            
        if self.country_combo.currentText() != "All Countries":
            filters["country"] = self.country_combo.currentText()
            
        self.filter_changed.emit(filters)
        
    def _reset_filters(self):
        self.date_all.setChecked(True)
        self.country_combo.setCurrentText("All Countries")
        self._toggle_date_fields(False)
        self._apply_filters()
        
    def update_countries(self, countries: list[str]):
        current = self.country_combo.currentText()
        
        self.country_combo.clear()
        self.country_combo.addItem("All Countries")
        
        for country in sorted(countries):
            self.country_combo.addItem(country)
            
        index = self.country_combo.findText(current)
        if index >= 0:
            self.country_combo.setCurrentIndex(index)