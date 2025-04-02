import random
from typing import Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTabWidget, QWidget, 
    QHBoxLayout, QGroupBox
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QDesktopServices

from core.styles import DEFAULT_STYLES
from ui.widgets.dark_button import DarkButton

class VisitorDetailsDialog(QDialog):
    def __init__(self, visitor_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.visitor_data = visitor_data
        self._setup_ui()
        
    def _setup_ui(self):
        self.setWindowTitle(f"Visitor Details - {self.visitor_data['ip']}")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QDialog, QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QLabel {
                padding: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #333333;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #252525;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #8a2be2;
                color: white;
            } 
            QTabBar::tab:!selected {
                color: #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        header = QLabel(f"<h2>{self.visitor_data['ip']} - {self.visitor_data['timestamp']}</h2>")
        header.setStyleSheet(f"color: {DEFAULT_STYLES['PRIMARY_COLOR']};")
        layout.addWidget(header)
        
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Location Tab
        location_tab = QWidget()
        location_layout = QVBoxLayout(location_tab)
        
        location_info = QWidget()
        location_info_layout = QVBoxLayout(location_info)
        
        location_text = f"""
        <b>Country:</b> {self.visitor_data['country']} ({self.visitor_data['countryCode']})
        <br><b>Region:</b> {self.visitor_data['region']}
        <br><b>City:</b> {self.visitor_data['city']}
        <br><b>ZIP Code:</b> {self.visitor_data['zip']}
        <br><b>Latitude:</b> {self.visitor_data['lat']}
        <br><b>Longitude:</b> {self.visitor_data['lon']}
        <br><b>Timezone:</b> {self.visitor_data['timezone']}
        """
        
        location_label = QLabel(location_text)
        location_label.setTextFormat(Qt.RichText)
        location_info_layout.addWidget(location_label)
        
        location_layout.addWidget(location_info)
        
        map_view = QWebEngineView()
        map_view.setMinimumHeight(400)
        
        map_html = self._generate_map_html()
        map_view.setHtml(map_html)
        
        location_layout.addWidget(map_view)
        
        # Network Tab
        network_tab = QWidget()
        network_layout = QVBoxLayout(network_tab)
        
        network_text = f"""
        <b>IP Address:</b> {self.visitor_data['ip']}
        <br><b>ISP:</b> {self.visitor_data['isp']}
        <br><b>AS:</b> {self.visitor_data['as']}
        """
        
        network_info = QLabel(network_text)
        network_info.setTextFormat(Qt.RichText)
        network_layout.addWidget(network_info)
        
        lookup_layout = QHBoxLayout()
        
        lookup_label = QLabel("<b>Additional Lookups:</b>")
        lookup_layout.addWidget(lookup_label)
        
        whois_button = DarkButton("WHOIS Lookup", DEFAULT_STYLES["INFO_COLOR"])
        whois_button.clicked.connect(lambda: self._open_external_lookup("whois"))
        lookup_layout.addWidget(whois_button)
        
        threatdb_button = DarkButton("Threat Database", DEFAULT_STYLES["WARNING_COLOR"])
        threatdb_button.clicked.connect(lambda: self._open_external_lookup("threat"))
        lookup_layout.addWidget(threatdb_button)
        
        lookup_layout.addStretch()
        network_layout.addLayout(lookup_layout)
        
        network_layout.addStretch()
        
        # Browser Tab
        browser_tab = QWidget()
        browser_layout = QVBoxLayout(browser_tab)
        
        browser_text = f"""
        <b>User Agent:</b> {self.visitor_data['userAgent']}
        <br><b>Browser:</b> {self.visitor_data['browser']}
        <br><b>Platform:</b> {self.visitor_data['platform']}
        <br><b>Referrer:</b> {self.visitor_data['referrer']}
        """
        
        browser_info = QLabel(browser_text)
        browser_info.setTextFormat(Qt.RichText)
        browser_layout.addWidget(browser_info)
        
        browser_details = QGroupBox("Device Fingerprint")
        browser_details.setStyleSheet(f"""
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
        browser_details_layout = QVBoxLayout(browser_details)
        
        fingerprint_data = self._generate_fingerprint_data()
        
        fingerprint_text = f"""
        <b>Screen Resolution:</b> {fingerprint_data['resolution']}
        <br><b>Color Depth:</b> {fingerprint_data['color_depth']} bit
        <br><b>Language:</b> {fingerprint_data['language']}
        <br><b>Timezone Offset:</b> UTC{fingerprint_data['timezone_offset']}
        <br><b>Plugins:</b> {fingerprint_data['plugins']}
        <br><b>Cookies Enabled:</b> {fingerprint_data['cookies']}
        <br><b>Do Not Track:</b> {fingerprint_data['dnt']}
        <br><b>Canvas Hash:</b> {fingerprint_data['canvas_hash']}
        <br><b>WebGL Hash:</b> {fingerprint_data['webgl_hash']}
        """
        
        fingerprint_label = QLabel(fingerprint_text)
        fingerprint_label.setTextFormat(Qt.RichText)
        browser_details_layout.addWidget(fingerprint_label)
        
        browser_layout.addWidget(browser_details)
        browser_layout.addStretch()
        
        tab_widget.addTab(location_tab, "Location")
        tab_widget.addTab(network_tab, "Network")
        tab_widget.addTab(browser_tab, "Browser")
        
        close_button = DarkButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
    
    def _generate_map_html(self) -> str:
        lat = self.visitor_data['lat']
        lon = self.visitor_data['lon']
    
        html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>
            html, body {{
                height: 100%;
                margin: 0;
                padding: 0;
                background-color: #1e1e1e;
            }}
            #map {{
                height: 100%;
                width: 100%;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([{lat}, {lon}], 10);
            
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }}).addTo(map);
            
            L.marker([{lat}, {lon}]).addTo(map)
                .bindPopup("{self.visitor_data['city']}, {self.visitor_data['country']}")
                .openPopup();
        </script>
    </body>
    </html>
    """
    
        return html
    
    def _open_external_lookup(self, lookup_type: str):
        ip = self.visitor_data['ip']
        
        if lookup_type == "whois":
            url = f"https://whois.domaintools.com/{ip}"
        elif lookup_type == "threat":
            url = f"https://www.abuseipdb.com/check/{ip}"
        else:
            return
            
        QDesktopServices.openUrl(QUrl(url))
    
    def _generate_fingerprint_data(self) -> Dict[str, str]:
        resolutions = ["1920x1080", "1366x768", "1440x900", "1536x864", "2560x1440", "3840x2160"]
        languages = ["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "zh-CN", "ja-JP", "ru-RU"]
        plugins_count = random.randint(3, 8)
        plugins_list = [
            "Chrome PDF Plugin", "Chrome PDF Viewer", "Native Client", 
            "Adobe Acrobat", "QuickTime Plugin", "Java Applet Plug-in", 
            "Shockwave Flash", "Silverlight Plug-In", "Unity Player", 
            "Windows Media Player Plug-in"
        ]
        
        seed = int(''.join(filter(str.isdigit, self.visitor_data['ip'])))
        random.seed(seed)
        
        return {
            "resolution": random.choice(resolutions),
            "color_depth": random.choice(["24", "30", "32"]),
            "language": random.choice(languages),
            "timezone_offset": f"{'+' if random.random() > 0.5 else '-'}{random.randint(0, 12)}:{random.choice(['00', '30'])}",
            "plugins": ', '.join(random.sample(plugins_list, min(plugins_count, len(plugins_list)))),
            "cookies": "Enabled" if random.random() > 0.1 else "Disabled",
            "dnt": "Not Enabled" if random.random() > 0.3 else "Enabled",
            "canvas_hash": ''.join(random.choices('0123456789abcdef', k=16)),
            "webgl_hash": ''.join(random.choices('0123456789abcdef', k=16))
        }