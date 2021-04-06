import typer
import pprint
from proximatic import Proximatic, __version__
from .utils import tabulate_resources as tabulate_resources

app = typer.Typer()

proximatic = Proximatic()

pp = pprint.PrettyPrinter(indent=4)


@app.callback()
def callback():
    """
    --------------\n
    Proximatic CLI\n
    Interactive command-line interface to Proximatic.\n
    --------------\n
    """


@app.command()
def config_show():
    typer.echo(pp.pprint(proximatic.system.dict()))


@app.command()
def provider_list(id: str = None):
    """Returns a list of configured providers."""
    response = proximatic.provider_list(id)
    if response.data:
        table = tabulate_resources(response)
        typer.echo(table)
    else:
        typer.echo(response.error)


@app.command()
def provider_create(id: str, server: str):
    response = proximatic.provider_create(id=id, server=server)
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
def provider_delete(id: str):
    response = proximatic.provider_delete(id)
    typer.echo(pp.pprint(response.dict()))
