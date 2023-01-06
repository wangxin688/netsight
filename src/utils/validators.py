from typing import List, overload


@overload
def items_to_list(input: int | List[int]) -> List[int]:
    ...


@overload
def items_to_list(input: str | List[str]) -> List[str]:
    ...


@overload
def items_to_list(input: float | List[float]) -> List[float]:
    ...


def items_to_list(
    input: str | float | int | List[str | float | int],
) -> List[str | float | int]:
    if isinstance(input, (int, str, float)):
        return [
            input,
        ]
    return input
