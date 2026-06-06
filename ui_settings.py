"""
Settings Dialog for JARVIS Configuration

A sleek, native Settings Dialog that directly hooks into your ConfigManager 
and safely restarts background threads when needed.

Features:
- Wake Word configuration
- Personality selection  
- Voice Engine selection
- LLM Backend selection
- Hot-swapping settings without restart

Usage:
    from ui_settings import SettingsDialog
    
    dialog = SettingsDialog(parent, restart_wake_word_callback=my_callback)
    dialog.exec()
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, 
    QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QLabel
)
from PySide6.QtCore import Qt

# Import the ConfigManager singleton
from core.config_manager import config


class SettingsDialog(QDialog):
    """
    Settings dialog for configuring JARVIS at runtime.
    
    Provides a user-friendly interface to modify:
    - Wake Word (for always-listening mode)
    - AI Personality (JARVIS, Friday, GLaDOS, HAL, TARS)
    - Voice Engine (edge-tts, elevenlabs, mac_local)
    - LLM Backend (gemini-2.5-flash, gemini-1.5-pro, etc.)
    
    Args:
        parent: Parent widget (optional)
        restart_wake_word_callback: Callback function to restart wake word listener 
                           when wake word changes (optional)
    """
    
    def __init__(self, parent=None, restart_wake_word_callback=None):
        super().__init__(parent)
        self.setWindowTitle("JARVIS Configuration")
        self.setMinimumWidth(400)
        self.restart_wake_word_callback = restart_wake_word_callback
        
        # Color scheme matching the main UI
        self._bg_color = "#00060a"
        self._pri_color = "#00d4ff"
        self._border_color = "#0d3347"
        self._text_color = "#8ffcff"
        self._text_dim = "#3a8a9a"
        self._panel_color = "#010d14"
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Build the settings UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("⚙  JARVIS Settings")
        title.setStyleSheet(f"""
            font-family: 'Courier New';
            font-size: 14px;
            font-weight: bold;
            color: {self._pri_color};
            background: transparent;
            padding: 4px;
        """)
        layout.addWidget(title)
        
        # Separator
        sep = QPushButton()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"""
            QPushButton {{
                background: {self._border_color};
                border: none;
            }}
        """)
        sep.setEnabled(False)
        layout.addWidget(sep)
        
        # Form layout for settings
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
# --- Wake Word ---
        self.wake_word_input = QLineEdit()
        self.wake_word_input.setText(config.get("wake_word", "hey_jarvis"))
        self.wake_word_input.setFixedHeight(28)
        self.wake_word_input.setStyleSheet(f"""
            QLineEdit {{
                background: {self._bg_color};
                color: {self._text_color};
                border: 1px solid {self._border_color};
                border-radius: 3px;
                padding: 4px 8px;
                font-family: 'Courier New';
                font-size: 10px;
            }}
            QLineEdit:focus {{
                border: 1px solid {self._pri_color};
            }}
        """)
        form_layout.addRow("Wake Word:", self.wake_word_input)
        
        # Helper text for wake word
        wake_help = QLabel("Say this to activate JARVIS (requires wake word listener)")
        wake_help.setStyleSheet(f"""
            color: {self._text_dim};
            font-size: 8px;
            background: transparent;
        """)
        form_layout.addRow("", wake_help)
        
        # --- Personality ---
        self.persona_combo = QComboBox()
        self.personas = ["jarvis", "friday", "glados", "hal", "tars"]
        self.persona_combo.addItems([p.capitalize() for p in self.personas])
        
# Set current personality
        current_persona = config.get("personality", "jarvis")
        if current_persona in self.personas:
            self.persona_combo.setCurrentIndex(self.personas.index(current_persona))
            
        self.persona_combo.setFixedHeight(28)
        self.persona_combo.setStyleSheet(f"""
            QComboBox {{
                background: {self._bg_color};
                color: {self._text_color};
                border: 1px solid {self._border_color};
                border-radius: 3px;
                padding: 4px 8px;
                font-family: 'Courier New';
                font-size: 10px;
            }}
            QComboBox:focus {{
                border: 1px solid {self._pri_color};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background: {self._panel_color};
                color: {self._text_color};
                border: 1px solid {self._border_color};
                selection-background-color: {self._pri_color};
                selection-color: {self._bg_color};
            }}
        """)
        form_layout.addRow("AI Persona:", self.persona_combo)
        
        # --- Voice Engine ---
        self.voice_engine_combo = QComboBox()
        self.voice_engines = ["edge-tts", "elevenlabs", "mac_local"]
        self.voice_engine_combo.addItems(self.voice_engines)
        
current_engine = config.get("voice_engine", "edge-tts")
        if current_engine in self.voice_engines:
            self.voice_engine_combo.setCurrentIndex(self.voice_engines.index(current_engine))
            
        self.voice_engine_combo.setFixedHeight(28)
        self.voice_engine_combo.setStyleSheet(f"""
            QComboBox {{
                background: {self._bg_color};
                color: {self._text_color};
                border: 1px solid {self._border_color};
                border-radius: 3px;
                padding: 4px 8px;
                font-family: 'Courier New';
                font-size: 10px;
            }}
            QComboBox:focus {{
                border: 1px solid {self._pri_color};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background: {self._panel_color};
                color: {self._text_color};
                border: 1px solid {self._border_color};
                selection-background-color: {self._pri_color};
                selection-color: {self._bg_color};
            }}
        """)
        form_layout.addRow("Voice Engine:", self.voice_engine_combo)
        
        # --- LLM Backend ---
        self.llm_combo = QComboBox()
        self.llms = ["gemini-2.5-flash", "gemini-1.5-pro", "claude-3.5-sonnet", "gpt-4o"]
        self.llm_combo.addItems(self.llms)
        
current_llm = config.get("llm_backend", "gemini-2.5-flash")
        if current_llm in self.llms:
            self.llm_combo.setCurrentIndex(self.llms.index(current_llm))
            
        self.llm_combo.setFixedHeight(28)
        self.llm_combo.setStyleSheet(f"""
            QComboBox {{
                background: {self._bg_color};
                color: {self._text_color};
                border: 1px solid {self._border_color};
                border-radius: 3px;
                padding: 4px 8px;
                font-family: 'Courier New';
                font-size: 10px;
            }}
            QComboBox:focus {{
                border: 1px solid {self._pri_color};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background: {self._panel_color};
                color: {self._text_color};
                border: 1px solid {self._border_color};
                selection-background-color: {self._pri_color};
                selection-color: {self._bg_color};
            }}
        """)
        form_layout.addRow("LLM Backend:", self.llm_combo)
        
        layout.addLayout(form_layout)
        
        # Spacer
        layout.addStretch()
        
        # --- Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(32)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self._bg_color};
                color: {self._text_dim};
                border: 1px solid {self._border_color};
                border-radius: 3px;
                font-family: 'Courier New';
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: {self._text_color};
                border: 1px solid {self._pri_color};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save & Apply")
        save_btn.setFixedHeight(32)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self._pri_color};
                color: {self._bg_color};
                border: none;
                border-radius: 3px;
                font-family: 'Courier New';
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #00e5ff;
            }}
        """)
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def save_settings(self):
        """
        Save all settings and apply changes.
        
        Updates the ConfigManager singleton and triggers wake word
        listener restart if the wake word changed.
        """
