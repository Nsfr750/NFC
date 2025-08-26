from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtWidgets import QToolBar, QLineEdit, QWidget, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QKeySequence, QAction

class WriteWidget(QtWidgets.QWidget):
    """Custom widget for write operations in the toolbar."""
    write_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the write widget UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter text to write to tag...")
        self.text_input.returnPressed.connect(self.on_write_clicked)
        
        self.write_btn = QtWidgets.QPushButton("Write")
        self.write_btn.clicked.connect(self.on_write_clicked)
        
        layout.addWidget(self.text_input)
        layout.addWidget(self.write_btn)
        self.setLayout(layout)
    
    def on_write_clicked(self):
        """Handle write button click."""
        text = self.text_input.text().strip()
        if text:
            self.write_requested.emit(text)
            self.text_input.clear()


class AppToolBar(QToolBar):
    """Custom toolbar for the NFC Reader application."""
    
    def __init__(self, parent, nfc_thread):
        """Initialize the toolbar with actions.
        
        Args:
            parent: The parent widget
            nfc_thread: The NFC thread instance for tag operations
        """
        super().__init__("Main Toolbar", parent)
        self.parent = parent
        self.nfc_thread = nfc_thread
        
        # Setup toolbar properties
        self.setMovable(True)
        self.setIconSize(QtCore.QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.setStyleSheet("""
            QToolBar {
                spacing: 5px;
                padding: 2px;
                background: #f0f0f0;
                border-bottom: 1px solid #d0d0d0;
            }
            QToolButton {
                padding: 4px;
                border: 1px solid transparent;
                border-radius: 3px;
            }
            QToolButton:hover {
                background: #e0e0e0;
                border: 1px solid #c0c0c0;
            }
            QToolButton:pressed {
                background: #d0d0d0;
            }
        """)
        
        self.setup_actions()
        self.add_actions()
    
    def setup_actions(self):
        """Create all toolbar actions."""
        # Read action
        self.read_action = QAction(
            self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay),
            "Read Tag",
            self.parent
        )
        self.read_action.setShortcut(Qt.CTRL | Qt.Key_R)
        self.read_action.setStatusTip("Start reading NFC tags (Ctrl+R)")
        self.read_action.triggered.connect(self.parent.start_reading)
        
        # Write action
        self.write_widget = WriteWidget()
        self.write_widget.write_requested.connect(self.parent.start_writing)
        
        # Clear log action
        self.clear_action = QAction(
            self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon),
            "Clear Log",
            self.parent
        )
        self.clear_action.setShortcut(Qt.CTRL | Qt.Key_L)
        self.clear_action.setStatusTip("Clear the log display (Ctrl+L)")
        self.clear_action.triggered.connect(self.parent.clear_log)
        
        # Toggle read/write mode
        self.mode_action = QAction(
            self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView),
            "Read Mode",
            self.parent,
            checkable=True
        )
        self.mode_action.setShortcut(Qt.CTRL | Qt.Key_M)
        self.mode_action.setStatusTip("Toggle between read and write mode (Ctrl+M)")
        self.mode_action.setChecked(True)
        self.mode_action.toggled.connect(self.toggle_read_write_mode)
        
        # Separator
        self.separator = self.addSeparator()
    
    def add_actions(self):
        """Add actions to the toolbar."""
        # Add read button
        self.addAction(self.read_action)
        
        # Add write widget
        write_container = QWidget()
        write_layout = QHBoxLayout()
        write_layout.setContentsMargins(0, 0, 0, 0)
        write_layout.addWidget(self.write_widget)
        write_container.setLayout(write_layout)
        write_container.setMinimumWidth(300)
        self.addWidget(write_container)
        
        # Add lock button
        self.lock_button = QAction(
            self.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_ComputerIcon')),  # Placeholder icon
            "Lock Session",
            self.parent
        )
        self.lock_button.setShortcut("Ctrl+Shift+L")
        self.lock_button.triggered.connect(self.parent.lock_application)
        self.addAction(self.lock_button)
        
        # Add separator and other actions
        self.addSeparator()
        self.addAction(self.clear_action)
        self.addAction(self.mode_action)
    
    @Slot(bool)
    def toggle_read_write_mode(self, checked):
        """Toggle between read and write modes.
        
        Args:
            checked: True if read mode is selected, False for write mode
        """
        if checked:
            self.mode_action.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView)
            )
            self.mode_action.setText("Read Mode")
            self.parent.statusBar().showMessage('Switched to Read Mode', 3000)
            self.parent.start_reading()
        else:
            self.mode_action.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogContentsView)
            )
            self.mode_action.setText("Write Mode")
            self.parent.statusBar().showMessage('Switched to Write Mode', 3000)
            self.write_widget.text_input.setFocus()
