import re

import git
from termcolor import colored

def retrieve_file_bytes_from_hash(repo: git.Repo, commit_hash: str, filepath: str) -> bytes | None:
    
    
    filepath = filepath.replace("\\", "/")


    filepath = re.sub(r"\/+", "/", filepath)

    if filepath.startswith("/"):
        print(colored(
            "Warning: Filepath '{filepath}' starts with a slash, but this slash will be stripped and the file will be relative to the repo root"
                      , "yellow"))
    if filepath.endswith("/"):
        print(colored(
            "Warning: Filepath '{filepath}' has unnecessary trailing slash"
        ))

    filepath = re.sub(r"^\/+", "", filepath)
    filepath = re.sub(r"\/+$", "", filepath)

    segments = filepath.split("/")

    for segment in segments:
        if segment == "." or segment == "..":
            raise ValueError("Relative paths with '.' and '..' are not allowed") 

    if commit_hash not in repo.tags and not repo.commit(commit_hash):
        raise ValueError(f"Commit '{commit_hash}' does not exist in the repository.")
    
    commit = repo.commit(commit_hash)
    
    tree = commit.tree

    try: 
        item = tree / filepath
    except KeyError as e:
        raise FileNotFoundError(
            colored(f"File '{filepath}' does not exist in the commit '{commit_hash}'.", "red")
            ) from e

    if item.type == "tree":
        raise IsADirectoryError(colored(
            f"File '{filepath}' is a directory in the commit '{commit_hash}'.", "red"
        ))
    
    return filepath, item.data_stream.read()