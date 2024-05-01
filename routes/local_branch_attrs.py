import re
import json
import click
from git import Repo

@click.command()
def local_branch_attrs():
    repo = Repo('.')
    branch_attrs = {}

    # Iterate over local branches
    for branch in repo.branches:
        commits = list(repo.iter_commits(branch.name, reverse=True))
        attrs = {}

        # Regex to detect the pattern '@attr[attr_name]=value'
        pattern = re.compile(r'@attr\[(\w+)\]=(.*)')

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

if __name__ == '__main__':
    local_branch_attrs()