import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
import sys
import tempfile
import subprocess
import traceback
from textwrap import dedent
from typing import Callable, List
from shutil import which


import click
import git
from termcolor import colored

def print_error(text,end="\n"):
    sys.stderr.write(colored(text,"red")+end)

def main(branch_name: str, command: str):

    if not branch_name:
        raise ValueError("A branch name must be provided")
    
    if not command:
        raise ValueError("A command must be provided")
    
    # Declare Useful Variables

    CWD = os.getcwd()

    # Exhaustive Checks

    if not os.path.isdir(os.path.join(CWD,".git")):
        raise ValueError(f"Current working directory is not a valid git repository")
    
    repo = None

    try:
        repo = git.Repo(CWD)
    except:
        raise ValueError(f"Current working directory is not a valid git repository")
    
    if branch_name not in [str(branch) for branch in repo.heads]:
        raise ValueError(f"Branch {branch_name} does not exist (locally) in the repo in the current working directory.")
    
    command = [which("bash"), "-c", command]

    with tempfile.TemporaryDirectory() as temp_dir:
        wt_name = os.path.join(temp_dir,"wt")
        subprocess.run(["git","worktree","add",wt_name,branch_name],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        proc=subprocess.Popen(command,cwd=wt_name,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout,stderr = proc.communicate()
        if stdout is not None:
            print(stdout.decode("utf-8"))
        if stderr is not None:
            print(colored(stderr.decode("utf-8"),"red"))

    subprocess.run(["git","worktree","prune"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)

@click.command(name="run-in-branch")
@click.argument("branch_name", required=False,type=click.STRING)
@click.argument("command", required=False,type=click.STRING)
def run_in_branch(branch_name: str, command: str):
    """
    Command: run-in-branch

    Run a bash shell comamnd in a particular branch in a completely safe manner, by taking advantage of git worktrees
    
    A worktree is silently created in a temporary directory and the commands and the shell script is run within it

    ATTENTION!
    1.  Present argument <COMMAND> as quoted text for safety.
        You will be subject to the quotation rules of both bash and the shell you are calling "gitsleuth" from.
    2.  "git worktree prune" will be called after running the command.
    
    Usage:
    gitsleuth run-in-branch <BRANCH NAME> <COMMAND>
    """

    try:
        main(branch_name,command)
    except Exception as e:
        print_error(f"Error running script file within branch {branch_name}:")
        print_error(str(e))
        print_error("Traceback:")
        print_error(traceback.format_exc())
        sys.exit(1)

