"""this file defined the common algorithm for data processing
"""
from typing import Any, Dict, List


def list_to_tree(data: List[Dict[str, str | int]]) -> List[Dict[str, Any]]:
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
