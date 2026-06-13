"""
Display module — aggregates metrics and prints the comparison table.

Uses the Rich library for beautiful terminal output.
"""

from rich.console import Console
from rich.table import Table
from rich import box
from compare_prompts.metrics import measure

console = Console()


def aggregate(results_for_label: list) -> dict:
    """
    Take a list of result dicts (one per input) for one prompt label,
    analyze each output, and return averaged/aggregated metrics.
    """
    # Filter out error results
    valid_results = [r for r in results_for_label if "error" not in r]
    if not valid_results:
        return {
            "avg_tokens": 0,
            "uses_lists_pct": 0,
            "uses_headers_pct": 0,
            "uses_code_blocks_pct": 0,
            "tone": "unknown",
            "reading_level": "unknown",
            "refusal_pct": 0,
            "avg_cost": 0.0,
            "avg_sentence_length": 0.0,
            "errors": len(results_for_label) - len(valid_results),
        }

    analyzed = [measure(r["text"]) for r in valid_results]
    n = len(analyzed)

    # Use actual completion_tokens from API response if available,
    # fall back to metric estimate
    avg_tokens = sum(
        r.get("completion_tokens", 0) or a["token_count"]
        for r, a in zip(valid_results, analyzed)
    ) // n

    uses_lists_pct = int(sum(1 for a in analyzed if a["uses_lists"]) / n * 100)
    uses_headers_pct = int(sum(1 for a in analyzed if a["uses_headers"]) / n * 100)
    uses_code_blocks_pct = int(
        sum(1 for a in analyzed if a["uses_code_blocks"]) / n * 100
    )
    refusal_pct = int(sum(1 for a in analyzed if a["is_refusal"]) / n * 100)

    # Most common tone
    tones = [a["tone"] for a in analyzed]
    tone = max(set(tones), key=tones.count)

    # Most common reading level
    levels = [a["reading_level"] for a in analyzed]
    reading_level = max(set(levels), key=levels.count)

    valid_costs = [r["cost"] for r in valid_results if r.get("cost") is not None]
    avg_cost = sum(valid_costs) / len(valid_costs) if valid_costs else None

    avg_sentence_length = round(
        sum(a["avg_sentence_length"] for a in analyzed) / n, 1
    )

    return {
        "avg_tokens": avg_tokens,
        "uses_lists_pct": uses_lists_pct,
        "uses_headers_pct": uses_headers_pct,
        "uses_code_blocks_pct": uses_code_blocks_pct,
        "tone": tone,
        "reading_level": reading_level,
        "refusal_pct": refusal_pct,
        "avg_cost": avg_cost,
        "avg_sentence_length": avg_sentence_length,
        "errors": len(results_for_label) - len(valid_results),
    }


def format_diff(value, baseline_value, unit="", is_pct=False):
    """
    Format a value with a diff indicator compared to the baseline.
    Example: 61 tokens compared to 187 baseline → "61  (-67%)"
    """
    if baseline_value is None or baseline_value == value:
        if is_pct:
            return f"{value}%"
        return f"{value}{unit}"

    if baseline_value == 0:
        diff_str = ""
    else:
        diff = ((value - baseline_value) / baseline_value) * 100
        sign = "+" if diff > 0 else ""
        diff_str = f"  ({sign}{diff:.0f}%)"

    if is_pct:
        return f"{value}%{diff_str}"
    return f"{value}{unit}{diff_str}"


def print_table(prompts: dict, all_results: dict):
    """
    Aggregate metrics for each prompt label and print the comparison table.

    Args:
        prompts: dict of {label: system_prompt_string}
        all_results: dict of {label: [list of result dicts]}
    """
    labels = list(prompts.keys())

    # Aggregate metrics for each label
    aggregated = {label: aggregate(all_results[label]) for label in labels}

    # Baseline is the first prompt (for showing diffs)
    baseline_label = labels[0]
    baseline = aggregated[baseline_label]

    # Build Rich table
    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold cyan",
        title="[bold]Prompt Comparison Results[/bold]",
        title_style="bold white",
    )

    # First column: metric names
    table.add_column("", style="dim bold", min_width=24)

    # One column per prompt label
    for label in labels:
        table.add_column(label, min_width=22)

    # Row: avg length
    table.add_row(
        "avg length (tokens)",
        *[
            format_diff(
                aggregated[label]["avg_tokens"],
                baseline["avg_tokens"] if label != baseline_label else None
            )
            for label in labels
        ]
    )

    # Row: tone
    table.add_row("tone", *[aggregated[label]["tone"] for label in labels])

    # Row: uses lists
    table.add_row(
        "uses lists",
        *[
            format_diff(
                aggregated[label]["uses_lists_pct"],
                baseline["uses_lists_pct"] if label != baseline_label else None,
                is_pct=True
            )
            for label in labels
        ]
    )

    # Row: uses headers
    table.add_row(
        "uses headers",
        *[
            format_diff(
                aggregated[label]["uses_headers_pct"],
                baseline["uses_headers_pct"] if label != baseline_label else None,
                is_pct=True
            )
            for label in labels
        ]
    )

    # Row: uses code blocks
    table.add_row(
        "uses code blocks",
        *[
            format_diff(
                aggregated[label]["uses_code_blocks_pct"],
                baseline["uses_code_blocks_pct"]
                if label != baseline_label else None,
                is_pct=True
            )
            for label in labels
        ]
    )

    # Row: avg cost
    has_cost = any(aggregated[label]["avg_cost"] is not None for label in labels)
    if has_cost:
        table.add_row(
            "avg cost (USD)",
            *[f"${aggregated[label]['avg_cost']:.4f}" if aggregated[label]["avg_cost"] is not None else "N/A" for label in labels]
        )

    # Row: refusal rate
    table.add_row(
        "refusal rate",
        *[
            format_diff(
                aggregated[label]["refusal_pct"],
                baseline["refusal_pct"] if label != baseline_label else None,
                is_pct=True
            )
            for label in labels
        ]
    )

    # Row: reading level
    table.add_row(
        "reading level",
        *[aggregated[label]["reading_level"] for label in labels]
    )

    # Row: avg sentence length
    table.add_row(
        "avg sentence length",
        *[
            format_diff(
                aggregated[label]["avg_sentence_length"],
                baseline["avg_sentence_length"]
                if label != baseline_label else None,
                unit=" words"
            )
            for label in labels
        ]
    )

    # Row: errors (only show if any occurred)
    if any(aggregated[label]["errors"] > 0 for label in labels):
        table.add_row(
            "errors",
            *[
                f"[red]{aggregated[label]['errors']}[/red]"
                if aggregated[label]["errors"] > 0
                else "0"
                for label in labels
            ]
        )

    console.print()
    console.print(table)
    console.print()
