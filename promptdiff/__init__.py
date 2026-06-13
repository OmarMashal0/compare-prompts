"""
promptdiff — Compare LLM prompts side by side.

Usage:
    from promptdiff import compare

    compare(
        prompts={
            "original": "You are a helpful assistant.",
            "concise":  "You are a concise assistant.",
        },
        inputs=["Explain recursion.", "Write a haiku."],
        model="gpt-4o-mini"
    )
"""

from dotenv import load_dotenv
from promptdiff.runner import run_all
from promptdiff.display import print_table

load_dotenv()

__version__ = "0.1.0"


def compare(
    prompts: dict | list,
    inputs: list,
    model: str = "gpt-4o-mini",
    show_outputs: bool = False,
    use_async: bool = False,
):
    """
    Compare multiple LLM prompts side by side.

    Args:
        prompts: Either a list of prompt strings, or a dict of {label: prompt_string}.
                 Minimum 2 prompts required. If a list is passed, default labels
                 "Prompt 1", "Prompt 2", etc. are assigned automatically.
        inputs:  List of user input strings to test each prompt against.
                 Minimum 1 input required. Use real questions from your actual users
                 for the most meaningful results.
        model:   LiteLLM model string. Default is "gpt-4o-mini".
                 Examples:
                   "gpt-4o-mini"                   (OpenAI)
                   "claude-haiku-4-5"               (Anthropic)
                   "gemini/gemini-2.0-flash"        (Google)
                   "groq/llama-3.3-70b-versatile"   (Groq - free)
                   "ollama/llama3"                  (Ollama - local)
                 Full list: https://models.litellm.ai
        show_outputs: If True, print raw LLM outputs below the table. Default False.
        use_async: If True, run API calls concurrently for faster execution.
                   Useful when running many prompt+input combinations.
                   Default False.

    Raises:
        ValueError: If fewer than 2 prompts are provided.
        ValueError: If no inputs are provided.
        ValueError: If API key is missing or model name is invalid.

    Example:
        >>> from promptdiff import compare
        >>> compare(
        ...     prompts={
        ...         "original": "You are a helpful assistant.",
        ...         "concise":  "You are a concise assistant.",
        ...     },
        ...     inputs=["Explain what a database is."],
        ...     model="groq/llama-3.3-70b-versatile"
        ... )
    """

    # --- Input validation with clear error messages ---

    if isinstance(prompts, list):
        if len(prompts) < 2:
            raise ValueError(
                "At least 2 prompts are required.\n"
                "You passed a list with only 1 prompt. "
                "Add another prompt to compare against."
            )
        prompts = {f"Prompt {i+1}": p for i, p in enumerate(prompts)}

    if isinstance(prompts, dict):
        if len(prompts) < 2:
            raise ValueError(
                "At least 2 prompts are required.\n"
                "You passed a dict with only 1 key. "
                "Add another key:value pair."
            )
    else:
        raise TypeError(
            f"prompts must be a dict or list, got {type(prompts).__name__}.\n"
            f'Example: prompts={{"a": "prompt 1", "b": "prompt 2"}}'
        )

    if not inputs or len(inputs) == 0:
        raise ValueError(
            "At least 1 input is required.\n"
            "Add test questions that represent real user queries."
        )

    if not isinstance(inputs, list):
        raise TypeError(
            f"inputs must be a list of strings, got {type(inputs).__name__}.\n"
            f'Example: inputs=["What is recursion?", "Explain databases."]'
        )

    if not model or not isinstance(model, str):
        raise ValueError(
            "model must be a non-empty string.\n"
            'Example: model="gpt-4o-mini" or '
            'model="groq/llama-3.3-70b-versatile"'
        )

    # --- Run all combinations ---
    total = len(prompts) * len(inputs)
    print(
        f"\n  Running {len(prompts)} prompts x {len(inputs)} inputs "
        f"= {total} calls...\n"
    )

    all_results = run_all(prompts, inputs, model, use_async=use_async)

    # --- Print table ---
    print_table(prompts, all_results)

    # --- Optionally print raw outputs ---
    if show_outputs:
        _print_outputs(prompts, inputs, all_results)


def _print_outputs(prompts: dict, inputs: list, all_results: dict):
    """Print raw outputs grouped by input for side-by-side reading."""
    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    for i, user_input in enumerate(inputs):
        console.print(
            f"\n[bold cyan]--- Input: \"{user_input}\" ---[/bold cyan]"
        )
        for label in prompts:
            result = all_results[label][i]
            text = result.get("text", "[No output]")
            console.print(
                Panel(text, title=f"[bold]{label}[/bold]", border_style="dim")
            )
