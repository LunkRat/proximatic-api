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
def show():
    response = proximatic.show()
    if response.data:
        table = tabulate_resources(response)
        typer.echo(table)
    else:
        typer.echo(response.error)


# @app.command()
# def create(id: str, server: str):
#     response = proximatic.create(id=id, server=server)
#     if response.data:
#         typer.echo(
#             f"\nSuccessfully created {response.data[0].type} {response.data[0].id}.\n"
#         )
#         table = tabulate_resources(response)
#         typer.echo(table)
#     else:
#         if response.error:
#             typer.echo(pp.pprint(response.error[0].dict()))


@app.command()
def export_yml():
    proximatic.export_yml()
