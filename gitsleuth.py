import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


import click
import os
import sys
import subprocess
from types import SimpleNamespace
from termcolor import colored

from routes.trace_local import trace_local
from routes.setup_tracking import setup_tracking
from routes.investigate_files import investigate_files
from routes.source_tree import source_tree
from routes.recover_file import recover_file
from routes.run_in_branch import run_in_branch
from routes.branch_attrs import branch_attrs
from routes.list_branches import list_branches

def from_root(*segments):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *segments)

@click.group()
def cli():
    """
    run gitsleuth [SUBCOMMAND] --help for more information about a subcommand
    """

cli.add_command(trace_local) 
cli.add_command(setup_tracking)
cli.add_command(investigate_files)
cli.add_command(source_tree)
cli.add_command(recover_file)
cli.add_command(run_in_branch)
cli.add_command(branch_attrs)
cli.add_command(list_branches)

if __name__ == '__main__':
    cli()