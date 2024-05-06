from lib.gitrun import gitrun

# git for-each-ref --format='%(refname:short)' refs/heads refs/remotes

def is_archived(name,is_remote):
    if is_remote:
        name="/".join(name.split("/")[1:])
    return name.lower().startswith("archive.")


def parse_branch_list_text(text,archived,is_remote):
    lines = text.split("\n")
    lines = [
        line.strip("\"'") for line in lines if not line.strip("\"'") .endswith("HEAD")
    ]
    lines = list(filter(lambda line: (not archived and not is_archived(line,is_remote)) or
                        (archived and is_archived(line,is_remote)),lines))
    return lines

def get_branch_list(where,archived):
    local_branches = parse_branch_list_text(gitrun([
        "for-each-ref",
        "--format='%(refname:short)'",
        "refs/heads",
    ]),archived,False)
    remote_branches = parse_branch_list_text(gitrun([
        "for-each-ref",
        "--format='%(refname:short)'",
        "refs/remotes",
    ]),archived,True)
    remote_branches =list(map(lambda x:f"remotes/{x}",remote_branches))
    branches = []
    if where == "both" or where == "local":
        branches.extend(local_branches)
    if where == "both" or where == "remote":
        branches.extend(remote_branches)
    return branches