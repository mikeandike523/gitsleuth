import re
from typing import Dict, Optional

from termcolor import colored

class TreeNode:
    value: Optional[str]
    children: Dict[str,"TreeNode"]

    def __init__(self, value=None, children=None):
        self.value = value
        self.children = children if children is not None else dict()

    def insert(self,path, value):
        if len(path) == 0:
            self.value = value
        if len(path) == 1:
            self.children[path[0]] = TreeNode(value)
        else:
            segment = path[0]
            if segment not in self.children:
                self.children[segment] = TreeNode()
            remaining = path[1:]
            self.children[segment].insert(remaining, value)

    def __str__(self):
        if len(self.children) == 0:
            return str(self.value)
        else:
            s=""
            for key in self.children:
                if len(self.children[key].children)==0:
                     s+=str(self.children[key])+"\n"
                else:
                    s+=" "*0+colored(f"{key}:\n","magenta")
                    sub=f"{str(self.children[key])}"
                    for line in sub.split("\n"):
                        s+=" "*4+f"{line}\n"
            return s.rstrip()


def filepaths_to_tree(filepaths):
    filepaths = list(map(lambda p:re.sub(r"((^\/)|(\/$))","",re.sub(r"\/+","/",re.sub(r"\\","/",p))), filepaths))
    segmented_paths = [f.split("/") for f in filepaths]
    root_node=TreeNode()
    for segmented_path in segmented_paths:
        if len(segmented_path) == 0:
            continue
        root_node.insert(segmented_path, segmented_path[-1])
    return root_node