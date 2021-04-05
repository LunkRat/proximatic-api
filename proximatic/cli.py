import typer
import pprint
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
    Interactive command-line interface to Proximatic.\n
    --------------\n
    """


@app.command()
def config_show(path: str = "/data/traefik/conf/"):
    config = proximatic.system
    typer.echo(pp.pprint(config.dict()))


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
def domain_export(id: str):
    fetch = proximatic.domain_fetch(id)
    if len(fetch) != 1:
        typer.echo("No domins to export.")
        typer.Abort()
    else:
        domain = fetch[0]
        response = proximatic.domain_export(domain)
        table = tabulate_resources(response)
        typer.echo(f"Domain {id} successfully saved:")
        typer.echo(table)


@app.command()
def domain_create(id: str, server: str):
    response = proximatic.domain_create(id=id, server=server)
    if response.data:
        typer.echo(
            f"\nSuccessfully created {response.data[0].type} {response.data[0].id}.\n"
        )
        table = tabulate_resources(response)
        typer.echo(table)
    else:
        if response.error:
            typer.echo(pp.pprint(response.error[0].dict()))


@app.command()
def domain_delete(id: str):
    response = proximatic.domain_delete(id)
    typer.echo(pp.pprint(response.dict()))
