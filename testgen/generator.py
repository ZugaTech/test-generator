import os
import json
import ast
from typing import List, Dict, Any
from openai import AsyncOpenAI
from .analyzer import FunctionInfo

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@dataclass
class TestCase:
    name: str
    description: str
    code: str
    category: str

@dataclass
class GeneratedTestSuite:
    function_name: str
    test_cases: List[TestCase]
    imports_needed: List[str]

async def generate_tests(func_info: FunctionInfo, config: Dict[str, Any]) -> GeneratedTestSuite:
    """Generates pytest test cases for a given function using GPT-4o."""
    model = config.get("model", "gpt-4o")
    coverage_target = config.get("coverage_target", 3)
    include_edge_cases = config.get("include_edge_cases", True)
    include_mocks = config.get("include_mocks", True)

    system_prompt = (
        "You are an expert Python engineer. Generate comprehensive pytest test cases for the provided function. "
        "Follow these rules:\n"
        "1. Use descriptive test names following 'test_given_X_when_Y_then_Z'.\n"
        "2. Use pytest fixtures where appropriate.\n"
        f"3. Aim for {coverage_target} test cases per function.\n"
        "4. Provide only valid Python code in each test case.\n"
        "5. Output MUST be valid JSON with 'test_cases' (list of {name, description, code, category}) and 'imports_needed' (list of strings)."
    )
    
    if include_edge_cases:
        system_prompt += "\nInclude edge cases like None inputs, zero, empty collections, and boundary values."
    if include_mocks:
        system_prompt += "\nUse unittest.mock.patch for external I/O or dependencies."

    # Context: Function source and metadata
    user_prompt = f"""
Function Source:
```python
{func_info.source_code}
```

Metadata:
- Name: {func_info.name}
- Args: {[{arg.name: arg.annotation} for arg in func_info.args]}
- Return: {func_info.return_annotation}
- Complexity: {func_info.complexity_score}
- Is Method: {func_info.is_method}
- Parent Class: {func_info.parent_class}
- Async: {func_info.is_async}

Generate the test cases now.
"""

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.2
    )

    data = json.loads(response.choices[0].message.content)
    test_cases = [
        TestCase(**tc) for tc in data.get("test_cases", [])
    ]
    
    # Validate syntactic correctness
    valid_test_cases = []
    for tc in test_cases:
        try:
            ast.parse(tc.code)
            valid_test_cases.append(tc)
        except SyntaxError:
            continue

    return GeneratedTestSuite(
        function_name=func_info.name,
        test_cases=valid_test_cases,
        imports_needed=data.get("imports_needed", [])
    )
