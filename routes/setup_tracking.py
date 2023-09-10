import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
import sys
from textwrap import dedent
import os
import git
import re
import subprocess


from lib.git.commit_tracing import create_commit_trace, convert_to_digraph


@click.command()
@click.option("-h","--help","show_help",is_flag=True)
@click.option("--cwd","cwd", default=None)
def setup_tracking(show_help,cwd):
    """
    Command: setup-tracking

    Sets up a local branch to track any remote branch that you aren't already tracking.

    Usage: 
    -h --help - show this help message and exit.
    """

    if show_help:
        click.echo(dedent(setup_tracking.__doc__))
        sys.exit(0)

    if os.path.normpath(os.path.realpath(cwd)) == os.path.normpath(os.path.realpath(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))):
        sys.stderr.write(f"Could not open repository in \"{os.getcwd()}\": {e}\n")
        sys.exit(1)

    os.chdir(cwd)

    stdout, stderr = subprocess.Popen(["git","checkout","master"]).communicate()

    stdout, stderr = subprocess.Popen(["git", "branch", "-l"], stdout=subprocess.PIPE).communicate()

    lines = list(map(lambda x: x.strip(" ").strip("\r").strip("\t").strip("\n"),stdout.decode("utf-8").replace("\r\n", "\n").strip("\n").split("\n")))

    existing_local_branches = lines

    stdout, stderr = subprocess.Popen(["git", "branch", "-r"], stdout=subprocess.PIPE).communicate()

    lines = list(map(lambda x: x.strip(" ").strip("\r").strip("\t").strip("\n"),stdout.decode("utf-8").replace("\r\n", "\n").strip("\n").split("\n")))

    for i, line in enumerate(lines):
        print(f"Line {i}: {line}")
    for line in lines:
        if "master" in line.lower():
            print("Already tracking master")
            continue
        print("Tracking to " + line)
        rem = line
        local = rem[len("origin/"):]
        if local in existing_local_branches:
            print("Already tracking " + local)
            continue
        print(f"Tracking remote {rem} to local {local}")
        stdout, stderr = subprocess.Popen(["git", "checkout", "-b", local, rem], stdout=subprocess.PIPE).communicate()
        print(stdout.decode("utf-8").strip("\n"))

    stdout, stderr = subprocess.Popen(["git","checkout","master"]).communicate()

if __name__ == '__main__':
    setup_tracking()

