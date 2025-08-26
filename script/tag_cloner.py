"""
Tag Cloning Module

This module provides functionality to clone data from one NFC tag to another,
supporting various tag types and handling authentication when needed.
"""
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QGroupBox, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from .nfc_operations import NfcOperations, TagType
from .tag_database import TagDatabase

logger = logging.getLogger(__name__)

@dataclass
class CloneResult:
    """Represents the result of a tag cloning operation."""
    success: bool
    message: str
    source_tag: Optional[Dict[str, Any]] = None
    target_tag: Optional[Dict[str, Any]] = None
    bytes_copied: int = 0

def format_tag_info(tag_info: Dict[str, Any]) -> str:
    """Format tag information for display."""
    lines = [
        f"Type: {tag_info.get('type', 'Unknown')}",
        f"ID: {tag_info.get('id', 'N/A')}",
        f"Size: {tag_info.get('memory_capacity', 0)} bytes"
    ]
    return "\n".join(lines)

class TagCloner:
    """Handles cloning of NFC tags with support for various tag types."""
    
    def __init__(self, nfc_ops: NfcOperations, db: Optional[TagDatabase] = None):
        """Initialize the TagCloner.
        
        Args:
            nfc_ops: Initialized NfcOperations instance
            db: Optional TagDatabase instance for logging
        """
        self.nfc_ops = nfc_ops
        self.db = db
        self.source_tag = None
        self.target_tag = None
    
    def read_tag_data(self, tag_info: Dict[str, Any]) -> Optional[bytes]:
        """Read all data from a tag."""
        try:
            # Connect to the tag
            if not self.nfc_ops.connect():
                return None
                
            tag_type = tag_info.get('type')
            data = None
            
            # Read data based on tag type
            if tag_type in [TagType.MIFARE_CLASSIC_1K, TagType.MIFARE_CLASSIC_4K]:
                data = self._read_mifare_classic(tag_info)
            elif tag_type in [TagType.MIFARE_ULTRALIGHT, TagType.NTAG_213, 
                            TagType.NTAG_215, TagType.NTAG_216]:
                data = self._read_ntag_ultralight(tag_info)
            # Add support for other tag types as needed
            
            return data
            
        except Exception as e:
            logger.error(f"Error reading tag data: {str(e)}")
            return None
        finally:
            self.nfc_ops.disconnect()
    
    def _read_mifare_classic(self, tag_info: Dict[str, Any]) -> Optional[bytes]:
        """Read data from MIFARE Classic tags."""
        # Implementation for reading MIFARE Classic tags
        # This is a simplified version - actual implementation would need to handle authentication
        data = bytearray()
        
        # For MIFARE Classic 1K: 16 sectors, 4 blocks per sector, 16 bytes per block
        # Skip sector 0 (contains manufacturer data)
        for sector in range(1, 16):
            # Authenticate with the sector
            if not self.nfc_ops.authenticate_mifare(sector * 4):
                logger.warning(f"Failed to authenticate sector {sector}")
                continue
                
            # Read blocks in the sector (first 3 blocks are data, 4th is sector trailer)
            for block in range(4):
                block_num = sector * 4 + block
                if block_num == 0:
                    continue  # Skip manufacturer block
                    
                block_data = self.nfc_ops.read_block(block_num)
                if block_data:
                    data.extend(block_data)
        
        return bytes(data)
    
    def _read_ntag_ultralight(self, tag_info: Dict[str, Any]) -> Optional[bytes]:
        """Read data from NTAG/Ultralight tags."""
        data = bytearray()
        
        # NTAG213: 45 pages (180 bytes)
        # NTAG215: 135 pages (540 bytes)
        # NTAG216: 231 pages (924 bytes)
        # Each page is 4 bytes
        
        # Read all available pages
        max_pages = {
            TagType.MIFARE_ULTRALIGHT: 45,  # 180 bytes
            TagType.NTAG_213: 45,           # 180 bytes
            TagType.NTAG_215: 135,          # 540 bytes
            TagType.NTAG_216: 231,          # 924 bytes
        }.get(tag_info.get('type'), 45)     # Default to NTAG213 size
        
        for page in range(0, max_pages):
            page_data = self.nfc_ops.read_page(page)
            if page_data:
                data.extend(page_data)
            else:
                break
                
        return bytes(data)
    
    def write_tag_data(self, tag_info: Dict[str, Any], data: bytes) -> bool:
        """Write data to a tag."""
        try:
            if not self.nfc_ops.connect():
                return False
                
            tag_type = tag_info.get('type')
            
            if tag_type in [TagType.MIFARE_CLASSIC_1K, TagType.MIFARE_CLASSIC_4K]:
                return self._write_mifare_classic(tag_info, data)
            elif tag_type in [TagType.MIFARE_ULTRALIGHT, TagType.NTAG_213, 
                             TagType.NTAG_215, TagType.NTAG_216]:
                return self._write_ntag_ultralight(tag_info, data)
            
            return False
            
        except Exception as e:
            logger.error(f"Error writing to tag: {str(e)}")
            return False
        finally:
            self.nfc_ops.disconnect()
    
    def _write_mifare_classic(self, tag_info: Dict[str, Any], data: bytes) -> bool:
        """Write data to MIFARE Classic tags."""
        # Implementation for writing to MIFARE Classic tags
        # This is a simplified version
        
        # Calculate how many blocks we can write
        block_size = 16  # 16 bytes per block
        data_len = len(data)
        
        # For MIFARE Classic 1K: 16 sectors, 4 blocks per sector, 16 bytes per block
        # Skip sector 0 (contains manufacturer data)
        data_index = 0
        
        for sector in range(1, 16):
            # Authenticate with the sector
            if not self.nfc_ops.authenticate_mifare(sector * 4):
                logger.warning(f"Failed to authenticate sector {sector}")
                continue
                
            # Write blocks in the sector (first 3 blocks are data, 4th is sector trailer)
            for block in range(3):  # Only write to first 3 blocks (data blocks)
                if data_index >= data_len:
                    return True  # Done writing
                    
                block_num = sector * 4 + block
                if block_num == 0:
                    continue  # Skip manufacturer block
                    
                # Get the data for this block
                block_data = data[data_index:data_index + block_size]
                # Pad with 0xFF if needed
                if len(block_data) < block_size:
                    block_data += b'\xFF' * (block_size - len(block_data))
                    
                # Write the block
                if not self.nfc_ops.write_block(block_num, block_data):
                    logger.warning(f"Failed to write block {block_num}")
                
                data_index += block_size
        
        return data_index >= data_len  # Return True if all data was written
    
    def _write_ntag_ultralight(self, tag_info: Dict[str, Any], data: bytes) -> bool:
        """Write data to NTAG/Ultralight tags."""
        # Implementation for writing to NTAG/Ultralight tags
        
        # Get the maximum number of pages for this tag type
        max_pages = {
            TagType.MIFARE_ULTRALIGHT: 45,  # 180 bytes
            TagType.NTAG_213: 45,           # 180 bytes
            TagType.NTAG_215: 135,          # 540 bytes
            TagType.NTAG_216: 231,          # 924 bytes
        }.get(tag_info.get('type'), 45)     # Default to NTAG213 size
        
        # Convert data to bytes if it's not already
        if not isinstance(data, (bytes, bytearray)):
            data = str(data).encode('utf-8')
        
        # Write data page by page (4 bytes per page)
        for page in range(0, max_pages):
            start = page * 4
            end = start + 4
            
            if start >= len(data):
                break  # Done writing
                
            # Get the data for this page
            page_data = data[start:end]
            
            # Pad with 0xFF if needed
            if len(page_data) < 4:
                page_data += b'\xFF' * (4 - len(page_data))
            
            # Skip writing to read-only pages (pages 0-3 on NTAG)
            if page < 4:
                continue
                
            # Write the page
            if not self.nfc_ops.write_page(page, page_data):
                logger.warning(f"Failed to write page {page}")
                return False
        
        return True
    
    def clone_tag(self, source_tag: Dict[str, Any], target_tag: Dict[str, Any]) -> CloneResult:
        """Clone data from source tag to target tag.
        
        Args:
            source_tag: Dictionary containing source tag information
            target_tag: Dictionary containing target tag information
            
        Returns:
            CloneResult: Result of the cloning operation
        """
        self.source_tag = source_tag
        self.target_tag = target_tag
        
        # Log the cloning operation
        logger.info(f"Starting tag clone: {source_tag.get('id')} -> {target_tag.get('id')}")
        
        # Read data from source tag
        logger.info("Reading data from source tag...")
        source_data = self.read_tag_data(source_tag)
        
        if not source_data:
            return CloneResult(
                success=False,
                message="Failed to read data from source tag",
                source_tag=source_tag,
                target_tag=target_tag
            )
        
        # Write data to target tag
        logger.info(f"Writing {len(source_data)} bytes to target tag...")
        success = self.write_tag_data(target_tag, source_data)
        
        if success:
            # Update the database if available
            if self.db and 'data' in source_tag:
                try:
                    self.db.store_tag(
                        tag_id=target_tag.get('id'),
                        tag_type=target_tag.get('type', 'unknown'),
                        data=source_tag.get('data', ''),
                        metadata={
                            'cloned_from': source_tag.get('id'),
                            'cloned_at': time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    )
                except Exception as e:
                    logger.error(f"Error updating database: {str(e)}")
            
            return CloneResult(
                success=True,
                message="Tag cloned successfully",
                source_tag=source_tag,
                target_tag=target_tag,
                bytes_copied=len(source_data)
            )
        else:
            return CloneResult(
                success=False,
                message="Failed to write data to target tag",
                source_tag=source_tag,
                target_tag=target_tag,
                bytes_copied=0
            )


class CloneWorker(QThread):
    """Worker thread for tag cloning operations."""
    progress = Signal(int, str)
    finished = Signal(object)  # Emits CloneResult
    
    def __init__(self, cloner, source_tag, target_tag):
        super().__init__()
        self.cloner = cloner
        self.source_tag = source_tag
        self.target_tag = target_tag
    
    def run(self):
        """Run the clone operation."""
        try:
            self.progress.emit(0, "Starting clone operation...")
            result = self.cloner.clone_tag(self.source_tag, self.target_tag)
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"Error in clone worker: {str(e)}")
            result = CloneResult(
                success=False,
                message=f"Error during cloning: {str(e)}",
                source_tag=self.source_tag,
                target_tag=self.target_tag
            )
            self.finished.emit(result)


