import argparse
import ast  # Abstract Syntax Tree
import os
import sys
from dataclasses import dataclass

from termcolor import colored


@dataclass
class Colors:
    filepath: str = "green"
    classname: str = "yellow"
    functionname: str = "red"
    argname: str = "blue"


@dataclass
class Messages:
    filepath_details: str = (
        "'{file_path}' (lines={lines}, functions={functions}, classes={classes})"
    )
    class_header: str = "\t{lineno:4} {class_name}"
    function_detail: str = (
        "\t\t{lineno:4} {function_name}({args_with_hints}) -> {return_type}{link}"
    )
    standalone_function: str = (
        "{lineno:04} {function_name}({args_with_hints}) -> {return_type}{link}"
    )
    error_processing: str = "Error processing {file_path}: {error}"
    summary: str = "\nTotal: Files={total_files}, Lines={total_lines}, Functions={total_functions}, Classes={total_classes}"


def list_classes_and_functions(script_path):
    with open(script_path, "r") as file:
        tree = ast.parse(file.read(), filename=script_path)

    class_details = []
    function_details = []
    import_details = []

    class FunctionVisitor(ast.NodeVisitor):
        def visit_Import(self, node):
            import_details.append((node.lineno, ast.unparse(node)))
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            import_details.append((node.lineno, ast.unparse(node)))
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            if isinstance(node.parent, ast.ClassDef):
                class_details[-1]["functions"].append(
                    (node.name, node.lineno, node.args.args, node.returns)
                )
            else:
                function_details.append(
                    (node.name, node.lineno, node.args.args, node.returns)
                )
            self.generic_visit(node)

        def visit_ClassDef(self, node):
            bases = [ast.unparse(base) for base in node.bases]
            class_details.append(
                {
                    "name": node.name,
                    "lineno": node.lineno,
                    "bases": bases,
                    "functions": [],
                }
            )
            self.generic_visit(node)

    def add_parent_info(node):
        for child in ast.iter_child_nodes(node):
            child.parent = node
            add_parent_info(child)

    add_parent_info(tree)

    visitor = FunctionVisitor()
    visitor.visit(tree)

    return class_details, function_details, import_details


def process_file(
    file_path, sort_items, sort_desc, header_only, show_imports, line_links
):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()

        class_details, function_details, import_details = list_classes_and_functions(
            file_path
        )

        if sort_items or sort_desc:
            reverse = sort_desc
            class_details.sort(key=lambda x: x["name"], reverse=reverse)
            for cls in class_details:
                cls["functions"].sort(key=lambda x: x[0], reverse=reverse)
            function_details.sort(key=lambda x: x[0], reverse=reverse)
            import_details.sort(key=lambda x: x[0], reverse=reverse)

        print(
            Messages.filepath_details.format(
                file_path=colored(os.path.abspath(file_path), Colors.filepath),
                lines=len(lines),
                functions=len(function_details)
                + sum(len(cls["functions"]) for cls in class_details),
                classes=len(class_details),
            )
        )

        if show_imports:
            for lineno, import_stmt in import_details:
                print(f"{lineno:6} {import_stmt}")
            print()

        if not header_only:
            for cls in class_details:
                base_classes = f"({', '.join(cls['bases'])})" if cls["bases"] else ""
                class_name = f"{colored(cls['name'], Colors.classname)}{base_classes}"
                print(
                    Messages.class_header.format(
                        lineno=cls["lineno"], class_name=class_name
                    )
                )
                for func in cls["functions"]:
                    args_with_hints = ", ".join(
                        f"{colored(arg.arg, Colors.argname)}{': ' + ast.unparse(arg.annotation) if arg.annotation and arg.arg != 'self' else ''}"
                        for arg in func[2]
                        if not (arg.arg == "self" and not arg.annotation)
                    )
                    return_type = ast.unparse(func[3]) if func[3] else "None"
                    function_name = f"{colored(func[0], Colors.functionname)}"
                    link = (
                        f" (vscode://file/{os.path.abspath(file_path)}:{func[1]})"
                        if line_links
                        else ""
                    )
                    print(
                        Messages.function_detail.format(
                            lineno=func[1],
                            function_name=function_name,
                            args_with_hints=args_with_hints,
                            return_type=return_type,
                            link=link,
                        )
                    )

            for func in function_details:
                args_with_hints = ", ".join(
                    f"{colored(arg.arg, Colors.argname)}: {ast.unparse(arg.annotation) if arg.annotation and arg.arg != 'self' else ''}"
                    for arg in func[2]
                    if not (arg.arg == "self" and not arg.annotation)
                )
                return_type = ast.unparse(func[3]) if func[3] else "None"
                function_name = f"{colored(func[0], Colors.functionname)}"
                link = (
                    f" (vscode://file/{os.path.abspath(file_path)}:{func[1]})"
                    if line_links
                    else ""
                )
                print(
                    Messages.standalone_function.format(
                        lineno=func[1],
                        function_name=function_name,
                        args_with_hints=args_with_hints,
                        return_type=return_type,
                        link=link,
                    )
                )

        return (
            len(lines),
            len(function_details) + sum(len(cls["functions"]) for cls in class_details),
            len(class_details),
        )

    except Exception as e:
        print(
            Messages.error_processing.format(file_path=file_path, error=e),
            file=sys.stderr,
        )
        return 0, 0, 0


def process_directory(
    directory, sort_items, sort_desc, header_only, show_imports, line_links
):
    total_files = 0
    total_lines = 0
    total_functions = 0
    total_classes = 0

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path) and file.endswith(".py"):
            print()
            lines, functions, classes = process_file(
                file_path, sort_items, sort_desc, header_only, show_imports, line_links
            )
            total_files += 1
            total_lines += lines
            total_functions += functions
            total_classes += classes

    print(
        Messages.summary.format(
            total_files=total_files,
            total_lines=total_lines,
            total_functions=total_functions,
            total_classes=total_classes,
        )
    )


def main():
    parser = argparse.ArgumentParser(
        description="Process some Python files or directories."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="List of files or directories to process.",
    )
    parser.add_argument(
        "--sorted",
        action="store_true",
        help="Sort the classes, class functions, and functions alphabetically.",
    )
    parser.add_argument(
        "--sorted_desc",
        action="store_true",
        help="Sort the classes, class functions, and functions in descending alphabetical order.",
    )
    parser.add_argument(
        "--header_only",
        action="store_true",
        help="Display only the header of the analysis, suppressing function details.",
    )
    parser.add_argument(
        "--show_imports",
        action="store_true",
        help="Display the import statements in the file.",
    )
    parser.add_argument(
        "--line_links",
        action="store_true",
        help="Include clickable VSCode file links for function definitions.",
    )

    args = parser.parse_args()

    if args.sorted and args.sorted_desc:
        print("Error: Cannot use --sorted and --sorted_desc together.")
        sys.exit(1)

    total_files = 0
    total_lines = 0
    total_functions = 0
    total_classes = 0

    for path in args.paths:
        if os.path.isfile(path) and path.endswith(".py"):
            lines, functions, classes = process_file(
                path,
                args.sorted,
                args.sorted_desc,
                args.header_only,
                args.show_imports,
                args.line_links,
            )
            total_files += 1
            total_lines += lines
            total_functions += functions
            total_classes += classes
        elif os.path.isdir(path):
            process_directory(
                path,
                args.sorted,
                args.sorted_desc,
                args.header_only,
                args.show_imports,
                args.line_links,
            )
        else:
            print(f"Skipping non-Python file: {path}")


if __name__ == "__main__":
    main()
