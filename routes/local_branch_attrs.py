import re
import json
import os

import click

from lib.git.repo import open_repo


@click.command("local-branch-attrs")
def local_branch_attrs():
    """
    Command: local-branch-attrs

    Outputs a JSON-formatted dictionary of up-to-date local branch attributes, as detected
    by the pattern '@attr[attr_name]=value' in commit messages.
    """
        
    repo = open_repo(os.getcwd())
    branch_attrs = {}

    # Iterate over local branches
    for branch in repo.branches:
        commits = list(repo.iter_commits(branch.name, reverse=True))
        attrs = {}

        # Regex to detect the pattern '@attr[attr_name]=value'
        pattern = re.compile(r"@attr\[(\w+)\]=(.*)")

        # Collect attributes from commit messages
        for commit in commits:
            for line in commit.message.splitlines():
                match = pattern.search(line)
                if match:
                    attr_name, value = match.groups()
                    attrs[attr_name] = value

        # Store attributes for the current branch
        branch_attrs[branch.name] = attrs

    # Output the dictionary in JSON format
    print(json.dumps(branch_attrs, indent=2))


if __name__ == "__main__":
    local_branch_attrs()