class TagClonerDialog(QDialog):
    """Dialog for cloning NFC tags."""
    
    def __init__(self, nfc_ops, db, parent=None):
        """Initialize the dialog.
        
        Args:
            nfc_ops: NfcOperations instance
            db: TagDatabase instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.nfc_ops = nfc_ops
        self.db = db
        self.tag_cloner = TagCloner(nfc_ops, db)
        self.source_tag = None
        self.target_tag = None
        
        self.setWindowTitle("Tag Cloner")
        self.setMinimumSize(500, 400)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Source tag group
        source_group = QGroupBox("Source Tag")
        source_layout = QVBoxLayout()
        
        self.source_info = QLabel("No tag selected")
        self.source_info.setWordWrap(True)
        
        self.source_btn = QPushButton("Read Source Tag")
        self.source_btn.clicked.connect(self.read_source_tag)
        
        source_layout.addWidget(self.source_info)
        source_layout.addWidget(self.source_btn)
        source_group.setLayout(source_layout)
        
        # Target tag group
        target_group = QGroupBox("Target Tag")
        target_layout = QVBoxLayout()
        
        self.target_info = QLabel("No tag selected")
        self.target_info.setWordWrap(True)
        
        self.target_btn = QPushButton("Read Target Tag")
        self.target_btn.clicked.connect(self.read_target_tag)
        
        target_layout.addWidget(self.target_info)
        target_layout.addWidget(self.target_btn)
        target_group.setLayout(target_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Ready")
        
        # Clone button
        self.clone_btn = QPushButton("Clone Tag")
        self.clone_btn.setEnabled(False)
        self.clone_btn.clicked.connect(self.start_clone)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.clone_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        
        # Add widgets to main layout
        layout.addWidget(source_group)
        layout.addWidget(target_group)
        layout.addWidget(self.progress_bar)
        layout.addLayout(btn_layout)
    
    def read_source_tag(self):
        """Read the source tag."""
        self.set_ui_state(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Scan source tag...")
        
        try:
            if not self.nfc_ops.connect():
                self.show_error("Error", "Could not connect to NFC reader")
                return
            
            # Read tag information
            tag_info = self.nfc_ops.get_tag_info()
            if not tag_info:
                self.show_error("Error", "Could not read tag information")
                return
            
            # Read tag data
            tag_data = self.tag_cloner.read_tag_data(tag_info)
            if tag_data:
                tag_info['data'] = tag_data
                self.source_tag = tag_info
                self.source_info.setText(
                    f"<b>Tag ID:</b> {tag_info.get('id', 'N/A')}<br>"
                    f"<b>Type:</b> {tag_info.get('type', 'Unknown')}<br>"
                    f"<b>Size:</b> {len(tag_data)} bytes"
                )
                self.update_ui_state()
                self.progress_bar.setFormat("Source tag read successfully")
            else:
                self.show_error("Error", "Could not read tag data")
                
        except Exception as e:
            self.show_error("Error", f"Failed to read tag: {str(e)}")
            logger.error(f"Error reading source tag: {str(e)}")
        finally:
            self.nfc_ops.disconnect()
            self.set_ui_state(True)
    
    def read_target_tag(self):
        """Read the target tag."""
        self.set_ui_state(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Scan target tag...")
        
        try:
            if not self.nfc_ops.connect():
                self.show_error("Error", "Could not connect to NFC reader")
                return
            
            # Read tag information
            tag_info = self.nfc_ops.get_tag_info()
            if not tag_info:
                self.show_error("Error", "Could not read tag information")
                return
            
            self.target_tag = tag_info
            self.target_info.setText(
                f"<b>Tag ID:</b> {tag_info.get('id', 'N/A')}<br>"
                f"<b>Type:</b> {tag_info.get('type', 'Unknown')}"
            )
            self.update_ui_state()
            self.progress_bar.setFormat("Target tag detected")
                
        except Exception as e:
            self.show_error("Error", f"Failed to read tag: {str(e)}")
            logger.error(f"Error reading target tag: {str(e)}")
        finally:
            self.nfc_ops.disconnect()
            self.set_ui_state(True)
    
    def start_clone(self):
        """Start the clone operation."""
        if not self.source_tag or not self.target_tag:
            return
            
        # Confirm clone operation
        reply = QMessageBox.question(
            self,
            "Confirm Clone",
            "WARNING: This will overwrite the target tag's data.\n"
            "Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.set_ui_state(False)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Starting clone operation...")
            
            # Create and start worker thread
            self.worker = CloneWorker(self.tag_cloner, self.source_tag, self.target_tag)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.clone_finished)
            self.worker.start()
    
    def update_progress(self, value, message):
        """Update the progress bar and status."""
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(message)
    
    def clone_finished(self, result):
        """Handle completion of the clone operation."""
        self.set_ui_state(True)
        
        if result.success:
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Clone completed successfully")
            QMessageBox.information(
                self,
                "Success",
                f"Tag cloned successfully!\n\n"
                f"Source: {result.source_tag.get('id')}\n"
                f"Target: {result.target_tag.get('id')}\n"
                f"Bytes copied: {result.bytes_copied}"
            )
        else:
            self.progress_bar.setFormat(f"Error: {result.message}")
            self.show_error("Clone Failed", result.message)
    
    def set_ui_state(self, enabled):
        """Enable or disable UI controls."""
        self.source_btn.setEnabled(enabled)
        self.target_btn.setEnabled(enabled)
        self.clone_btn.setEnabled(enabled and self.source_tag and self.target_tag)
    
    def update_ui_state(self):
        """Update the state of UI controls."""
        self.clone_btn.setEnabled(self.source_tag is not None and self.target_tag is not None)
    
    def show_error(self, title, message):
        """Show an error message."""
        QMessageBox.critical(self, title, message)
        self.progress_bar.setFormat(f"Error: {message}")
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        event.accept()
