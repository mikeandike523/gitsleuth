import re
import json
import os
import shutil
from functools import reduce
import textwrap

import click
from tabulate import tabulate
from natsort import natsorted

from lib.branch_attrs import get_branch_attrs

def wrap_text(text, width):
    return '\n'.join(textwrap.wrap(text, width))

def get_longest_width(strings):
    if len(strings) == 0:
        return 0
    return len(reduce(lambda a,b:a if len(a) > len(b) else b, strings))

def get_column_sizes(names,numcols,tolerance=0.1):
    longest_name_len=get_longest_width(names)
    ncols,_ =shutil.get_terminal_size()
    ncols = int((1.0-tolerance)*ncols)
    remaining=ncols-longest_name_len
    portion=int(remaining/numcols)
    return portion

def format_row(names,row):
    numcols =len(row)-1
    portion =get_column_sizes(names, numcols)
    for i in range(1,len(row)):
        row[i]=wrap_text(row[i],portion)






@click.command("branch-attrs")
@click.option("--format",type=click.Choice([
    "table",
    "json"
]), required=False,default="table")
def branch_attrs(format="table"):
    if format == "json":
        print(json.dumps(get_branch_attrs(), indent=2))
    else:
        data=get_branch_attrs()
        attrnames = set()
        for v in data.values():
            for kk in v.keys():
                attrnames.add(kk)
        for v in data.values():
            for attrname in attrnames:
                if attrname not in v:
                    v[attrname]=""
        for k, v in data.items():
            v["name"]=k
        if len(attrnames) == 0:
            print("No branch attributes")
            exit()
        attrnames=natsorted(list(attrnames))
        rows = []
        for v in data.values():
            rows.append([v["name"],]+[
                v[attrname] for attrname in attrnames
            ])
        names = [v[0] for v in rows]
        for row in rows:
            format_row(names,row)
        longest_name_len = get_longest_width(names)
        portion = get_column_sizes(names,len(attrnames))
        headers = ["name".ljust(longest_name_len)]+list(map(lambda n:n.ljust(portion),attrnames))
        print(tabulate(rows, headers=headers,tablefmt="grid"))
