# ui/main_window.py
import os
from PySide6.QtUiTools import loadUiType
from PySide6.QtWidgets import QFileDialog, QMessageBox, QPlainTextEdit, QLabel, QDialog, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from ui.utils.dialogs import WarningBox
from core.project_tree_view import update_tree_view, populate_comboboxes
from ui.utils.text_processor import TextProcessor
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
        self.setWindowIcon(QIcon(os.path.join('media','logo.png')))

        self.warning_message = WarningBox()
        self.file_handler = FileHandler(self.warning_message)
        self.prompt_builder = PromptBuilder(self.warning_message)
        self.project_manager = ProjectManager(self.warning_message)
        self.text_processor = TextProcessor()
        self.llm_handler = LLMHandler(self.warning_message)
        self.api_key_path = ""

        self.project_data = {}
        self.ignore_patterns = []
        self.loaded_ignore = ""
        self.output_type = "xml"

        self.button_actions()  
        self.toolbar_actions()
        self.setup_tree_view()
        self.populate_comboboxes()
        self.le_search.hide() # Not implemented
        self.pb_thoughts.hide() # Not implemented
        # self.label_api.mousePressEvent = self.load_api_key # Set the mouse event

    def toolbar_actions(self):
        self.actionNew_Project.triggered.connect(self.new_project)
        self.actionOpen_Project.triggered.connect(self.open_project)
        self.actionSave_Project.triggered.connect(self.save_project)
        self.actionExport_Project.triggered.connect(self.save_project)
        self.actionAbout.triggered.connect(show_about_info)
        self.actionAbout_PySide.triggered.connect(show_about_pyside)
        self.actionAbout_Google_AI_Studio.triggered.connect(show_about_googleaistudio)
        self.actionMute_Warnings.triggered.connect(lambda: self.warning_message.mute(self.actionMute_Warnings.isChecked()))
        self.actionXML_JSON_Formatting.triggered.connect(self.toggle_output_format)

    def button_actions(self):
        self.compile_button.clicked.connect(self.compile_prompt)
        self.pb_choose_folder.clicked.connect(lambda: self.choose_directory(self.project_path_lineedit))
        self.pb_projectopen.clicked.connect(self.open_project)
        self.pb_projectsave.clicked.connect(self.save_project)
        self.pb_copyfiletree.clicked.connect(self.copy_file_tree_to_tab)
        self.pb_loadgitignore.clicked.connect(self.load_ignore)
        self.pb_add_file_content.clicked.connect(self.add_file_content_to_prompt)
        self.pb_add_file_content_all.clicked.connect(self.add_all_files_content_to_prompt)
        self.pb_projectnew.clicked.connect(self.new_project)
        self.pb_enhance.clicked.connect(lambda: self.call_llm_api(self.tedit_tab1)) # Connect to the api button
        self.pb_refresh.clicked.connect(self.refresh_file_tree)
        self.pb_add_files_context.clicked.connect(self.add_files_to_context)
        self.pb_add_folder_context.clicked.connect(self.add_folder_to_context)
        # self.actionToggle_logging.triggered.connect(self.toggle_logging)

        # Connect the combo box and push button for role prompts tab
        self.pb_tab2_load_example.clicked.connect(lambda: self.load_from_combobox("role_prompts", self.cb_tab2_load_example, self.tedit_tab2))
        # Connect the combo box and push button for constraint prompts tab
        self.pb_tab3_load_example.clicked.connect(lambda: self.load_from_combobox("constraint_prompts", self.cb_tab3_load_example, self.tedit_tab3))
        # Connect the combo box and push button for output format tab
        self.pb_tab_output_load_example.clicked.connect(lambda: self.load_from_combobox("structured_output", self.cb_tab_output_load_example, self.output_format_textedit))

    def populate_comboboxes(self):
        populate_comboboxes(self, "data/role_prompts", self.cb_tab2_load_example)
        populate_comboboxes(self, "data/constraint_prompts", self.cb_tab3_load_example)
        populate_comboboxes(self, "data/structured_output", self.cb_tab_output_load_example)

    def load_from_combobox(self, folder: str, combobox, text_edit):
        self.file_handler.load_from_combobox(folder, combobox, text_edit)


    def toggle_output_format(self):
        if self.actionXML_JSON_Formatting.isChecked():
            self.output_type = "json"
        else:
            self.output_type = "xml"

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
            self.prompt_builder.clear_all_text_fields(self)
            self.treeView.clear()
            self.project_path_lineedit.clear()
            self.ignore_patterns = []
            self.label_char_count.setText("Characters: 0")
            self.label_token_count.setText("Tokens: 0")
            self.label_line_count.setText("Lines: 0")
            # Reset Api key
            # self.label_api.setText("API Key: Click to load")
            self.api_key_path = ""
            self.project_data = {}

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
            # Uses the saved value when you load with Add Filter
            self.ignore_patterns = self.file_handler.load_default_ignore(self.loaded_ignore, silent)
        else:
            # Uses the .ignore file in the IsolatePromptComposer folder as default
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
            self.loaded_ignore = os.path.dirname(file_path) # ignore dir

    def copy_file_tree_to_tab(self):
        project_path = self.project_path_lineedit.text().strip()
        if project_path:
            file_tree_str = f"Project Folder: {project_path}\nProject Content: \n"
            file_tree_str += self.file_handler.get_file_tree_string(self.treeView.invisibleRootItem(), 0)
            self.tedit_tab4.setPlainText(file_tree_str)

    def add_file_content_to_prompt(self):
        self.prompt_builder.add_file_content_to_prompt(self)

    def add_all_files_content_to_prompt(self):
        self.prompt_builder.add_all_files_content_to_prompt(self)

    def add_files_to_context(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Context Files", "", "All Files (*);;Text Files (*.txt *.md)"
        )
        self.prompt_builder.add_files_to_context(self, file_paths)

    def add_folder_to_context(self):
        selected_folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if selected_folder:
            # append all files inside folder
            self.prompt_builder.add_folder_files_content_to_prompt(self, selected_folder)

    def compile_prompt(self):
        final_prompt = self.prompt_builder.compile_prompt(self)
        self.plainTextEdit_12.setPlainText(final_prompt)

        # Count tokens, chars and lines
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

    def toggle_logging(self):
        self.llm_handler.enable_logging = not self.llm_handler.enable_logging
        if self.llm_handler.enable_logging:
            self.warning_message.message_box("Info", "LLM Logging is enabled")
        else:
            self.warning_message.message_box("Info", "LLM Logging is disabled")

    # Load content from a file
    def load_file_content(self, file_path) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found.")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    # def load_api_key(self, event):
    #     file_path, _ = QFileDialog.getOpenFileName(self, "Load API Key", "", "API Key Files (*.key);;All Files (*.*)")
    #     if file_path:
    #         try:
    #             self.llm_handler.load_api_key(file_path)
    #             self.api_key_path = file_path
    #             self.label_api.setText(f"API Key: {os.path.basename(file_path)}")
    #             self.warning_message.message_box("Success", "API Key loaded successfully.")
    #         except Exception as e:
    #             self.warning_message.message_box("Error", f"Error loading API Key: {e}")

    def refresh_file_tree(self):
        self.load_default_ignore(silent=True)

    def call_llm_api(self, text_box:QPlainTextEdit):
        """
        This method is called when the "Call API" button is clicked.
        It gathers the necessary data, calls the LLM API, and shows the response.
        """
        # Get the user input, role data and structure data.
        user_input = text_box.toPlainText().strip()
        role_data = self.load_file_content("core/agents/enhance_input/role.md")
        structure_data = self.load_file_content("core/agents/enhance_input/structure.md")
        if not user_input or not role_data or not structure_data:
            self.warning_message.message_box("Warning", "Please fill the required fields before calling the API")
            return         
        try:
            # Load the LLM API
            selected_api = self.cb_api.currentText()
            if "Choose" in selected_api:
                self.warning_message.message_box("Warning", "Please select the API")
                return
            else:
                if not self.llm_handler.load_api_key(api=selected_api, key=self.api_key_path): # Load api key from path
                    return
            # Call the LLM API
            self.warning_message.message_box("Info", "Calling the LLM API, please wait")
            thought_process, response = self.llm_handler.call_api(user_input, role_data, structure_data)
            print(thought_process, response)
            # Log output
            self.llm_handler.log_output({
                "user_input": user_input,
                "thought_process": thought_process,
                "enhanced_prompt": response.get("enhanced_prompt"),
                "explanation": response.get("explanation"),
                "additional_info": response.get("additional_info")
            }, self.llm_handler.LOG_FILE)
            # Save Output
            self.llm_handler.save_output(response, self.llm_handler.LOG_FILE)
            # Open Review Dialog
            review_dialog = ReviewDialog(response["enhanced_prompt"], self)
            review_dialog.exec()

            # Display the response
            if review_dialog.get_accepted():
                text_box.setPlainText(response["enhanced_prompt"])
        except Exception as e:
            self.warning_message.message_box("Error", f"Error during the LLM API Call: {e}")
