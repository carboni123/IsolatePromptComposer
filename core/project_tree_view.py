# core/project_tree_view.py
import os
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtCore import Qt
import fnmatch


def populate_comboboxes(main_window, folder_path, combobox):
    combobox.clear()
    combobox.addItem("Custom")
    try:
        for filename in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, filename)):
                combobox.addItem(filename)
    except FileNotFoundError:
        main_window.warning_message.message_box(
            "Error", f"Folder not found: {folder_path}"
        )


def update_tree_view(main_window, folder_path: str):
    main_window.treeView.clear()
    if not folder_path:
        return
    root_item = QTreeWidgetItem(main_window.treeView, [os.path.basename(folder_path)])
    root_item.setData(0, Qt.ItemDataRole.UserRole, folder_path)
    _add_tree_items(main_window, root_item, folder_path)
    main_window.treeView.addTopLevelItem(root_item)
    root_item.setExpanded(True)


def _add_tree_items(main_window, parent_item: QTreeWidgetItem, path: str):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if not _is_ignored(main_window, item_path):
            tree_item = QTreeWidgetItem(parent_item, [item])
            tree_item.setData(0, Qt.ItemDataRole.UserRole, item_path)
            if os.path.isdir(item_path):
                _add_tree_items(main_window, tree_item, item_path)


def _is_ignored(main_window, path):
    for pattern in main_window.ignore_patterns:
        path_from_root = (
            path.replace(main_window.project_path_lineedit.text(), "")
            .lstrip(os.sep)
            .replace(os.sep, "/")
        )
        if fnmatch.fnmatch(path_from_root, pattern) or fnmatch.fnmatch(
            os.path.basename(path), pattern
        ):
            return True
    return False
