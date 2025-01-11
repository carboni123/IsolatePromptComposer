# main.py
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow  # Import UI
# from core.project_manager import ProjectManager  # Example of core module import


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow() # Instantiate the UI class
    # project_manager = ProjectManager() # Instantiate the core project manager class
    main_window.show()
    sys.exit(app.exec())