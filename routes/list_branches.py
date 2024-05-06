import click

from lib.list_branches import get_branch_list

@click.command("list-branches")
@click.argument("where",type=click.Choice([
    "local",
    "remote",
    "both"
]),required=False,default="both")
@click.option("--archived",is_flag=True,required=False,default=False)
def list_branches(where,archived):
    branches = get_branch_list(where,archived)
    print("\n".join(branches))