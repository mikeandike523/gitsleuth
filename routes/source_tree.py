import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from textwrap import dedent
from typing import Optional

import click
from termcolor import colored
import colorama

from lib.git.ignores import CollectMode, PathReturnMode, RepoIgnoreChecker
from lib.md import escape_for_markdown
from lib.tree import filepaths_to_tree


def list_source_files(repo_root: str) -> [str]:
    repo_ignore_checker = RepoIgnoreChecker(repo_root)

    files = repo_ignore_checker.collect_included_files()

    files = list(filter(lambda file: len(file.strip()) > 0, files))

    return files

@click.command(name="source-tree")
@click.argument("subcommand", type=click.STRING, required=True)
@click.option("--checklist", is_flag=True, default=False)
def source_tree(
    subcommand: str,
    checklist: bool
):
    cwd=os.getcwd()

    if subcommand == "list":
        files=list_source_files(cwd)
        for i,file in enumerate(files):
            if checklist:
                sys.stdout.write(f"- [ ] {escape_for_markdown(file)}")
            else:
                sys.stdout.write(file)
            if i < len(files) - 1:
                sys.stdout.write("\n")
    elif subcommand == "tree":
        files=list_source_files(cwd)
        print(str(filepaths_to_tree(files)))
    else:
        click.echo(f"Unknown subcommand: {subcommand}")