# core/project_manager.py
import os
import json
from PySide6.QtWidgets import QFileDialog, QPlainTextEdit


class ProjectManager:
    def __init__(self, warning_message):
        self.warning_message = warning_message

    def save_project(self, main_window):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(main_window, "Save Project", "", "JSON Files (*.json)")
        if file_path:
            project_data = {
                "version": 1.1,  # Updated version for new structure
                "prompts": {},
                "ignore_patterns": main_window.ignore_patterns,
                "api_key_path": main_window.api_key_path,
                "project_path": main_window.project_path_lineedit.text(),
                "files_tab_paths": list(main_window.files_added_to_files_tab),  # Save the master set
                "output_type": main_window.output_type,  # Save output type
                "line_enumerator_checked": main_window.actionLine_Enumerator.isChecked(),  # Save line enum state
            }
            for i in range(main_window.prompt_tab.count()):
                tab_name = main_window.prompt_tab.tabText(i)
                # Do not save raw content of "Files" tab, it's rebuilt
                if tab_name == "Files":  # Assuming "Files" is the text of tedit_tab5's tab
                    continue

                current_tab = main_window.prompt_tab.widget(i)
                text_edits = current_tab.findChildren(QPlainTextEdit)
                if text_edits:
                    text_edit = text_edits[0]
                    project_data["prompts"][tab_name] = text_edit.toPlainText()

            with open(file_path, "w") as f:
                json.dump(project_data, f, indent=4)
                self.warning_message.message_box("Project Saved", f"Project saved to {file_path}")

    def open_project(self, main_window):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(main_window, "Open Project", "", "JSON Files (*.json)")
        if file_path:
            main_window.new_project(silent=True)  # Clear current state
            try:
                with open(file_path, "r") as f:
                    project_data = json.load(f)

                    main_window.project_path_lineedit.setText(project_data.get("project_path", ""))
                    project_path = project_data.get("project_path")

                    main_window.ignore_patterns = project_data.get("ignore_patterns", [])
                    if project_path:  # List content only if path exists
                        main_window.list_project_content(project_path)  # This uses ignore_patterns

                    # Load prompts for other tabs
                    if "prompts" in project_data:
                        for i in range(main_window.prompt_tab.count()):
                            tab_name = main_window.prompt_tab.tabText(i)
                            if tab_name == "Files":  # Skip "Files" tab raw content
                                continue
                            if tab_name in project_data["prompts"]:
                                current_tab = main_window.prompt_tab.widget(i)
                                text_edits = current_tab.findChildren(QPlainTextEdit)
                                if text_edits:
                                    text_edit = text_edits[0]
                                    text_edit.setPlainText(project_data["prompts"][tab_name])

                    # Restore API key path
                    main_window.api_key_path = project_data.get("api_key_path", "")
                    if main_window.api_key_path and os.path.exists(
                        main_window.api_key_path
                    ):  # Check if key path is valid
                        # Attempt to load key, but don't make it fatal if API itself has issues. UI should reflect path.
                        # The actual API loading happens on demand (e.g. when calling LLM)
                        main_window.label_api.setText(f"API Key: {os.path.basename(main_window.api_key_path)}")
                    elif main_window.api_key_path:  # Path saved but not found
                        main_window.warning_message.message_box(
                            "Warning", f"API Key file not found: {main_window.api_key_path}"
                        )
                        main_window.label_api.setText("API Key: Click to load")  # Reset label
                    else:  # No key path saved
                        main_window.label_api.setText("API Key: Click to load")

                    # Restore output type and line enumerator state
                    main_window.output_type = project_data.get("output_type", "xml")
                    main_window.actionXML_JSON_Formatting.setChecked(main_window.output_type == "json")
                    main_window.actionLine_Enumerator.setChecked(project_data.get("line_enumerator_checked", False))

                    # Restore and rebuild "Files" tab
                    if "files_tab_paths" in project_data:
                        main_window.files_added_to_files_tab = set(
                            os.path.normpath(os.path.abspath(p)) for p in project_data["files_tab_paths"]
                        )
                        # main_window._rebuild_files_tab_content() # Called by main_window.open_project() wrapper

                    main_window.project_data = project_data
                    self.warning_message.message_box("Project Loaded", f"Project loaded from {file_path}")
            except FileNotFoundError:
                self.warning_message.message_box("Error", f"Project file not found: {file_path}")
            except json.JSONDecodeError:
                self.warning_message.message_box("Error", f"Invalid JSON format on: {file_path}")
            except Exception as e:
                self.warning_message.message_box("Error", f"Error loading project: {e}")
