"""
Password strength meter widget and validation logic.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QProgressBar, 
                              QLabel, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette
import re

class PasswordStrengthMeter(QWidget):
    """A widget that shows password strength with a visual indicator."""
    
    # Signal emitted when password strength changes
    strength_changed = Signal(int)  # 0-100
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Strength indicator
        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setFixedHeight(6)
        
        # Strength label
        self.strength_label = QLabel("Password strength: Weak")
        self.strength_label.setStyleSheet("font-size: 9pt;")
        
        # Requirements list
        self.requirements = QLabel()
        self.requirements.setStyleSheet("font-size: 8pt; color: #666;")
        self.requirements.setWordWrap(True)
        
        layout.addWidget(self.strength_bar)
        layout.addWidget(self.strength_label)
        layout.addWidget(self.requirements)
        self.setLayout(layout)
        
        # Set initial state
        self.update_strength(0)
        
    def update_strength(self, strength):
        """Update the strength indicator with the given strength (0-100)."""
        try:
            if not hasattr(self, 'strength_bar') or not self.strength_bar:
                return
                
            # Ensure strength is within valid range
            strength = max(0, min(100, int(strength)))
            
            # Update progress bar value
            self.strength_bar.setValue(strength)
            
            # Update color and label based on strength
            if strength < 30:
                color = "#ff4d4d"  # Red
                label = "Very Weak"
            elif strength < 60:
                color = "#ff9933"  # Orange
                label = "Weak"
            elif strength < 80:
                color = "#ffcc00"  # Yellow
                label = "Moderate"
            elif strength < 90:
                color = "#99cc33"  # Light green
                label = "Strong"
            else:
                color = "#33cc33"  # Green
                label = "Very Strong"
            
            # Only update styles if widget is visible and has a window
            if self.isVisible() and self.window():
                try:
                    self.strength_bar.setStyleSheet(f"""
                        QProgressBar {{
                            border: none;
                            border-radius: 3px;
                            background-color: #f0f0f0;
                        }}
                        QProgressBar::chunk {{
                            background-color: {color};
                            border-radius: 3px;
                        }}
                    """)
                except RuntimeError:
                    # Widget might be deleted in another thread
                    return
            
            # Update label text
            self.strength_label.setText(f"Password strength: {label}")
            
            # Emit signal if connected
            try:
                self.strength_changed.emit(strength)
            except RuntimeError:
                # Signal might be disconnected or object deleted
                pass
                
        except Exception as e:
            # Log any errors but don't crash
            import traceback
            print(f"Error updating password strength: {e}\n{traceback.format_exc()}")

class PasswordValidator:
    """Validates password strength and requirements."""
    
    def __init__(self, min_length=8, require_uppercase=True, 
                 require_lowercase=True, require_digits=True,
                 require_special=True, min_strength=60):
        """
        Initialize the password validator.
        
        Args:
            min_length: Minimum password length
            require_uppercase: Whether to require uppercase letters
            require_lowercase: Whether to require lowercase letters
            require_digits: Whether to require digits
            require_special: Whether to require special characters
            min_strength: Minimum strength score (0-100) to consider password valid
        """
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.min_strength = min_strength
        
    def check_strength(self, password):
        """
        Check the strength of a password.
        
        Returns:
            tuple: (strength_score, requirements_met, feedback)
        """
        if not password:
            return 0, [], "Enter a password"
            
        score = 0
        requirements = []
        feedback = []
        
        # Length check
        length = len(password)
        if length >= self.min_length:
            score += 25
            requirements.append(("length", True, f"At least {self.min_length} characters"))
        else:
            requirements.append(("length", False, f"At least {self.min_length} characters (current: {length})"))
            feedback.append(f"Password should be at least {self.min_length} characters long")
            
        # Uppercase check
        if self.require_uppercase:
            if re.search(r'[A-Z]', password):
                score += 15
                requirements.append(("uppercase", True, "Contains uppercase letters"))
            else:
                requirements.append(("uppercase", False, "Contains uppercase letters"))
                feedback.append("Password should contain at least one uppercase letter")
        else:
            score += 15
                
        # Lowercase check
        if self.require_lowercase:
            if re.search(r'[a-z]', password):
                score += 15
                requirements.append(("lowercase", True, "Contains lowercase letters"))
            else:
                requirements.append(("lowercase", False, "Contains lowercase letters"))
                feedback.append("Password should contain at least one lowercase letter")
        else:
            score += 15
            
        # Digits check
        if self.require_digits:
            if re.search(r'[0-9]', password):
                score += 15
                requirements.append(("digits", True, "Contains numbers"))
            else:
                requirements.append(("digits", False, "Contains numbers"))
                feedback.append("Password should contain at least one number")
        else:
            score += 15
            
        # Special characters check
        if self.require_special:
            if re.search(r'[^A-Za-z0-9]', password):
                score += 15
                requirements.append(("special", True, "Contains special characters"))
            else:
                requirements.append(("special", False, "Contains special characters"))
                feedback.append("Password should contain at least one special character")
        else:
            score += 15
            
        # Additional points for length beyond minimum
        if length > self.min_length:
            extra_length = min(length - self.min_length, 10)  # Max 10 points for extra length
            score += extra_length
            
        # Check for common patterns (penalize)
        if password.lower() in ["password", "123456", "qwerty", "letmein"]:
            score = max(0, score - 30)
            feedback.append("Avoid common passwords")
            
        # Check for repeated characters
        if re.search(r'(.)\1{2,}', password):
            score = max(0, score - 10)
            feedback.append("Avoid repeated characters")
            
        # Cap at 100
        score = min(100, score)
        
        return score, requirements, feedback

    def is_valid(self, password):
        """Check if the password meets all requirements."""
        if not password:
            return False, "Password cannot be empty"
            
        score, requirements, feedback = self.check_strength(password)
        
        if score < self.min_strength:
            return False, "Password is too weak. " + " ".join(feedback)
            
        return True, "Password is strong"