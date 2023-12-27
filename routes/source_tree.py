import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from textwrap import dedent
from typing import Optional

import click

from lib.git.ignores import CollectMode, RepoIgnoreChecker, PathReturnMode

def list_source_files_feature(repo_root: str, collect_mode: CollectMode) -> [str]:
    repo_ignore_checker = RepoIgnoreChecker(repo_root)

    # Will list relative paths, the cli user really doesn't want absolute paths, since it just clutters the terminal

    files = repo_ignore_checker.collect_excluded_files(PathReturnMode.RELATIVE) if collect_mode == CollectMode.EXCLUDED else repo_ignore_checker.collect_included_files()

    files = list(filter(lambda file: len(file.strip()) > 0, files))

    message = ""

    for i, file in enumerate(files):
        message += f"{file}"
        if i < len(files) - 1:
            message += "\n" 

    return message

@click.command()
@click.option("-h","--help","show_help",is_flag=True)
@click.option("--cwd","cwd", default=None)
@click.argument("subcommand", type=click.STRING, required=True)
@click.option("--checklist", is_flag=True, default=False)
def source_tree(
    show_help: bool,
    cwd: Optional[str],
    subcommand: str,
    checklist: bool
):
    
    if not cwd:
        raise Exception("No cwd specified. This is not expected as the top-level cli manager should have supplied it.")
    
    if not os.path.isabs(cwd):
        raise Exception(f"cwd was not an absolute path. This is not expected as the top-level cli manager should have supplied it.")

    if show_help:
        click.echo(dedent(source_tree.__doc__))
        sys.exit(0)

    if subcommand == "list-included":
        message = list_source_files_feature(cwd, CollectMode.INCLUDED)
        if not checklist:
            sys.stdout.write(message)
        else:
            lines = message.splitlines()
            for i,line in enumerate(lines):
                sys.stdout.write(f"- [ ] {line}")
                if i < len(lines) - 1:
                    sys.stdout.write("\n")
    else:
        click.echo(f"Unknown subcommand: {subcommand}")

if __name__ == '__main__':
    source_tree()