import asyncio
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from pathlib import Path

from .analyzer import analyze_file
from .test_detector import find_test_file, get_covered_functions, map_coverage
from .generator import generate_tests, GeneratedTestSuite
from .writer import write_tests
from .interactive import review_test_suite, show_summary
from .config import get_config

app = typer.Typer(help="AI-powered unit test generator for Python")
console = Console()

@app.command()
def analyze(file: str):
    """Analyzes a Python file and shows functions needing tests."""
    if not Path(file).exists():
        console.print(f"[bold red]Error:[/bold red] File {file} not found.")
        raise typer.Exit(1)
        
    funcs = analyze_file(file)
    test_file = find_test_file(file)
    test_funcs = get_covered_functions(test_file) if test_file else []
    coverage = map_coverage([f.name for f in funcs], test_funcs)
    
    table = Table(title=f"Analysis: {file}")
    table.add_column("Function", style="cyan")
    table.add_column("Line", style="magenta")
    table.add_column("Complexity", style="green")
    table.add_column("Has Test", style="yellow")
    
    for f in funcs:
        has_test = "✓" if coverage.get(f.name) else "✗"
        table.add_row(f.name, str(f.lineno), str(f.complexity_score), has_test)
        
    console.print(table)

@app.command()
def generate(
    file: str,
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output test file path"),
    model: str = typer.Option("gpt-4o", "--model", "-m"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Auto-approve all generated tests"),
    merge: bool = typer.Option(False, "--merge", help="Merge into existing test file")
):
    """Generates tests for a Python file."""
    asyncio.run(_async_generate(file, output, model, yes, merge))

async def _async_generate(file: str, output: Optional[str], model: str, yes: bool, merge: bool):
    config = get_config()
    config_dict = config.model_dump()
    config_dict["model"] = model
    
    funcs = analyze_file(file)
    test_file = find_test_file(file)
    test_funcs = get_covered_functions(test_file) if test_file else []
    coverage = map_coverage([f.name for f in funcs], test_funcs)
    
    # Filter for functions needing tests (or all if forced)
    to_generate = [f for f in funcs if not coverage.get(f.name)]
    if not to_generate:
        console.print("[bold yellow]No untested functions found.[/bold yellow]")
        if not Confirm.ask("Generate tests anyway for all functions?"):
             return
        to_generate = funcs

    final_suites = []
    for f in to_generate:
        console.print(f"Generating tests for [cyan]{f.name}[/cyan]...")
        suite = await generate_tests(f, config_dict)
        
        if yes:
            final_suites.append(suite)
        else:
            accepted_cases = review_test_suite(suite)
            if accepted_cases:
                suite.test_cases = accepted_cases
                final_suites.append(suite)

    if not final_suites:
        console.print("[bold red]No tests were accepted or generated.[/bold red]")
        return

    # Determine output path
    if not output:
        path = Path(file)
        output = str(path.parent / f"test_{path.name}")

    result = write_tests(final_suites, file, output, merge_mode=merge)
    show_summary(len(funcs), result.test_cases_written, result.output_path)

if __name__ == "__main__":
    app()
