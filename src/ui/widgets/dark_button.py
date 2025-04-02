from PyQt5.QtWidgets import QPushButton
from core.styles import DEFAULT_STYLES

class DarkButton(QPushButton):
    def __init__(self, text: str, color: str = DEFAULT_STYLES["PRIMARY_COLOR"], parent=None):
        super().__init__(text, parent)
        self.default_color = color
        self._update_style()
        
    def _update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.default_color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(self.default_color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(self.default_color)};
            }}
            QPushButton:disabled {{
                background-color: #555555;
                color: #aaaaaa;
            }}
        """)
        
    def _lighten_color(self, hex_color: str) -> str:
        r = min(int(hex_color[1:3], 16) + 25, 255)
        g = min(int(hex_color[3:5], 16) + 25, 255)
        b = min(int(hex_color[5:7], 16) + 25, 255)
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def _darken_color(self, hex_color: str) -> str:
        r = max(int(hex_color[1:3], 16) - 25, 0)
        g = max(int(hex_color[3:5], 16) - 25, 0)
        b = max(int(hex_color[5:7], 16) - 25, 0)
        return f"#{r:02x}{g:02x}{b:02x}"