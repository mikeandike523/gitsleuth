import os
from textwrap import dedent

from git import Repo

class NotARepoException(Exception):
    pass

def open_repo(path: str) -> Repo:
    if not os.path.isabs(path):
        raise Exception(dedent(f"""
                        Path "{path}" is not an absolute path.
                        This is to protect against accidental effects due to the current working directory.
                        Please manually resolve relatives paths
                        """.strip(0))) 
    if not os.path.exists(path):
        raise NotARepoException(f"Directory \"{path}\" does not exist")
    if not os.path.isdir(path):
        raise NotARepoException(f"Path \"{path}\" is not a directory")
    items  = os.listdir(path)
    if ".git" not in items:
        raise NotARepoException(f"No \".git\" directory found in \"{path}\"")
    try:
        return Repo(path)
    except Exception as e:
        raise NotARepoException(f"Could not open repository in \"{path}\"") from e