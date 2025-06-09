# ui/utils/review_dialog.py
from PySide6.QtWidgets import QDialog
from ui.utils.ui_review_window import Ui_ReviewDialog

class ReviewDialog(QDialog, Ui_ReviewDialog):
    def __init__(self, enhanced_prompt, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.enhanced_text_edit.setPlainText(enhanced_prompt)
        self.accept_button.clicked.connect(self.accept)
        self.decline_button.clicked.connect(self.reject)
        self.accepted = False
    
    def accept(self):
        self.accepted = True
        self.close()
    
    def get_accepted(self):
        return self.accepted
