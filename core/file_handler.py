# core/file_handler.py
import os
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import Qt


class FileHandler:
    def __init__(self, warning_message):
        self.warning_message = warning_message

    def load_from_combobox(self, folder, combobox, text_edit):
        selected_item = combobox.currentText()
        if selected_item == "Custom":
            self.load_specific_file(text_edit)
        else:
            file_path = os.path.join("data", folder, selected_item)
            self._load_file_content(file_path, text_edit)

    def load_specific_file(self, text_edit):
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Load File", "", "All Files (*)"
        )
        if file_path:
            self._load_file_content(file_path, text_edit)

    def _load_file_content(self, file_path, text_edit):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                file_content = file.read()
                text_edit.setPlainText(file_content)
        except FileNotFoundError:
            self.warning_message.message_box("Error", f"File not found: {file_path}")
        except PermissionError:
            self.warning_message.message_box("Error", f"Permission denied: {file_path}")
        except Exception as e:
            self.warning_message.message_box("Error", f"Error loading file: {e}")

    def read_file_content(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            self.warning_message.message_box("Error", f"File not found: {file_path}")
            return None
        except PermissionError:
            self.warning_message.message_box("Error", f"Permission denied: {file_path}")
            return None
        except Exception as e:
            self.warning_message.message_box("Error", f"Error reading file: {e}")
            return None

    def load_default_ignore(self, project_path, silent=True):
        ignore_patterns = []
        ignore_path = os.path.join(project_path, ".ignore")
        if os.path.exists(ignore_path):
            try:
                with open(ignore_path, "r") as f:
                    ignore_patterns = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]
                if not silent:
                    self.warning_message.message_box(
                        "ignore file Loaded",
                        f".ignore filters added from {ignore_path}",
                    )

            except Exception as e:
                self.warning_message.message_box("Error", f"Error loading .ignore: {e}")
        return ignore_patterns

    def load_ignore(self, file_path, silent=True):
        ignore_patterns = []
        try:
            with open(file_path, "r") as f:
                ignore_patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
            if not silent:
                self.warning_message.message_box(
                    "ignore Loaded", f".ignore filters added from {file_path}"
                )
        except Exception as e:
            self.warning_message.message_box("Error", f"Error loading .ignore: {e}")
        return ignore_patterns

    def get_file_tree_string(self, parent, indent, is_last_sibling=False):
        tree_string = ""
        if parent is None:
            return ""

        # Sort children: directories first, then files
        children = []
        for i in range(parent.childCount()):
            child = parent.child(i)
            file_path = child.data(0, Qt.ItemDataRole.UserRole)
            children.append((os.path.isdir(file_path), file_path, child))
        
        # Sort by: is_directory descending (directories first), then by name
        children.sort(key=lambda x: (not x[0], os.path.basename(x[1])))

        for index, (is_dir, file_path, child) in enumerate(children):
            is_last = index == len(children) - 1

            # Constructing the prefix string
            prefix = ""
            if indent > 0:
                prefix = "│   " * (indent - 1) + ("└── " if is_last_sibling else "├── ")
            else:
                prefix = ""  # No prefix at root level

            if is_dir:
                tree_string += f"{prefix}{os.path.basename(file_path)}/\n"
                tree_string += self.get_file_tree_string(child, indent + 1, is_last)
            else:
                tree_string += f"{prefix}{os.path.basename(file_path)}\n"

        return tree_string
