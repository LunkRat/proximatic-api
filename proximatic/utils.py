from tabulate import tabulate

def item_table(item: dict) -> str:
    headers = list(item.keys())
    tabular = list(item.values())
    table = tabulate([tabular], headers=headers)
    return table