#!/usr/bin/env python3
import sys
from pathlib import Path

try:
    from src.lib import (
        SKILLS_SRC_DIR,
        discover_skills,
        install_skill,
        skill_installed,
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.lib import (
        SKILLS_SRC_DIR,
        discover_skills,
        install_skill,
        skill_installed,
    )

from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table
from rich.prompt import Prompt


def main() -> None:
    skills = discover_skills()
    if not skills:
        console = Console()
        console.print(f"No skills found under {SKILLS_SRC_DIR}. Add .md files with name/description frontmatter to install.")
        return

    console = Console()
    table = Table(
        title="Skills to install",
        show_header=True,
        header_style="bold",
        show_lines=True,
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Mcp Tools")

    for i, (stem, name, desc, mcp) in enumerate(skills, 1):
        table.add_row(str(i), name, desc, mcp or "—")
    table.add_row("all", "[bold]Install all[/bold]", "Install every skill listed above", "—", style="dim")

    prompt_msg = (
        "Enter number(s) to install (e.g. 1 3 5), [bold]all[/bold], or [bold]q[/bold] to quit"
    )

    while True:
        console.print(table)
        console.print()

        choice = Prompt.ask(prompt_msg, default="all").strip()

        if choice.lower() == "q":
            console.print("Exiting.")
            return

        if choice.lower() == "all":
            to_install = [s[0] for s in skills]
        else:
            to_install = []
            for word in choice.split():
                if word.isdigit():
                    idx = int(word) - 1
                    if 0 <= idx < len(skills):
                        to_install.append(skills[idx][0])

        if not to_install:
            console.print("[yellow]Invalid input. Please try again.[/yellow]")
            console.print()
            continue

        stem_to_name = {s[0]: s[1] for s in skills}  # (stem, name, desc, mcp)
        for stem in to_install:
            if skill_installed(stem):
                name = stem_to_name.get(stem, stem)
                if not Confirm.ask(
                    f"Skill [bold]{name}[/bold] is already installed. Overwrite?",
                    default=False,
                ):
                    console.print(f"Skipped {name}.")
                    continue
            try:
                install_skill(stem)
            except FileNotFoundError as e:
                console.print(f"[red]error:[/red] {e}")
                sys.exit(1)

        console.print("[green]Done.[/green]")
        console.print()


if __name__ == "__main__":
    main()
