"""
JARVIS Settings Dialog
PyQt6-based Settings UI that hooks into ConfigManager for dynamic configuration.

Usage:
    from ui_settings import SettingsDialog
    
    # Open settings dialog
    dialog = SettingsDialog(parent_window, restart_wake_word_callback=callback)
    dialog.exec()
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, 
    QLineEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.config_manager import config


class SettingsDialog(QDialog):
    def __init__(self, parent=None, restart_wake_word_callback=None):
        super().__init__(parent)
        self.setWindowTitle("JARVIS Configuration")
        self.setMinimumWidth(400)
        self.setModal(True)
        self.restart_wake_word_callback = restart_wake_word_callback
        
        # Available options from config
        self.personas = ["jarvis", "friday", "glados", "hal", "tars"]
        self.voice_engines = ["gemini", "edge-tts", "elevenlabs"]
        self.llms = ["gemini-2.5-flash", "gemini-1.5-pro", "claude-3.5-sonnet", "gpt-4o"]
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the settings UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Title
        title = QPushButton("◈ JARVIS CONFIGURATION")
        title.setFont(QFont("Courier New", 11, QFont.Weight.Bold))
        title.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #00d4ff;
                border: none;
                padding: 8px;
            }
        """)
        title.setCursor(Qt.CursorShape.ArrowCursor)
        layout.addWidget(title)
        
        # Form layout for settings
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # --- Wake Word ---
        self.wake_word_input = QLineEdit()
        self.wake_word_input.setPlaceholderText("e.g., hey_jarvis")
        self.wake_word_input.setText(config.get("wake_word", "hey_jarvis"))
        self.wake_word_input.setFont(QFont("Courier New", 9))
        self.wake_word_input.setStyleSheet("""
            QLineEdit {
                background: #000d14;
                color: #d8f8ff;
                border: 1px solid #0d3347;
                border-radius: 3px;
                padding: 6px 8px;
            }
            QLineEdit:focus {
                border: 1px solid #00d4ff;
            }
        """)
        form_layout.addRow("Wake Word:", self.wake_word_input)
        
        # --- Personality ---
        self.persona_combo = QComboBox()
        self.persona_combo.addItems([p.capitalize() for p in self.personas])
        current_persona = config.get("personality", "jarvis")
        if current_persona in self.personas:
            self.persona_combo.setCurrentIndex(self.personas.index(current_persona))
        self.persona_combo.setFont(QFont("Courier New", 9))
        self.persona_combo.setStyleSheet("""
            QComboBox {
                background: #000d14;
                color: #d8f8ff;
                border: 1px solid #0d3347;
                border-radius: 3px;
                padding: 6px 8px;
            }
            QComboBox:focus {
                border: 1px solid #00d4ff;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #00d4ff;
            }
        """)
        form_layout.addRow("AI Persona:", self.persona_combo)
        
        # --- Voice Engine ---
        self.voice_engine_combo = QComboBox()
        self.voice_engine_combo.addItems(self.voice_engines)
        current_engine = config.get("voice_engine", "gemini")
        if current_engine in self.voice_engines:
            self.voice_engine_combo.setCurrentIndex(self.voice_engines.index(current_engine))
        self.voice_engine_combo.setFont(QFont("Courier New", 9))
        self.voice_engine_combo.setStyleSheet("""
            QComboBox {
                background: #000d14;
                color: #d8f8ff;
                border: 1px solid #0d3347;
                border-radius: 3px;
                padding: 6px 8px;
            }
            QComboBox:focus {
                border: 1px solid #00d4ff;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #00d4ff;
            }
        """)
        form_layout.addRow("Voice Engine:", self.voice_engine_combo)
        
        # --- LLM Backend ---
        self.llm_combo = QComboBox()
        self.llm_combo.addItems(self.llms)
        current_llm = config.get("llm_backend", "gemini-2.5-flash")
        if current_llm in self.llms:
            self.llm_combo.setCurrentIndex(self.llms.index(current_llm))
        self.llm_combo.setFont(QFont("Courier New", 9))
        self.llm_combo.setStyleSheet("""
            QComboBox {
                background: #000d14;
                color: #d8f8ff;
                border: 1px solid #0d3347;
                border-radius: 3px;
                padding: 6px 8px;
            }
            QComboBox:focus {
                border: 1px solid #00d4ff;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #00d4ff;
            }
        """)
        form_layout.addRow("LLM Backend:", self.llm_combo)
        
        layout.addLayout(form_layout)
        
        # --- Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        cancel_btn.setFixedHeight(36)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #000d14;
                color: #8ffcff;
                border: 1px solid #0d3347;
                border-radius: 3px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                border: 1px solid #1a5c7a;
                color: #d8f8ff;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Save & Apply")
        save_btn.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        save_btn.setFixedHeight(36)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #00d4ff;
                color: #000d14;
                border: none;
                border-radius: 3px;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #00e5ff;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background: #010d14;
            }
            QFormLayout::label {
                color: #5ab8cc;
                font-family: 'Courier New';
                font-size: 9px;
            }
            QFormLayout::field {
                color: #d8f8ff;
            }
        """)
    
    def save_settings(self):
        """Save settings and update ConfigManager."""
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
        
        # Update config via ConfigManager singleton
        config.update("wake_word", new_wake_word)
        config.set_personality(self.personas[self.persona_combo.currentIndex()])
        config.update("voice_engine", self.voice_engine_combo.currentText())
        config.update("llm_backend", self.llm_combo.currentText())
        
        # If wake word changed, trigger the callback to restart the listener
        if old_wake_word != new_wake_word and self.restart_wake_word_callback:
            self.restart_wake_word_callback(new_wake_word)
        
        QMessageBox.information(
            self, 
            "Settings Saved", 
            "JARVIS configuration updated successfully.\nSome changes may require restart."
        )
        self.accept()


def open_settings(parent=None, restart_callback=None) -> bool:
    """
    Convenience function to open the settings dialog.
    
    Args:
        parent: Parent window (optional)
        restart_callback: Callback function to restart wake word listener (optional)
    
    Returns:
        True if settings were saved, False if cancelled
    """
    dialog = SettingsDialog(parent, restart_wake_word_callback=restart_callback)
    return dialog.exec() == QDialog.DialogCode.Accepted
