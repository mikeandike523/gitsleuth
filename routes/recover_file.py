import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
import sys
from textwrap import dedent
import os
import re
import traceback
from typing import Callable, List

import git

class BranchBoundaryError(Exception):
    def __init__(self, from_branch, to_branch):
        self.from_branch = from_branch
        self.to_branch = to_branch

    def __str__(self):
        return f"BranchBoundaryError: Traversal denied from branch {self.from_branch} to branch {self.to_branch}"

class NoParentsError(Exception):

    def __init__(commit: git.Commit):
        super(f"Commit {commit.hexsha} has no parents. It may be the repository eroot or related to a rebase operation")

def get_branchstart_name(commit: git.Commit, repo: git.Repo) -> str:
    # Loop through the list of branches and check if starting commit hash is same as the provided commit
    # if found, return the branch name
    # if not, then the commit is not a branch start and return None
    for branch in repo.branches:
        if branch.commit == commit:
            return branch.name
    return None

class BackTraverser:

    def __init__(self, repo, starting_branch_name=None, commit=None):
        self.repo = repo
        if commit is None:
            commit = repo.head.commit
        if starting_branch_name is None:
            starting_branch_name = repo.active_branch.name
        self.commit = commit
        self.branch_name = starting_branch_name

    def get_commit(self) -> git.Commit:
        return self.commit
    
    def get_repo(self) -> git.Repo:
        return self.repo
    
    def get_branch_name(self) -> str:
        return self.branch_name

    def walk_until(self,
                   condition: Callable[["BackTraverser"], bool],
                   permit_branch_boundary_crossing=True) -> List["BackTraverser"]:
        if condition(self):
            return [self]
        satisfied: List["BackTraverser"] = []
        if not self.commit.parents or len(self.commit.parents) == 0:
            raise NoParentsError(self.commit)
        for parent in self.commit.parents:
            potential_branchstart_name = get_branchstart_name(self.commit, self.repo)
            if (potential_branchstart_name is not None
            and potential_branchstart_name!= self.branch_name
            and not permit_branch_boundary_crossing):
                raise BranchBoundaryError(self.branch_name, potential_branchstart_name)
            next_branchname = get_branchstart_name(parent, self.repo)
            if next_branchname is None:
                next_branchname = self.branch_name
            next_traverser = BackTraverser(self.repo, next_branchname, parent)
            parent_satisfied = next_traverser.walk_until(condition, permit_branch_boundary_crossing)
            satisfied.extend(parent_satisfied)
        return satisfied


@click.command()
@click.option("-h","--help","show_help",is_flag=True)
@click.option("--cwd","cwd", default=None)
@click.option("--identify", is_flag=True, default=False)
@click.option("--all-time", is_flag=True, default=False)
# `required` argument had to be false since the "gitsleuth" launcher was being tripped up in the -h/--help case
@click.argument("filename", required=False,type=click.STRING)
def recover_file(show_help: bool,cwd: str, identify: str, all_time, filename: str):
    """
    Command: recover-file

    Go backwards through the commit history of the current branch until file <filename> is found

    Optionally, show the commit hash instead of the file contents

    ATTENTION:
    <filename> is relative to the repository root
    backslash is converted to forward slash
    leading forward slashes are stripped, and the file is still relative to the repository root

    Usage: 
    -h --help   - show this help message and exit.
    --identify  - Print the branch name and commit hash instead of the file contents.
                  The output format will be "<branch name>/<commit hash>"

    --all-time  - Start with the current branch,
                  but continue searching up the history even over branch boundaries,
                  until the start of the repo history

    

    `gitsleuth recover-file <filename> <OPTIONS>`

    """

    if show_help:
        click.echo(dedent(recover_file.__doc__))
        sys.exit(0)

    # checks to make sure that not performing operations on the gitsleuth installation directory
    if os.path.normpath(os.path.realpath(cwd)) == os.path.normpath(os.path.realpath(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))):
        sys.stderr.write(f"Could not open repository in \"{os.getcwd()}\": {e}\n")
        sys.exit(1)

    os.chdir(cwd)

    if not filename:
        sys.stderr.write("No filename provided\n")
        sys.exit(1)

    # clean up the filename according to the rules mentioned in the help text

    filename = filename.replace("\\","/")
    filename = filename.lstrip("/")

    # trailing slashes are never relevant since it has no bearning on whether its a file or folder
    # no reason not to remove it
    filename = filename.rstrip("/")

    # Also, to make things easier, collapse multiple slashes into a single one
    filename = re.sub(r"\/+", "/", filename)

    repo = None

    try:
        repo = git.Repo()

    except Exception as e:
        sys.stderr.write(f"Could not open repository in \"{os.getcwd()}\": {e}\n")
        sys.exit(1)

    if not repo.head.is_valid():
        sys.stderr.write(f"The repository is empty or is not initialized\n")
        sys.exit(1)

    try:

        def condition(back_traverser: BackTraverser) -> bool:
            t_commit = back_traverser.get_commit()
            t_tree =t_commit.tree
            try:
                t_tree / filename
                return True
            except KeyError:
                return False
        
        starting_branch_name = repo.active_branch.name

        start_traverser = BackTraverser(repo, starting_branch_name, repo.head.commit)

        satisfied = start_traverser.walk_until(condition, permit_branch_boundary_crossing=all_time)

        if len(satisfied) == 0:
            if all_time:
                sys.stderr.write(f"Could not find the desired file within the entire repository history\n")
            else:
                sys.stderr.write(f"Could not find the desired file within the current branch\n")
            sys.exit(1)

        def finalize(traverser: BackTraverser):

            if identify:
                if repo.active_branch.name != traverser.get_branch_name():
                    sys.stdout.write(f"{repo.active_branch.name}/{traverser.get_commit().hexsha}\n")
                else:
                    sys.stdout.write(f"{repo.active_branch.name}/{traverser.get_commit().hexsha}\n")
            else:
                t_tree = satisfied[0].get_commit().tree
                t_blob = t_tree / filename
                # we already know it exists, and if there is some issue, it will reach the catch-all error handling
                sys.stdout.write(t_blob.data_stream.read().decode("utf-8"))
                
            sys.exit(0)

        if len(satisfied) == 1:
            finalize(satisfied[0])

        if len(satisfied) > 1:
            print(f"Found {len(satisfied)} matches")
            print(f"#\tdate\tidentity")
            for i, traverser in satisfied:
                print(f"{i+1}\t{traverser.get_commit().committed_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')}\t{traverser.get_branch_name()}/{traverser.get_commit().hexsha()}\n")
            selection = None
            while selection is None:
                try:
                    selection = int(input("Select match "))-1
                except ValueError:
                    sys.stderr.write("Please enter a number\n")
                if selection < 0 or selection >= len(satisfied):
                    sys.stderr.write("Please enter a number between 1 and {len(satisfied)}\n")

            finalize(satisfied[selection])

    except NoParentsError:
        if all_time:
            sys.stderr.write(f"Could not find the desired file within the entire repository history\n")
        else:
            sys.stderr.write(f"Could not find the desired file within the current branch\n")
        sys.exit(1)
    
    
    except BranchBoundaryError as e:
        sys.stderr.write(f"--all-time was false or not specified, and could not find the desired file within the current branch: {e}\n")
        sys.exit(1)    
    except Exception as e:
        sys.stderr.write(f"Encountered unexpected error: {e}\n")
        sys.stderr.write(f"Traceback\n")
        tb = traceback.format_exc()
        sys.stderr.write(tb)
        sys.stderr.write("\n")
        sys.exit(1)

if __name__ == '__main__':
    recover_file()