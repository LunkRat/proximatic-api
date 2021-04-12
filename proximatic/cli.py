import typer
import pprint
from proximatic import Proximatic, __version__
from .utils import tabulate_resources

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
def view():
    response = proximatic.view()
    if response.data:
        table = tabulate_resources(response)
        typer.echo(table)
    else:
        typer.echo(response.error)


@app.command()
def add(resource_id: str, service_url: str):
    response = proximatic.add(resource_id=resource_id, service_url=service_url)
    if response.data:
        typer.echo(
            f"\nSuccessfully created {response.data[0].type} {response.data[0].resource_id}.\n"
        )
        table = tabulate_resources(response)
        typer.echo(table)
    else:
        if response.error:
            typer.echo(pp.pprint(response.error[0].dict()))


@app.command()
def export_yml():
    proximatic.export_yml()
