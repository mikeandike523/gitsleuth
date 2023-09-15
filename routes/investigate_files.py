import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
import sys
from textwrap import dedent
import os
import git
import shutil
from termcolor import colored

from lib.git.retrieve_file import retrieve_file_bytes_from_hash

@click.command()
@click.option("-h","--help","show_help",is_flag=True)
@click.option("--cwd","cwd", default=None)
@click.option("--hash", required=True, type=click.STRING)
@click.argument("filenames",nargs=-1,type=click.STRING)
def investigate_files(show_help: bool,cwd: str, hash: str, filenames: [str]):
    """
    Command: investigate-files

    Given a list of files to investigate and a particular hash, write these files to a directory:

    <cwd>/.gitsleuth/investigation

    Note: old investigation files are cleared when a new investigation is run

    Usage: 
    -h --help - show this help message and exit.

    `gitsleuth investigate-files --hash=<hash> file1 folder2/file3 "file 4" ...`

    """

    if show_help:
        click.echo(dedent(investigate_files.__doc__))
        sys.exit(0)

    if os.path.normpath(os.path.realpath(cwd)) == os.path.normpath(os.path.realpath(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))):
        sys.stderr.write(f"Could not open repository in \"{os.getcwd()}\": {e}\n")
        sys.exit(1)

    os.chdir(cwd)

    outdir = os.path.normpath(os.path.join(cwd, '.gitsleuth','investigation'))

    if os.path.isdir(outdir):
        shutil.rmtree(outdir)

    if not os.path.isdir(outdir):
        os.makedirs(outdir, exist_ok=True)
   
    repo = None

    try:
        repo = git.Repo()
    except Exception as e:
        sys.stderr.write(f"Could not open repository in \"{os.getcwd()}\": {e}\n")
        sys.exit(1)

    for file in filenames:
        print(colored(f"Investigating {file}...", "yellow"))

        try:
            sanitized_path, file_bytes = retrieve_file_bytes_from_hash(repo, hash, file)

            norm_sanitized_path = os.path.normpath(sanitized_path)

            if os.path.sep in norm_sanitized_path:
                parent = os.path.dirname(norm_sanitized_path)
                folder = os.path.join(outdir, parent)
                os.makedirs(folder, exist_ok=True)
            out_file = os.path.join(outdir, norm_sanitized_path)
            with open(out_file, "wb") as f:
                f.write(file_bytes)

            print(colored(f"Wrote {file} to {out_file}...", "green"))     

        except FileNotFoundError as e:
            print(colored(f"Could not find {file} in repository, skipping...", "red"))            


    

if __name__ == '__main__':
    investigate_files()