import os
import ast
from pathlib import Path
from typing import List, Dict

def find_test_file(source_file: str) -> Optional[str]:
    """Finds the corresponding test file for a source file."""
    path = Path(source_file)
    # Common patterns: test_{name}.py or {name}_test.py
    patterns = [
        f"test_{path.name}",
        path.name.replace(".py", "_test.py")
    ]
    
    # Check current directory
    for p in patterns:
        test_path = path.parent / p
        if test_path.exists():
            return str(test_path)
            
    # Check tests/ directory
    tests_dir = path.parent / "tests"
    if tests_dir.exists():
        for p in patterns:
            test_path = tests_dir / p
            if test_path.exists():
                return str(test_path)
                
    return None

def get_covered_functions(test_file: str) -> List[str]:
    """Extracts all test function names from a test file."""
    if not test_file or not os.path.exists(test_file):
        return []
        
    with open(test_file, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
        
    test_funcs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                test_funcs.append(node.name)
    return test_funcs

def map_coverage(source_funcs: List[str], test_funcs: List[str]) -> Dict[str, bool]:
    """Maps source functions to a boolean indicating if a test likely exists."""
    coverage_map = {}
    for func in source_funcs:
        # Simple heuristic: if any test function contains the source function name
        has_test = any(func in tf for tf in test_funcs)
        coverage_map[func] = has_test
    return coverage_map
