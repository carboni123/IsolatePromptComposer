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
    def __init__(self, warning_message):
        self.warning_message = warning_message

    def clear_all_text_fields(self, main_window):
        for i in range(main_window.prompt_tab.count()):
            current_tab = main_window.prompt_tab.widget(i)
            text_edits = current_tab.findChildren(QPlainTextEdit)
            if text_edits:
                text_edit = text_edits[0]
                text_edit.clear()
        main_window.output_format_textedit.clear()
        main_window.plainTextEdit_12.clear()

    def add_file_content_to_prompt(self, main_window):
        selected_items = main_window.treeView.selectedItems()
        if not selected_items:
            self.warning_message.message_box(
                "Warning", "Select a file or folder from the file tree"
            )
            return
        if len(selected_items) > 1:
            self.warning_message.message_box(
                "Warning", "Select only one item at a time"
            )
            return

        selected_item = selected_items[0]
        file_path = selected_item.data(0, Qt.ItemDataRole.UserRole)

        if os.path.isfile(file_path):
            file_content = main_window.file_handler.read_file_content(file_path)
            if file_content:
                if main_window.actionLine_Enumerator.isChecked():
                    self._add_file_content_with_line_numbers(
                        main_window.tedit_tab5,
                        file_path,
                        file_content,
                        output_type=main_window.output_type,
                    )
                else:
                    self._add_file_content_without_line_numbers(
                        main_window.tedit_tab5,
                        file_path,
                        file_content,
                        output_type=main_window.output_type,
                    )
        elif os.path.isdir(file_path):
            # Process all files in the folder
            for root, _, files in os.walk(file_path):
                for file_name in files:
                    full_file_path = os.path.join(root, file_name)
                    file_content = main_window.file_handler.read_file_content(
                        full_file_path
                    )
                    if file_content:
                        if main_window.actionLine_Enumerator.isChecked():
                            self._add_file_content_with_line_numbers(
                                main_window.tedit_tab5,
                                full_file_path,
                                file_content,
                                output_type=main_window.output_type,
                                silent=True,
                            )
                        else:
                            self._add_file_content_without_line_numbers(
                                main_window.tedit_tab5,
                                full_file_path,
                                file_content,
                                output_type=main_window.output_type,
                                silent=True,
                            )
        else:
            self.warning_message.message_box("Warning", "Something went wrong!")

    def _add_file_content_with_line_numbers(
        self,
        text_edit: QPlainTextEdit,
        file_path,
        file_content,
        output_type="xml",
        silent=True,
    ):
        numbered_prompt = ""
        for i, line in enumerate(file_content.splitlines()):
            # - or → recommended as separator
            numbered_prompt += f"{i+1}→{line}\n"
        text_edit.appendPlainText(
            format_file_text(os.path.basename(file_path), numbered_prompt, output_type)
        )
        if not silent:
            self.warning_message.message_box(
                "Success",
                f"File content from {os.path.basename(file_path)} added to Files tab",
            )

    def _add_file_content_without_line_numbers(
        self,
        text_edit: QPlainTextEdit,
        file_path,
        file_content,
        output_type="xml",
        silent=True,
    ):
        text_edit.appendPlainText(
            format_file_text(os.path.basename(file_path), file_content, output_type)
        )
        if not silent:
            self.warning_message.message_box(
                "Success",
                f"File content from {os.path.basename(file_path)} added to Files tab",
            )

    def add_folder_files_content_to_prompt(self, main_window, folder_path):
        # Process all files in the folder
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                full_file_path = os.path.join(root, file_name)
                file_content = main_window.file_handler.read_file_content(
                    full_file_path
                )
                if file_content:
                    if main_window.actionLine_Enumerator.isChecked():
                        self._add_file_content_with_line_numbers(
                            main_window.tab_context,
                            full_file_path,
                            file_content,
                            output_type=main_window.output_type,
                            silent=True,
                        )
                    else:
                        self._add_file_content_without_line_numbers(
                            main_window.tab_context,
                            full_file_path,
                            file_content,
                            output_type=main_window.output_type,
                            silent=True,
                        )

    def add_all_files_content_to_prompt(self, main_window):
        root = main_window.treeView.invisibleRootItem()
        self._add_all_files_recursive(root, main_window)

    def add_files_to_context(self, main_window, file_paths):
        if file_paths:
            for file_path in file_paths:
                file_content = main_window.file_handler.read_file_content(file_path)
                if file_content:
                    main_window.tab_context.appendPlainText(
                        format_file_text(
                            os.path.basename(file_path),
                            file_content,
                            output_type=main_window.output_type,
                        )
                    )

    def _add_all_files_recursive(self, parent, main_window):
        if parent is None:
            return

        for i in range(parent.childCount()):
            child = parent.child(i)
            file_path = child.data(0, Qt.ItemDataRole.UserRole)

            if os.path.isfile(file_path):
                if not file_path.lower().endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".gif",
                        ".bmp",
                        ".tiff",
                        ".webp",
                        ".svg",
                        ".ico",
                        ".mp4",
                        ".mov",
                        ".avi",
                        ".mkv",
                        ".mp3",
                        ".wav",
                        ".ogg",
                    )
                ):
                    file_content = main_window.file_handler.read_file_content(file_path)
                    if file_content:
                        if main_window.actionLine_Enumerator.isChecked():
                            self._add_file_content_with_line_numbers(
                                main_window.tedit_tab5,
                                file_path,
                                file_content,
                                output_type=main_window.output_type,
                                silent=True,
                            )
                        else:
                            self._add_file_content_without_line_numbers(
                                main_window.tedit_tab5,
                                file_path,
                                file_content,
                                output_type=main_window.output_type,
                                silent=True,
                            )
            elif os.path.isdir(file_path):
                if os.path.basename(file_path).lower() != "media":
                    self._add_all_files_recursive(child, main_window)

    def compile_prompt(self, main_window):
        prompt_parts = []

        for i in range(main_window.prompt_tab.count()):
            # Get the tab text and corresponding widget
            tab_text = main_window.prompt_tab.tabText(i)
            tab_widget = main_window.prompt_tab.widget(i)

            # Find QPlainTextEdit within the widget
            text_edits = tab_widget.findChildren(QPlainTextEdit)
            if text_edits:
                text_edit = text_edits[0]
                # Get and clean text
                text_content = text_edit.toPlainText().strip()
                if text_content:  # Only include non-empty prompts
                    # Format the prompt part with <content> and add to list
                    prompt_parts.append(
                        f'<prompt type="{tab_text}">\n<content>\n{text_content}\n</content>\n</prompt>'
                    )
        # Join all parts into the final prompt
        final_prompt = "\n".join(prompt_parts)
        # Wrap all prompt parts in a root <prompts> element
        final_prompt = f"<prompts>\n{final_prompt}\n</prompts>"
        # Copy to clipboard
        QApplication.clipboard().setText(final_prompt)
        # Show warning message
        self.warning_message.message_box(
            "Prompt Copied", "The compiled prompt has been copied to your clipboard."
        )
        return final_prompt
