# testgen-ai 🤖

AI-powered unit test generator for Python. Analyzes your source code and generates comprehensive `pytest` test cases using GPT-4o.

## Features

- **AST Analysis**: Extracts function metadata, arguments, and cyclomatic complexity.
- **Test Detection**: Identifies functions that lack test coverage.
- **AI Generation**: Creates high-quality tests using GPT-4o, including edge cases and mocks.
- **Interactive Review**: Review and edit generated tests in a Rich TUI before saving.
- **Smart Merging**: Safely adds new tests to existing test files.
- **Auto-Formatting**: Integrated with `black` for perfectly formatted output.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/test-generator.git
   cd test-generator
   ```

2. **Install dependencies**:
   ```bash
   pip install .
   ```

3. **Configure OpenAI**:
   Create a `.env` file with your API key:
   ```env
   OPENAI_API_KEY=your-sk-...
   ```

## Usage

### Analyze a file
Find functions that need tests:
```bash
testgen analyze path/to/file.py
```

### Generate tests
Generate and review tests interactively:
```bash
testgen generate path/to/file.py
```

Options:
- `-y`, `--yes`: Auto-approve all tests (skip interactive review).
- `--merge`: Merge into existing test file.
- `-o`, `--output`: Specify custom output path.
- `-m`, `--model`: Choose OpenAI model (default: gpt-4o).

## Development

Run tests:
```bash
pytest tests/
```

## License

MIT
