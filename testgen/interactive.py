from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from .generator import GeneratedTestSuite, TestCase

console = Console()

def review_test_suite(suite: GeneratedTestSuite) -> List[TestCase]:
    """Provides an interactive TUI for reviewing generated test cases."""
    console.print(Panel(
        f"[bold green]Reviewing tests for function:[/bold green] [yellow]{suite.function_name}[/yellow]",
        border_style="green"
    ))
    
    accepted_cases = []
    
    for i, tc in enumerate(suite.test_cases, 1):
        console.print(f"\n[bold]Test Case {i}/{len(suite.test_cases)}: {tc.name}[/bold]")
        console.print(f"[italic]{tc.description}[/italic]")
        
        syntax = Syntax(tc.code, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"{tc.category}"))
        
        choice = Prompt.ask(
            "Action",
            choices=["accept", "edit", "skip", "quit"],
            default="accept"
        )
        
        if choice == "accept":
            accepted_cases.append(tc)
        elif choice == "edit":
            # For simplicity in this CLI version, we'll prompt for manual override
            # A real version would open $EDITOR
            new_code = Prompt.ask("Paste new code (or press enter to keep current)")
            if new_code:
                tc.code = new_code
            accepted_cases.append(tc)
        elif choice == "skip":
            continue
        elif choice == "quit":
            break
            
    return accepted_cases

def show_summary(functions_analyzed: int, tests_generated: int, output_path: str):
    console.print(f"\n[bold green]✓ Generation Complete![/bold green]")
    console.print(f"Analyzed {functions_analyzed} functions.")
    console.print(f"Generated and wrote {tests_generated} test cases to [cyan]{output_path}[/cyan].")
