import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


import click
import os
import sys
import subprocess
from types import SimpleNamespace
from termcolor import colored


def from_root(*segments):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *segments)

# Manually define a dictionary of valid routes
ROUTES = {

    "trace-local": SimpleNamespace(
        file="trace_local.py",
        short_description="Visualize the commit history of the local repository",
    ),
    "setup-tracking": SimpleNamespace(
        file="setup_tracking.py",
        short_description="Setup a local branch to track every remote branch in the repository",
    ),
    "investigate-files": SimpleNamespace(
        file="investigate_files.py",
        short_description="investigate one or more files from an old commit"
    ),
    "source-tree": SimpleNamespace(
        file="source_tree.py",
        short_description="Visualize the source tree of the repository"
    ),
    "recover-file": SimpleNamespace(
        file="recover_file.py",
        short_description="Recover a file from an old commit"
    ),
}

@click.command(context_settings=dict(
        ignore_unknown_options=True,
))
@click.argument("init_cwd", required=True)
@click.argument('command', required=False, type=click.Choice(list(ROUTES.keys())))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.option('-h', '--help', 'show_help', is_flag=True, help='Show this message and exit')
def cli(init_cwd,command, args, show_help):
    """A CLI tool to execute available routes."""

    CWD = init_cwd

    os.chdir(init_cwd)

    if show_help:
        # No command provided, display the list of all commands
        if not command:
            max_cmd_length = max([len(cmd) for cmd in ROUTES.keys()])
            click.echo("Available commands:")
            for cmd, details in ROUTES.items():
                click.echo(f"  {cmd.ljust(max_cmd_length)} - {details.short_description}")
            sys.exit(0)
        else:
            args = args + ("-h","--help", )

    if not command:
        click.echo("Please provide a valid command. Use -h for a list of commands.")
        sys.exit(1)


    args = args + ("--cwd", CWD)
    
    route = ROUTES[command]

    # Use subprocess to run the desired route
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(from_root("routes"), route.file), *args],
            capture_output=True,
            text=True
        )

        # Check if there was an error and print stderr
        if result.returncode != 0:
            click.echo(colored(f"Error: {result.stderr}", 'red'), err=True)
            sys.exit(result.returncode)
        else:
            sys.stdout.write(result.stdout)

    except Exception as e:
        click.echo(colored(f"Error: {e}", 'red'), err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()