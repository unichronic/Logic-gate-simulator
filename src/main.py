


import sys
import os
from PyQt5.QtWidgets import QApplication
from mainwindow import MainWindow

def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Logic Gate Simulator")
    
    
    try:
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        resources_dir = os.path.join(os.path.dirname(current_dir), "resources")
        
        with open(os.path.join(resources_dir, "style.qss"), "r") as f:
            style = f.read()
            app.setStyleSheet(style)
    except FileNotFoundError:
        print("Style file not found, using default style")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
