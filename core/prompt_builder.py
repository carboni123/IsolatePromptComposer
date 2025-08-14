# core/prompt_builder.py
import os
import json
from PySide6.QtWidgets import QApplication, QPlainTextEdit
from PySide6.QtCore import Qt


def format_file_text(file_path, content, output_type="xml"):
    # Assuming numbered_prompt is your processed text with line numbers
    if output_type == "json":
        content = json.dumps(
            {"file_name": os.path.basename(file_path), "content": content},
            ensure_ascii=False,
            indent=2,
        )
    elif output_type == "markdown":
        content = f"File: {os.path.basename(file_path)}\n```\n{content}\n```\n"
    else:
        # Use XML as default.
        content = f'<file name="{os.path.basename(file_path)}">{content}</file>'
    return content


class PromptBuilder:
    def __init__(self, warning_message, main_window):
        self.warning_message = warning_message
        self.main_window = main_window

    def clear_all_text_fields(self):
        for i in range(self.main_window.prompt_tab.count()):
            current_tab = self.main_window.prompt_tab.widget(i)
            text_edits = current_tab.findChildren(QPlainTextEdit)
            if text_edits:
                text_edit = text_edits[0]
                text_edit.clear()
        self.main_window.plainTextEdit_12.clear()

    # This method is no longer directly called by MainWindow for populating tedit_tab5.
    # It's kept for other potential uses or if add_file_content_to_prompt needs to be revived for a different purpose.
    # MainWindow's add_selected_item_and_dependencies_to_prompt now handles logic.
    def add_file_content_to_prompt(self):
        # This method's original purpose is now largely handled by
        # MainWindow.add_selected_item_and_dependencies_to_prompt and MainWindow._rebuild_files_tab_content
        # If this button/action is still wired, it might need to be rethought or call the MainWindow method.
        # For now, let's assume it's a legacy/alternative way or that the button calls the MainWindow method.
        self.warning_message.message_box("Info", "This specific action might be deprecated or handled by 'Add Selected (+Deps)'.")


    def _add_file_content_with_line_numbers(
        self,
        text_edit: QPlainTextEdit,
        file_path,
        file_content,
        output_type="xml",
        silent=True, # silent is now always true as MainWindow manages messages
    ):
        numbered_prompt = ""
        for i, line in enumerate(file_content.splitlines()):
            numbered_prompt += f"{i+1}→{line}\n"
        text_edit.appendPlainText(format_file_text(os.path.basename(file_path), numbered_prompt, output_type))
        # MainWindow handles success messages now.

    def _add_file_content_without_line_numbers(
        self,
        text_edit: QPlainTextEdit,
        file_path,
        file_content,
        output_type="xml",
        silent=True, # silent is now always true
    ):
        text_edit.appendPlainText(format_file_text(os.path.basename(file_path), file_content, output_type))
        # MainWindow handles success messages now.


    def add_folder_files_content_to_prompt(self, folder_path):
        # This method populates the "Context" tab (self.main_window.tab_context)
        # It is distinct from the "Files" tab (tedit_tab5) logic.
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                full_file_path = os.path.join(root, file_name)
                # Consider ignoring binary files here too if not desired in context
                file_content = self.main_window.file_handler.read_file_content(full_file_path)
                if file_content:
                    # For context, line numbers might not be desired, or could be an option
                    # For now, adding without line numbers to context tab.
                    self._add_file_content_without_line_numbers(
                        self.main_window.tab_context, # Target "Context" tab
                        full_file_path,
                        file_content,
                        output_type=self.main_window.output_type,
                        silent=True, 
                    )

    def get_all_project_files_for_prompt(self):
        collected_files = set()
        root = self.main_window.treeView.invisibleRootItem()
        self._collect_all_files_recursive_for_paths(root, collected_files)
        return collected_files

    def _collect_all_files_recursive_for_paths(self, parent_item, collected_files_set):
        if parent_item is None:
            return

        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            # UserRole data should be absolute path from tree population
            file_path = child.data(0, Qt.ItemDataRole.UserRole) 

            if os.path.isfile(file_path):
                excluded_extensions = (
                    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".ico",
                    ".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav", ".ogg",
                )
                if not file_path.lower().endswith(excluded_extensions):
                    collected_files_set.add(os.path.normpath(file_path)) # Ensure normalized
            elif os.path.isdir(file_path):
                # Respect ignore patterns if necessary (current tree view build already does)
                # Or specific folder names like "media"
                # Current tree view already filters by .ignore, so items in tree are "valid"
                # We might want to add an additional explicit check here if needed
                # e.g. if os.path.basename(file_path).lower() not in self.main_window.ignore_patterns_for_folders_like_media:
                self._collect_all_files_recursive_for_paths(child, collected_files_set)


    def add_files_to_context(self, file_paths):
        # This method populates the "Context" tab (self.main_window.tab_context)
        if file_paths:
            for file_path in file_paths:
                file_content = self.main_window.file_handler.read_file_content(file_path)
                if file_content:
                    # Adding to context tab, usually without line numbers
                    self.main_window.tab_context.appendPlainText(
                        format_file_text(
                            os.path.basename(file_path),
                            file_content,
                            output_type=self.main_window.output_type,
                        )
                    )

    def compile_prompt(self):
        prompt_parts = []
        for i in range(self.main_window.prompt_tab.count()):
            tab_text = self.main_window.prompt_tab.tabText(i)
            tab_widget = self.main_window.prompt_tab.widget(i)

            if tab_text == "Patch Comparison":
                if self.main_window.patches:
                    patches_xml = "\n".join(
                        f"<patch_{idx}>{patch}</patch_{idx}>" for idx, patch in enumerate(self.main_window.patches, 1)
                    )
                    patch_prompt = (
                        "Given the following patches, make a comparison and select the best version. "
                        "If there is a mix of ideas between patches, suggest tasks to further refine the best patch\n"
                        f"{patches_xml}"
                    )
                    prompt_parts.append(f'<prompt type="{tab_text}">\n{patch_prompt}\n</prompt>')
                continue

            text_edits = tab_widget.findChildren(QPlainTextEdit)
            if text_edits:
                text_edit = text_edits[0]
                text_content = text_edit.toPlainText().strip()
                if text_content:
                    prompt_parts.append(f'<prompt type="{tab_text}">\n{text_content}\n</prompt>')
        
        final_prompt = "\n".join(prompt_parts)
        final_prompt = f"<prompts>\n{final_prompt}\n</prompts>"
        
        QApplication.clipboard().setText(final_prompt)
        self.warning_message.message_box("Prompt Copied", "The compiled prompt has been copied to your clipboard.")
        return final_prompt