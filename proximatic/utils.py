import yaml
from tabulate import tabulate
from .models import ResponseModel

def tabulate_resources(response: ResponseModel) -> str:
    """
    Takes a ResponseModel and returns all of its resources as a string 
    formatted as a GitHub-flavored markdown table.
    """
    if response.data:
        # headers = ["type", "id"] + list(response.data[0].attributes.dict().keys())
        headers = ["type", "id", "endpoint", "server"]
        tabular = []
        for resource in response.data:
            # tabular.append([resource.type, resource.id] + list(resource.attributes.dict().values()))
            tabular.append([resource.type, resource.id, resource.attributes.endpoint, resource.attributes.server])
        table = tabulate(tabular, headers=headers, tablefmt="github")
        return table