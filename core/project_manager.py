# core/project_manager.py
import os
import json
from PySide6.QtWidgets import QFileDialog, QPlainTextEdit


class ProjectManager:
    def __init__(self, warning_message):
        self.warning_message = warning_message

    def save_project(self, main_window):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            main_window, "Save Project", "", "JSON Files (*.json)"
        )
        if file_path:
            project_data = {
                "version": 1,  # Add a version key to facilitate future updates
                "prompts": {},
                "ignore_patterns": main_window.ignore_patterns,
                "api_key_path": main_window.api_key_path,  # Save api_key_path
                "project_path": main_window.project_path_lineedit.text(), # Save project path
            }
            for i in range(main_window.prompt_tab.count()):
                tab_name = main_window.prompt_tab.tabText(i)
                current_tab = main_window.prompt_tab.widget(i)
                text_edits = current_tab.findChildren(QPlainTextEdit)
                if text_edits:
                    text_edit = text_edits[0]
                    project_data["prompts"][tab_name] = text_edit.toPlainText()

            with open(file_path, "w") as f:
                json.dump(project_data, f, indent=4)
                self.warning_message.message_box(
                    "Project Saved", f"Project saved to {file_path}"
                )

    def open_project(self, main_window):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            main_window, "Open Project", "", "JSON Files (*.json)"
        )
        if file_path:
            main_window.new_project(silent=True)
            try:
                with open(file_path, "r") as f:
                    project_data = json.load(f)
                    
                    if "project_path" in project_data:
                        main_window.project_path_lineedit.setText(
                            project_data["project_path"]
                        )
                        project_path = project_data["project_path"]
                        main_window.list_project_content(project_path)
                        if "ignore_patterns" in project_data:
                            main_window.ignore_patterns = project_data["ignore_patterns"]
                            main_window.list_project_content(project_path)
                        else:
                            main_window.load_default_ignore(silent=True)
                    if "prompts" in project_data:
                        for i in range(main_window.prompt_tab.count()):
                            tab_name = main_window.prompt_tab.tabText(i)
                            if tab_name in project_data["prompts"]:
                                current_tab = main_window.prompt_tab.widget(i)
                                text_edits = current_tab.findChildren(QPlainTextEdit)
                                if text_edits:
                                    text_edit = text_edits[0]
                                    text_edit.setPlainText(
                                        project_data["prompts"][tab_name]
                                    )
                    if "api_key_path" in project_data and project_data["api_key_path"]:
                        try:
                            main_window.llm_handler.load_api_key(project_data["api_key_path"])
                            main_window.api_key_path = project_data["api_key_path"]
                            main_window.label_api.setText(f"API Key: {os.path.basename(project_data['api_key_path'])}")
                        except Exception as e:
                             main_window.warning_message.message_box("Error", f"Error loading API Key: {e}")
                    main_window.project_data = project_data
                    self.warning_message.message_box(
                        "Project Loaded", f"Project loaded from {file_path}"
                    )
            except FileNotFoundError:
                self.warning_message.message_box("Error", f"Project file not found: {file_path}")
            except json.JSONDecodeError:
               self.warning_message.message_box("Error", f"Invalid JSON format on: {file_path}")
            except Exception as e:
                self.warning_message.message_box("Error", f"Error loading project: {e}")