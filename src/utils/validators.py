from typing import List, TypeVar, Union

InputItemDataT = TypeVar("InputItemDataT", int, str, float)
ItemsDataT = TypeVar("ItemsDataT", bound=List[Union[str, float, int]])


def items_to_list(
    input: InputItemDataT | ItemsDataT,
) -> ItemsDataT:
    if isinstance(input, (int, str, float)):
        return [
            input,
        ]
    return input
