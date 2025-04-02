import time
from core.styles import DEFAULT_STYLES

class Logger:
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    
    @staticmethod
    def format_message(message: str, level: str = INFO) -> str:
        timestamp = time.strftime("%H:%M:%S")
        
        color = {
            Logger.INFO: "#e0e0e0",
            Logger.SUCCESS: DEFAULT_STYLES["SUCCESS_COLOR"],
            Logger.WARNING: DEFAULT_STYLES["WARNING_COLOR"],
            Logger.ERROR: DEFAULT_STYLES["ERROR_COLOR"]
        }.get(level, "#e0e0e0")
        
        return f'<span style="color:#aaaaaa;">[{timestamp}]</span> <span style="color:{color};">{message}</span>'