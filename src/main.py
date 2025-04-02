import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import IPGrabberTool

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = IPGrabberTool()
    window.show()
    
    sys.exit(app.exec_())