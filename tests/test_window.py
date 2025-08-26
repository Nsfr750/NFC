import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

def main():
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    
    print("Creating main window...")
    window = QMainWindow()
    window.setWindowTitle("Test Window")
    window.setGeometry(100, 100, 400, 300)
    
    # Create central widget and layout
    central_widget = QWidget()
    layout = QVBoxLayout()
    
    # Add a label
    label = QLabel("If you can see this, PySide6 is working!")
    layout.addWidget(label)
    
    # Set the layout to central widget and set it to main window
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)
    
    print("Showing window...")
    window.show()
    
    print("Starting event loop...")
    sys.exit(app.exec())

if __name__ == "__main__":
    print("Starting test...")
    main()
