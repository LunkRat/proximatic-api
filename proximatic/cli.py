import typer
import pprint
from typing import Optional
from tabulate import tabulate
from proximatic import Proximatic
from .utils import tabulate_resources as tabulate_resources

app = typer.Typer()

proximatic = Proximatic()

pp = pprint.PrettyPrinter(indent=4)

@app.callback()
def callback():
    """
    --------------\n
    Welcome to Proximatic CLI!\n
    Interactive command-line interface for Proximatic.\n
    --------------\n
    """

@app.command()
def config_show(path: str = '/data/traefik/conf/'):
    config = proximatic.system
    typer.echo(pp.pprint(config.domains[0].routers[0].dict()))

@app.command()
def domain_list(id: str = None):
    """Returns a list of configured domains."""
    response = proximatic.domain_list(id)
    if response.data:
        table = tabulate_resources(response)
        typer.echo(table)
    else:
        typer.echo(response.error)

@app.command()
def domain_save():
    proximatic.domain_save()