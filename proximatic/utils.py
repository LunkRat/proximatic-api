from tabulate import tabulate
from .models import ResponseModel


def tabulate_resources(response: ResponseModel) -> str:
    """
    Takes a ResponseModel and returns all of its resources as a string
    formatted as a GitHub-flavored markdown table.
    """
    if response.data:
        headers = ["type", "id", "router_rule", "middlewares", "service_url"]
        tabular = []
        for resource in response.data:
            tabular.append(
                [
                    resource.type,
                    resource.resource_id,
                    resource.attributes.router_rule,
                    " ,".join(resource.attributes.middlewares),
                    resource.attributes.service_url,
                ]
            )
        table = tabulate(tabular, headers=headers, tablefmt="github")
        return table
