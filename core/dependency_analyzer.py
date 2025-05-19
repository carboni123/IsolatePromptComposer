# core/dependency_analyzer.py
import ast
import os


class DependencyAnalyzer:
    def __init__(self, project_root):
        self.project_root = self._normalize_path(project_root)

    def _normalize_path(self, path):
        return os.path.normpath(os.path.abspath(path))

    def _is_project_file(self, file_path):
        if not file_path:
            return False
        abs_file_path = self._normalize_path(file_path)
        return (
            abs_file_path.startswith(self.project_root)
            and os.path.exists(abs_file_path)
            and os.path.isfile(abs_file_path)
        )

    def _resolve_module_path(self, module_name_parts, base_dir):
        # Try as a .py file
        potential_path_py = os.path.join(base_dir, *module_name_parts) + ".py"
        if self._is_project_file(potential_path_py):
            return self._normalize_path(potential_path_py)

        # Try as a package (directory with __init__.py)
        potential_path_pkg = os.path.join(base_dir, *module_name_parts, "__init__.py")
        if self._is_project_file(potential_path_pkg):
            return self._normalize_path(potential_path_pkg)

        return None

    def _resolve_import(self, module_str, level, current_file_path):
        current_file_dir = os.path.dirname(current_file_path)

        if level > 0:  # Relative import
            base_relative_dir = current_file_dir
            for _ in range(level - 1):
                base_relative_dir = os.path.dirname(base_relative_dir)

            if not module_str:
                return None

            module_parts = module_str.split(".")
            return self._resolve_module_path(module_parts, base_relative_dir)
        else:  # Absolute import
            if not module_str:
                return None
            module_parts = module_str.split(".")

            path_from_proj_root = self._resolve_module_path(module_parts, self.project_root)
            if path_from_proj_root:
                return path_from_proj_root
        return None

    def _extract_imports_from_file(self, file_path):
        imports = set()
        if not file_path.endswith(".py"):
            return imports

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return imports

        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            return imports

        for node in ast.walk(tree):
            resolved_path = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    resolved_path = self._resolve_import(alias.name, 0, file_path)
                    if resolved_path:
                        imports.add(resolved_path)
            elif isinstance(node, ast.ImportFrom):
                module_name_from_node = node.module

                if node.level > 0 and not module_name_from_node:  # e.g., `from . import foo`
                    for alias in node.names:
                        resolved_path = self._resolve_import(alias.name, node.level, file_path)
                        if resolved_path:
                            imports.add(resolved_path)
                elif module_name_from_node:  # e.g., `from .foo import bar` or `from package import baz`
                    resolved_path = self._resolve_import(module_name_from_node, node.level, file_path)
                    if resolved_path:
                        imports.add(resolved_path)
        return imports

    def find_all_dependencies(self, start_file_path):
        norm_start_file_path = self._normalize_path(start_file_path)
        if not self._is_project_file(norm_start_file_path):
            return set()

        processing_pipeline = [norm_start_file_path]
        all_found_deps = set()
        queued_for_processing = {norm_start_file_path}

        head = 0
        while head < len(processing_pipeline):
            current_file = processing_pipeline[head]
            head += 1

            if current_file in all_found_deps:
                continue

            all_found_deps.add(current_file)

            # Special handling for your project's api/__init__.py dynamic imports
            api_init_path_check = self._normalize_path(os.path.join(self.project_root, "api", "__init__.py"))
            if current_file == api_init_path_check:
                api_dir = os.path.dirname(current_file)
                try:
                    for item_name in os.listdir(api_dir):
                        # Mimic the logic in your api/__init__.py _discover_apis
                        if item_name.endswith(".py") and item_name != "__init__.py" and item_name != "api.py":
                            dynamic_dep_path = self._normalize_path(os.path.join(api_dir, item_name))
                            if (
                                self._is_project_file(dynamic_dep_path)
                                and dynamic_dep_path not in queued_for_processing
                            ):
                                processing_pipeline.append(dynamic_dep_path)
                                queued_for_processing.add(dynamic_dep_path)
                except FileNotFoundError:
                    pass

            direct_imports = self._extract_imports_from_file(current_file)
            for dep_path in direct_imports:
                if self._is_project_file(dep_path) and dep_path not in queued_for_processing:
                    processing_pipeline.append(dep_path)
                    queued_for_processing.add(dep_path)

        return all_found_deps
