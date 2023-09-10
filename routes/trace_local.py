import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
import sys
from textwrap import dedent
import os
import git
import re

from lib.git.commit_tracing import create_commit_trace, convert_to_digraph


@click.command()
@click.option("-h","--help","show_help",is_flag=True)
@click.option("--cwd","cwd", default=None)
@click.option("-o","--out","out", required=False, default=None)
def trace_local(show_help,cwd,out):
    """
    Command: trace-local

    Create a trace of the commit history of the local branches
    in the repo in the current working directory.

    Uses GraphViz to save a pdf file specified using the -o/--out option.

    Usage: 
    -h --help - show this help message and exit.
    -o --out - The output file path, relative to ./.gitsleuth/reports
    """

    if show_help:
        click.echo(dedent(trace_local.__doc__))
        sys.exit(0)

    if os.path.normpath(os.path.realpath(cwd)) == os.path.normpath(os.path.realpath(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))):
        sys.stderr.write(f"Could not open repository in \"{os.getcwd()}\": {e}\n")
        sys.exit(1)

    os.chdir(cwd)

    if not os.path.isdir(os.path.join(cwd, '.gitsleuth','reports')):
        os.makedirs(os.path.join(cwd, '.gitsleuth','reports'))

    if out is None:
        out = 'trace-local.pdf'

    out = re.sub('(\\.pdf)*$','',out)

    repo = None

    try:
        repo = git.Repo()
    except Exception as e:
        sys.stderr.write(f"Could not open repository in \"{os.getcwd()}\": {e}\n")
        sys.exit(1)

    # Create the commit trace
    commit_trace = create_commit_trace(repo)

    # Convert to a Digraph
    dot = convert_to_digraph(commit_trace)

    # Saving the diagram to a PDF
    os.chdir(os.path.join(cwd, '.gitsleuth','reports'))
    dot.format = 'pdf'
    dot.render(out)
    os.chdir(cwd)

    fullout = os.path.join(cwd, '.gitsleuth','reports', out)

    print(f"Generated files:\n\t1.{fullout}\n\t2.{fullout}.pdf")

if __name__ == '__main__':
    trace_local()