# Get old wake word before updating
        old_wake_word = config.get("wake_word")
        new_wake_word = self.wake_word_input.text().strip().lower()
        
        # Validate wake word
        if not new_wake_word:
            QMessageBox.warning(
                self, 
                "Invalid Wake Word",
                "Please enter a valid wake word."
            )
            return
        
        # Update ConfigManager singleton
        config.update("wake_word", new_wake_word)
        config.set_personality(self.personas[self.persona_combo.currentIndex()])
        config.update("voice_engine", self.voice_engine_combo.currentText())
        config.update("llm_backend", self.llm_combo.currentText())
        
        # If wake word changed, trigger the callback to restart the thread safely
        if old_wake_word != new_wake_word and self.restart_wake_word_callback:
            self.restart_wake_word_callback(new_wake_word)
        
        # Show success message
        QMessageBox.information(
            self, 
            "Settings Saved", 
            "JARVIS configuration updated successfully.\n\n"
            "Some changes may require restarting the assistant."
        )
        
        self.accept()


# Alternative import for PyQt6 compatibility
try:
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox
    from PyQt6.QtCore import Qt
except ImportError:
    pass


if __name__ == "__main__":
    # Test the settings dialog
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Show the dialog
    dialog = SettingsDialog()
    result = dialog.exec()
    
    if result == QDialog.DialogCode.Accepted:
        print("Settings saved!")
    else:
        print("Settings cancelled.")
    
    sys.exit(0)
