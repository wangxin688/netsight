"""this file defined the common algorithm for data processing
"""
from typing import Any, List, Mapping


def list_to_tree(data: List[Mapping[str, str | int]]) -> Mapping[str, Any]:
    """Adjacency list to tree representation for frontend data processing"""
    output = {}
    for element in data:
        output[element["id"]] = element
    output_tree = []
    for element in data:
        element.update({"value": element["id"], "label": element["name"]})
        if element["parent_id"] is None:
            output_tree.append(element)
        else:
            parent = output[element["parent_id"]]
            if "children" not in parent:
                parent["children"] = []
            parent["children"].append(element)
    return output_tree
