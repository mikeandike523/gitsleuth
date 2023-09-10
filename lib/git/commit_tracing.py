import git
from graphviz import Digraph

def create_commit_trace(repo):
    """
    Create an abstract representation of the commit history.
    
    Args:
        repo (git.Repo): The Git repository.

    Returns:
        dict: A dictionary representing the commit history.
    """
    commit_trace = {}
    for branch in repo.branches:
        prev_commit = None
        for commit in repo.iter_commits(branch):
            if commit.hexsha not in commit_trace:
                commit_trace[commit.hexsha] = {
                    "date": commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    "author_name": commit.author.name,
                    "message": commit.summary,
                    "parents": [p.hexsha for p in commit.parents],
                    "branches": [branch.name],
                    "is_merge": len(commit.parents) > 1,
                }
            else:
                # If the commit already exists, add the branch to it
                commit_trace[commit.hexsha]["branches"].append(branch.name)
            prev_commit = commit
    return commit_trace

def convert_to_digraph(commit_trace):
    """
    Convert the abstract representation to a GraphViz Digraph.

    Args:
        commit_trace (dict): The abstract representation of the commit history.

    Returns:
        graphviz.Digraph: A Digraph representing the commit history.
    """
    dot = Digraph('CommitGraph', node_attr={'style': 'filled', 'color': 'lightyellow'})
    for commit_hash, commit_info in commit_trace.items():
        node_label = (
            f"{commit_hash[:7]}\n"
            f"Date: {commit_info['date']}\n"
            f"Author: {commit_info['author_name']}\n"
            f"Message: {commit_info['message']}\n"
            f"Branches: {', '.join(commit_info['branches'])}"
        )
        if commit_info["is_merge"]:
            dot.node(commit_hash, node_label, color="lightblue")
        else:
            dot.node(commit_hash, node_label)
        for parent_hash in commit_info["parents"]:
            dot.edge(commit_hash, parent_hash)
    return dot