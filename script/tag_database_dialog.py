"""
Tag Database Dialog

Provides a user interface for managing the tag database.
"""
import os
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QAbstractItemView, QLineEdit, QComboBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

logger = logging.getLogger(__name__)

class TagDatabaseDialog(QDialog):
    """Dialog for managing the tag database."""
    
    def __init__(self, db, parent=None):
        """Initialize the dialog.
        
        Args:
            db: TagDatabase instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Tag Database")
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        self.load_tags()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search tags...")
        self.search_edit.textChanged.connect(self.filter_tags)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_edit)
        
        # Tags table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Tag ID", "Type", "Size", "Last Updated"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self.view_tag_details)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.view_btn = QPushButton("View Details")
        self.view_btn.clicked.connect(self.view_tag_details)
        self.view_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_selected_tags)
        self.delete_btn.setEnabled(False)
        
        self.export_btn = QPushButton("Export...")
        self.export_btn.clicked.connect(self.export_tags)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.view_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.close_btn)
        
        # Connect selection changed signal
        self.table.selectionModel().selectionChanged.connect(self.update_button_states)
        
        # Add widgets to layout
        layout.addLayout(search_layout)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
    
    def load_tags(self):
        """Load tags from the database."""
        try:
            # Clear the table
            self.table.setRowCount(0)
            
            # Get tags from database
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, tag_id, tag_type, LENGTH(data) as size, updated_at 
                    FROM tags 
                    ORDER BY updated_at DESC
                """)
                
                for row in cursor.fetchall():
                    self.add_table_row(row)
                    
        except Exception as e:
            logger.error(f"Error loading tags: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load tags: {str(e)}")
    
    def add_table_row(self, row_data):
        """Add a row to the tags table."""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Add items to the row
        for col, value in enumerate(row_data):
            item = QTableWidgetItem(str(value) if value is not None else "")
            self.table.setItem(row, col, item)
    
    def filter_tags(self):
        """Filter tags based on search text."""
        search_text = self.search_edit.text().lower()
        
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
    
    def update_button_states(self):
        """Update the enabled state of action buttons."""
        selected = len(self.table.selectedItems()) > 0
        self.view_btn.setEnabled(selected)
        self.delete_btn.setEnabled(selected)
    
    def view_tag_details(self):
        """View details of the selected tag."""
        selected = self.table.selectedItems()
        if not selected:
            return
            
        row = selected[0].row()
        tag_id = self.table.item(row, 1).text()
        
        try:
            # Get tag details from database
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, tag_id, tag_type, data, created_at, updated_at, metadata 
                    FROM tags 
                    WHERE tag_id = ?
                """, (tag_id,))
                
                tag_data = cursor.fetchone()
                if tag_data:
                    self.show_tag_details(tag_data)
                    
        except Exception as e:
            logger.error(f"Error viewing tag details: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to get tag details: {str(e)}")
    
    def show_tag_details(self, tag_data):
        """Show detailed information about a tag."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Tag Details - {tag_data[1]}")
        layout = QVBoxLayout(dialog)
        
        # Create form layout for tag details
        form_layout = QFormLayout()
        
        # Add tag details to form
        form_layout.addRow("Tag ID:", QLabel(tag_data[1]))
        form_layout.addRow("Type:", QLabel(tag_data[2]))
        form_layout.addRow("Created:", QLabel(tag_data[4]))
        form_layout.addRow("Last Updated:", QLabel(tag_data[5]))
        
        # Add data preview
        data_label = QLabel("Data:")
        data_text = QLabel(tag_data[3][:500] + ("..." if len(tag_data[3]) > 500 else ""))
        data_text.setWordWrap(True)
        data_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Add metadata if available
        if tag_data[6]:
            import json
            try:
                metadata = json.loads(tag_data[6])
                metadata_text = "\n".join(f"{k}: {v}" for k, v in metadata.items())
                form_layout.addRow("Metadata:", QLabel(metadata_text))
            except:
                pass
        
        # Add widgets to layout
        layout.addLayout(form_layout)
        layout.addWidget(data_label)
        layout.addWidget(data_text)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
        
        dialog.exec()
    
    def delete_selected_tags(self):
        """Delete selected tags from the database."""
        selected = self.table.selectedItems()
        if not selected:
            return
            
        # Get unique rows from selected items
        rows = set(item.row() for item in selected)
        tag_ids = [self.table.item(row, 1).text() for row in rows]
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete {len(tag_ids)} tag(s)?\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with self.db._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.executemany(
                        "DELETE FROM tags WHERE tag_id = ?",
                        [(tag_id,) for tag_id in tag_ids]
                    )
                    conn.commit()
                    
                    # Remove rows from table
                    for row in sorted(rows, reverse=True):
                        self.table.removeRow(row)
                    
                    QMessageBox.information(
                        self, 
                        "Success", 
                        f"Successfully deleted {len(tag_ids)} tag(s)."
                    )
                    
            except Exception as e:
                logger.error(f"Error deleting tags: {str(e)}")
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Failed to delete tags: {str(e)}"
                )
    
    def export_tags(self):
        """Export tags to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Tags",
            "",
            "CSV Files (*.csv);;JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT tag_id, tag_type, data, created_at, updated_at, metadata 
                    FROM tags
                """)
                
                if file_path.lower().endswith('.json'):
                    self.export_to_json(cursor, file_path)
                else:
                    self.export_to_csv(cursor, file_path)
                    
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Tags exported successfully to:\n{file_path}"
                )
                
        except Exception as e:
            logger.error(f"Error exporting tags: {str(e)}")
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export tags: {str(e)}"
            )
    
    def export_to_csv(self, cursor, file_path):
        """Export tags to a CSV file."""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([d[0] for d in cursor.description])
            
            # Write data
            for row in cursor.fetchall():
                writer.writerow(row)
    
    def export_to_json(self, cursor, file_path):
        """Export tags to a JSON file."""
        import json
        
        columns = [d[0] for d in cursor.description]
        data = []
        
        for row in cursor.fetchall():
            data.append(dict(zip(columns, row)))
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from tag_database import TagDatabase
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    
    # Create database instance
    db = TagDatabase()
    
    # Show the dialog
    dialog = TagDatabaseDialog(db)
    dialog.show()
    
    sys.exit(app.exec())
