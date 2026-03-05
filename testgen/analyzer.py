import ast
from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class ArgInfo:
    name: str
    annotation: Optional[str] = None
    default: Optional[str] = None
    is_optional: bool = False

@dataclass
class FunctionInfo:
    name: str
    lineno: int
    end_lineno: int
    args: List[ArgInfo]
    return_annotation: Optional[str]
    decorators: List[str]
    is_async: bool
    is_method: bool
    parent_class: Optional[str]
    docstring: Optional[str]
    source_code: str
    complexity_score: int

class Analyzer(ast.NodeVisitor):
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.lines = source_code.splitlines()
        self.functions: List[FunctionInfo] = []
        self.current_class: Optional[str] = None

    def visit_ClassDef(self, node: ast.ClassDef):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._process_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._process_function(node, is_async=True)

    def _process_function(self, node: Any, is_async: bool):
        # Skip private/protected unless __init__
        if node.name.startswith("_") and not node.name.startswith("__") and not node.name == "__init__":
             return
        if node.name.startswith("__") and not node.name == "__init__":
             return
        
        # Check for pytest fixtures
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        if any("fixture" in str(d) for d in decorators):
            return

        # Complexity
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1

        # Args
        args = []
        # Normal args
        defaults = [None] * (len(node.args.args) - len(node.args.defaults)) + node.args.defaults
        for arg, default in zip(node.args.args, defaults):
            if arg.arg == "self" or arg.arg == "cls":
                continue
            args.append(ArgInfo(
                name=arg.arg,
                annotation=ast.unparse(arg.annotation) if arg.annotation else None,
                default=ast.unparse(default) if default else None,
                is_optional=default is not None
            ))

        # Source
        source = "\n".join(self.lines[node.lineno-1:node.end_lineno])

        self.functions.append(FunctionInfo(
            name=node.name,
            lineno=node.lineno,
            end_lineno=node.end_lineno,
            args=args,
            return_annotation=ast.unparse(node.returns) if hasattr(node, "returns") and node.returns else None,
            decorators=decorators,
            is_async=is_async,
            is_method=self.current_class is not None,
            parent_class=self.current_class,
            docstring=ast.get_docstring(node),
            source_code=source,
            complexity_score=complexity
        ))

    def _get_decorator_name(self, node: Any) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{self._get_decorator_name(node.value)}.{node.attr}"
        if isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return "unknown"

def analyze_file(file_path: str) -> List[FunctionInfo]:
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    tree = ast.parse(code)
    analyzer = Analyzer(code)
    analyzer.visit(tree)
    return analyzer.functions
