import ast
import os
import sys


def list_classes_and_functions(script_path):
    with open(script_path, "r") as file:
        tree = ast.parse(file.read(), filename=script_path)

    class_details = []
    function_details = []

    class FunctionVisitor(ast.NodeVisitor):
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

    return class_details, function_details


def process_file(file_path):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()

        class_details, function_details = list_classes_and_functions(file_path)

        print(f"Functions in '{file_path}':")
        print(
            f"Number of lines: {len(lines)}, Number of functions: {len(function_details) + sum(len(cls['functions']) for cls in class_details)}, Number of classes: {len(class_details)}"
        )

        for cls in class_details:
            base_classes = f"({', '.join(cls['bases'])})" if cls["bases"] else ""
            class_name = f"\033[93m{cls['name']}\033[0m{base_classes}"  # ANSI code for yellow text for class name only
            print(f"{cls['lineno']:10} {class_name}")
            for func in cls["functions"]:
                args_with_hints = ", ".join(
                    f"\033[94m{arg.arg}\033[0m: {ast.unparse(arg.annotation) if arg.annotation else 'Any'}"
                    for arg in func[2]
                )
                return_type = ast.unparse(func[3]) if func[3] else "None"
                function_name = f"\033[91m{func[0]}\033[0m"  # ANSI code for red text
                print(
                    f"{'':14}{func[1]:10} {function_name}({args_with_hints}) -> {return_type}"
                )

        for func in function_details:
            args_with_hints = ", ".join(
                f"\033[94m{arg.arg}\033[0m: {ast.unparse(arg.annotation) if arg.annotation else 'Any'}"
                for arg in func[2]
            )
            return_type = ast.unparse(func[3]) if func[3] else "None"
            function_name = f"\033[91m{func[0]}\033[0m"  # ANSI code for red text
            print(f"{func[1]:10} {function_name}({args_with_hints}) -> {return_type}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)


def process_directory(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path) and file.endswith(".py"):
            process_file(file_path)


def main(paths):
    for path in paths:
        if os.path.isfile(path) and path.endswith(".py"):
            process_file(path)
        elif os.path.isdir(path):
            process_directory(path)
        else:
            print(f"Skipping non-Python file: {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <file_or_directory1> <file_or_directory2> ...")
    else:
        main(sys.argv[1:])
