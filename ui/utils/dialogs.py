import os
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon


class WarningBox:
    def __init__(self):
        # Warning box
        self.box = QMessageBox()
        self.box.setIcon(QMessageBox.Icon.Warning)
        self.box.setWindowIcon(QIcon(os.path.join("media", "logo.png")))
        # Warning box with yes/no
        self.box_accept = QMessageBox()
        self.box_accept.setIcon(QMessageBox.Icon.Question)
        self.box_accept.setWindowIcon(QIcon(os.path.join("media", "logo.png")))
        # Mutes the alerts
        self._mute = False

    def mute(self, state):
        "Mutes all alerts"
        self._mute = state

    def message_box(self, title, message):
        if self._mute:
            return
        self.box.setWindowTitle(title)
        self.box.setText(message)
        self.box.exec()

    def message_box_with_accept(self, title, message):
        self.box_accept.setWindowTitle(title)
        self.box_accept.setText(message)
        self.box_accept.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        buttonY = self.box_accept.button(QMessageBox.StandardButton.Yes)
        buttonY.setText("Yes")
        buttonN = self.box_accept.button(QMessageBox.StandardButton.No)
        buttonN.setText("No")
        self.box_accept.exec()
        if self.box_accept.clickedButton() == buttonY:
            return True
        # elif self.box_accept.clickedButton() == buttonN:
        else:
            return False
