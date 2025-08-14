# ui/main_window.py
import os
from PySide6.QtUiTools import loadUiType
from PySide6.QtWidgets import QFileDialog, QMessageBox, QPlainTextEdit, QLabel, QDialog, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from ui.utils.dialogs import WarningBox
from core.project_tree_view import update_tree_view, populate_comboboxes
from ui.utils.text_processor import TextProcessor
from core.dependency_analyzer import DependencyAnalyzer
from core.file_handler import FileHandler
from core.prompt_builder import PromptBuilder
from core.project_manager import ProjectManager
from core.llm_handler import LLMHandler
from ui.utils.review_dialog import ReviewDialog
from ui.utils.about import show_about_info, show_about_pyside, show_about_googleaistudio


Ui_MainWindow, QMainWindow = loadUiType("ui/ui_main_window.ui")


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join("media", "logo.png")))

        self.warning_message = WarningBox()
        self.file_handler = FileHandler(self.warning_message)
        self.prompt_builder = PromptBuilder(self.warning_message, self)
        self.project_manager = ProjectManager(self.warning_message)
        self.text_processor = TextProcessor()
        self.llm_handler = LLMHandler(self.warning_message)
        self.api_key_path = ""
        self.output_type = "xml"
        self.files_added_to_files_tab = set()  # Master set of normalized absolute paths for tedit_tab5
        self.patches = []

        self.project_data = {}
        self.ignore_patterns = []
        self.loaded_ignore = ""
        # self.output_type = "xml" # Already defined above

        self.button_actions()
        self.toolbar_actions()
        self.setup_tree_view()
        self.populate_comboboxes()
        self.le_search.hide()  # Not implemented
        self.pb_thoughts.hide()  # Not implemented
        # self.label_api.mousePressEvent = self.load_api_key # Set the mouse event

    def toolbar_actions(self):
        self.actionNew_Project.triggered.connect(self.new_project)
        self.actionOpen_Project.triggered.connect(self.open_project)
        self.actionSave_Project.triggered.connect(self.save_project)
        self.actionExport_Project.triggered.connect(self.save_project)
        self.actionAbout.triggered.connect(show_about_info)
        self.actionAbout_PySide.triggered.connect(show_about_pyside)
        self.actionAbout_Google_AI_Studio.triggered.connect(show_about_googleaistudio)
        self.actionMute_Warnings.triggered.connect(
            lambda: self.warning_message.mute(self.actionMute_Warnings.isChecked())
        )
        self.actionXML_JSON_Formatting.triggered.connect(self.toggle_output_format)

    def button_actions(self):
        self.compile_button.clicked.connect(self.compile_prompt)
        self.pb_choose_folder.clicked.connect(lambda: self.choose_directory(self.project_path_lineedit))
        self.pb_projectopen.clicked.connect(self.open_project)
        self.pb_projectsave.clicked.connect(self.save_project)
        self.pb_copyfiletree.clicked.connect(self.copy_file_tree_to_tab)
        self.pb_loadgitignore.clicked.connect(self.load_ignore)
        self.pb_add_file_content.clicked.connect(self.add_selected_item_and_dependencies_to_prompt)
        self.pb_add_file_content_all.clicked.connect(self.add_all_files_content_to_prompt)
        self.pb_projectnew.clicked.connect(self.new_project)
        self.pb_enhance.clicked.connect(lambda: self.call_llm_api(self.tedit_tab1))  # Connect to the api button
        self.pb_refresh.clicked.connect(self.refresh_file_tree)
        self.pb_add_files_context.clicked.connect(self.add_files_to_context)
        self.pb_add_folder_context.clicked.connect(self.add_folder_to_context)
        self.pb_clear_files_selection.clicked.connect(self.clear_files_tab_and_selection)
        # self.actionToggle_logging.triggered.connect(self.toggle_logging)

        # Connect the combo box and push button for role prompts tab
        self.pb_tab2_load_example.clicked.connect(
            lambda: self.load_from_combobox("role_prompts", self.cb_tab2_load_example, self.tedit_tab2)
        )

        self.pb_add_patch.clicked.connect(self.add_patch)
        self.pb_remove_patch.clicked.connect(self.remove_selected_patch)
        self.patch_list.itemDoubleClicked.connect(self.preview_patch)

    def clear_files_tab_and_selection(self):
        """Clears the master set of files for the 'Files' tab and updates the UI."""
        if not self.files_added_to_files_tab and not self.tedit_tab5.toPlainText():
            return

        confirmation = self.warning_message.message_box_with_accept(
            "Confirm Clear",
            "Are you sure you want to clear all selected files from the 'Files' tab?"
        )
        if confirmation:
            self.files_added_to_files_tab.clear()
            self._rebuild_files_tab_content() # This will clear tedit_tab5
            
    def populate_comboboxes(self):
        populate_comboboxes(self, "data/role_prompts", self.cb_tab2_load_example)

    def load_from_combobox(self, folder: str, combobox, text_edit):
        self.file_handler.load_from_combobox(folder, combobox, text_edit)

    def toggle_output_format(self):
        if self.actionXML_JSON_Formatting.isChecked():
            self.output_type = "json"
        else:
            self.output_type = "xml"
        self._rebuild_files_tab_content()  # Rebuild if format changes

    def new_project(self, silent: bool = False):
        """Clears all text fields, the tree view, and the compiled prompt.
        Requests confirmation before creating a new project.
        """
        if not silent:
            confirmation = self.warning_message.message_box_with_accept(
                "Confirm New Project",
                "Are you sure you want to clear all fields and start a new project?",
            )
        else:
            confirmation = True

        if confirmation:
            self.prompt_builder.clear_all_text_fields()  # This clears tedit_tab5 as well
            self.treeView.clear()
            self.project_path_lineedit.clear()
            self.ignore_patterns = []
            self.label_char_count.setText("Characters: 0")
            self.label_token_count.setText("Tokens: 0")
            self.label_line_count.setText("Lines: 0")
            self.api_key_path = ""
            self.project_data = {}
            self.files_added_to_files_tab.clear()
            self.patches.clear()
            self.patch_list.clear()
            # tedit_tab5 is already cleared by prompt_builder.clear_all_text_fields()

    def add_patch(self):
        patch_text = self.patch_input.toPlainText().strip()
        if patch_text:
            self.patches.append(patch_text)
            self.patch_list.addItem(f"Patch {len(self.patches)}")
            self.patch_input.clear()

    def preview_patch(self, item):
        index = self.patch_list.row(item)
        if 0 <= index < len(self.patches):
            QMessageBox.information(self, f"Patch {index + 1}", self.patches[index])

    def remove_selected_patch(self):
        row = self.patch_list.currentRow()
        if row >= 0:
            self.patches.pop(row)
            self.patch_list.takeItem(row)
            for i in range(self.patch_list.count()):
                self.patch_list.item(i).setText(f"Patch {i + 1}")

    def choose_directory(self, line_edit):
        selected_folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if selected_folder:
            line_edit.setText(selected_folder)
            self.project_data["project_path"] = selected_folder
            self.load_default_ignore(silent=False)
            self.list_project_content(selected_folder)

    def setup_tree_view(self):
        self.treeView.setHeaderHidden(True)
        self.treeView.setColumnCount(1)

    def load_default_ignore(self, silent=False):
        project_path = self.project_path_lineedit.text().strip()
        if self.loaded_ignore:
            self.ignore_patterns = self.file_handler.load_default_ignore(self.loaded_ignore, silent)
        else:
            self.ignore_patterns = self.file_handler.load_default_ignore(os.getcwd(), silent=True)
        if project_path:
            self.list_project_content(project_path)

    def list_project_content(self, folder_path: str):
        update_tree_view(self, folder_path)

    def load_ignore(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load .ignore", "", ".ignore Files (*)")
        if file_path:
            self.ignore_patterns = self.file_handler.load_ignore(file_path)
            self.list_project_content(self.project_path_lineedit.text())
            self.loaded_ignore = os.path.dirname(file_path)

    def copy_file_tree_to_tab(self):
        project_path = self.project_path_lineedit.text().strip()
        if project_path:
            file_tree_str = f"Project Folder: {project_path}\nProject Content: \n"
            file_tree_str += self.file_handler.get_file_tree_string(self.treeView.invisibleRootItem(), 0)
            self.tedit_tab4.setPlainText(file_tree_str)

    def _collect_files_from_tree_item_recursive(self, tree_item, collected_files_set):
        for i in range(tree_item.childCount()):
            child = tree_item.child(i)
            child_path = child.data(0, Qt.ItemDataRole.UserRole)
            if os.path.isfile(child_path):
                collected_files_set.add(os.path.normpath(os.path.abspath(child_path)))
            elif os.path.isdir(child_path):
                self._collect_files_from_tree_item_recursive(child, collected_files_set)

    def _rebuild_files_tab_content(self):
        output_tab_text_edit = self.tedit_tab5
        output_tab_text_edit.clear()

        sorted_files_for_display = sorted(
            list(self.files_added_to_files_tab), key=lambda x: (os.path.dirname(x).lower(), os.path.basename(x).lower())
        )

        for f_path in sorted_files_for_display:
            file_content = self.file_handler.read_file_content(f_path)
            if file_content:
                if self.actionLine_Enumerator.isChecked():
                    self.prompt_builder._add_file_content_with_line_numbers(
                        output_tab_text_edit, f_path, file_content, output_type=self.output_type, silent=True
                    )
                else:
                    self.prompt_builder._add_file_content_without_line_numbers(
                        output_tab_text_edit, f_path, file_content, output_type=self.output_type, silent=True
                    )
        self.update_text_counts(self.plainTextEdit_12.toPlainText())  # Update counts for compiled prompt
        # Potentially update counts for tedit_tab5 if needed

    def add_selected_item_and_dependencies_to_prompt(self):
        selected_items = self.treeView.selectedItems()
        if not selected_items:
            self.warning_message.message_box("Warning", "Select a file or folder from the file tree.")
            return
        if len(selected_items) > 1:
            self.warning_message.message_box("Warning", "Select only one item at a time for this action.")
            return

        selected_item = selected_items[0]
        item_path_from_tree = selected_item.data(0, Qt.ItemDataRole.UserRole)
        project_root = self.project_path_lineedit.text().strip()

        files_to_process_for_this_click = set()

        if os.path.isfile(item_path_from_tree):
            abs_item_path = os.path.normpath(os.path.abspath(item_path_from_tree))
            if item_path_from_tree.endswith(".py") and project_root:
                try:
                    analyzer = DependencyAnalyzer(project_root)
                    dependencies = analyzer.find_all_dependencies(item_path_from_tree)  # Expects non-normalized?
                    # Ensure dependencies are normalized absolute paths
                    files_to_process_for_this_click.update(os.path.normpath(os.path.abspath(p)) for p in dependencies)
                except Exception as e:
                    self.warning_message.message_box(
                        "Error", f"Error analyzing dependencies for {os.path.basename(item_path_from_tree)}: {e}"
                    )
                    files_to_process_for_this_click.add(abs_item_path)
            else:
                files_to_process_for_this_click.add(abs_item_path)
        elif os.path.isdir(item_path_from_tree):
            self._collect_files_from_tree_item_recursive(selected_item, files_to_process_for_this_click)

        if not files_to_process_for_this_click:
            self.warning_message.message_box("Info", "No files found to add for the selected item.")
            return

        newly_added_to_master_set_count = 0
        for f_path in files_to_process_for_this_click:
            # Paths should already be normalized absolute from collection logic
            if f_path not in self.files_added_to_files_tab:
                self.files_added_to_files_tab.add(f_path)
                newly_added_to_master_set_count += 1

        self._rebuild_files_tab_content()

        if newly_added_to_master_set_count > 0:
            message = (
                f"Added {newly_added_to_master_set_count} new file(s) and refreshed the 'Files' tab. "
                f"Total {len(self.files_added_to_files_tab)} file(s) shown."
            )
        elif files_to_process_for_this_click:
            message = (
                f"Selected file(s) were already included. 'Files' tab refreshed with "
                f"{len(self.files_added_to_files_tab)} file(s)."
            )
        else:  # Should be caught by "No files found" earlier
            message = "'Files' tab refreshed."
        self.warning_message.message_box("Success", message)

    def add_all_files_content_to_prompt(self):
        paths_from_builder = self.prompt_builder.get_all_project_files_for_prompt()

        newly_added_to_master_set_count = 0
        for f_path in paths_from_builder:
            normalized_f_path = os.path.normpath(os.path.abspath(f_path))
            if normalized_f_path not in self.files_added_to_files_tab:
                self.files_added_to_files_tab.add(normalized_f_path)
                newly_added_to_master_set_count += 1

        self._rebuild_files_tab_content()

        message = (
            f"Processed all project files. {newly_added_to_master_set_count} new file(s) added to selection. "
            f"Total {len(self.files_added_to_files_tab)} file(s) now shown in 'Files' tab."
        )
        self.warning_message.message_box("Success", message)

    def add_files_to_context(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Context Files", "", "All Files (*);;Text Files (*.txt *.md)"
        )
        self.prompt_builder.add_files_to_context(file_paths)

    def add_folder_to_context(self):
        selected_folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if selected_folder:
            self.prompt_builder.add_folder_files_content_to_prompt(selected_folder)

    def compile_prompt(self):
        final_prompt = self.prompt_builder.compile_prompt()
        self.plainTextEdit_12.setPlainText(final_prompt)
        self.update_text_counts(final_prompt)

    def update_text_counts(self, text):
        word_count, char_count, line_count = self.text_processor.count_text_properties(text)
        self.label_token_count.setText(f"Tokens: {word_count}")
        self.label_char_count.setText(f"Characters: {char_count}")
        self.label_line_count.setText(f"Lines: {line_count}")

    def save_project(self):
        self.project_manager.save_project(self)

    def open_project(self):
        self.project_manager.open_project(self)
        # After project data is loaded, including self.files_added_to_files_tab,
        # rebuild the "Files" tab content.
        self._rebuild_files_tab_content()

    def toggle_logging(self):
        self.llm_handler.enable_logging = not self.llm_handler.enable_logging
        if self.llm_handler.enable_logging:
            self.warning_message.message_box("Info", "LLM Logging is enabled")
        else:
            self.warning_message.message_box("Info", "LLM Logging is disabled")

    def load_file_content(self, file_path) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found.")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def refresh_file_tree(self):
        self.load_default_ignore(silent=True)

    def call_llm_api(self, text_box: QPlainTextEdit):
        user_input = text_box.toPlainText().strip()
        # Ensure role_data and structure_data paths are correct or handle errors
        try:
            role_data = self.load_file_content("core/agents/enhance_input/role.md")
            structure_data = self.load_file_content("core/agents/enhance_input/structure.md")
        except FileNotFoundError as e:
            self.warning_message.message_box("Error", f"Required agent file not found: {e}")
            return

        if not user_input or not role_data or not structure_data:
            self.warning_message.message_box("Warning", "Please fill the required fields before calling the API")
            return
        try:
            selected_api = self.cb_api.currentText()
            if "Choose" in selected_api:
                self.warning_message.message_box("Warning", "Please select the API")
                return
            else:
                if not self.llm_handler.load_api_key(api=selected_api, key=self.api_key_path):
                    return
            self.warning_message.message_box("Info", "Calling the LLM API, please wait")
            thought_process, response = self.llm_handler.call_api(user_input, role_data, structure_data)

            self.llm_handler.log_output(
                {
                    "user_input": user_input,
                    "thought_process": thought_process,  # May be None
                    "enhanced_prompt": response.get("enhanced_prompt"),
                    "explanation": response.get("explanation"),
                    "additional_info": response.get("additional_info"),
                },
                self.llm_handler.LOG_FILE,
            )
            self.llm_handler.save_output(response, self.llm_handler.LOG_FILE)  # This probably should be unique name

            review_dialog = ReviewDialog(response["enhanced_prompt"], self)
            review_dialog.exec()

            if review_dialog.get_accepted():
                text_box.setPlainText(response["enhanced_prompt"])
        except Exception as e:
            self.warning_message.message_box("Error", f"Error during the LLM API Call: {e}")
