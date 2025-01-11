from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import os


def create_box(message: str):
    """Creates about box"""
    message_box = QMessageBox()
    message_box.setWindowTitle("About Isolate Prompt Composer")
    message_box.setWindowIcon(QIcon(os.path.join("media", "logo.png")))
    message_box.setTextFormat(Qt.TextFormat.RichText)  # For HTML formatting
    message_box.setText(message)
    message_box.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    message_box.exec()


def show_about_info():
    """Displays the information about the project."""
    create_box(
        f"""
        <b>Isolate Prompt Composer</b>
        <br>
        A tool for composing structured prompts for Large Language Models.
        <br>
        <br>
        Version: 0.1
        <br>
        <br>
        2025 - Diego Carboni
        <br>
        https://github.com/carboni123
        <br>
        <br>
        This project is licensed under the GNU GPLv3 license.
        """
    )


def show_about_pyside():
    """Displays the information about the project."""
    create_box(
        f"""
    This project is built using PySide6
    <br>
    More information: https://www.qt.io/qt-for-python
    <p><b>Licensing Information:</b></p>
    <ul>
        <b>PySide6:</b> Distributed under the LGPLv3 license. Additional terms may apply if you distribute this software.
    </ul>
    """
    )


def show_about_googleaistudio():
    """Displays the information about the project."""
    create_box(
        f"""
    <p>This project leverages:</p>
    <ul>
        <b>Google AI Studio</b> with <b>Gemini 2.0 Flash Experimental</b>.
    </ul>
    
    <p>More Information: https://aistudio.google.com/
    
    <p><b>Acknowledgment:</b></p>
    <ul>
        <li>Thanks to the Google team for providing free access to this cutting-edge technology.</li>
    </ul>
    """
    )
