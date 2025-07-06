from collections import deque
from copy import deepcopy


def _tokenize_path(path: str):
    return path.strip("/").split("/") if path != "/" else [None]


def _find_or_create_node(target: dict, path: str) -> tuple[dict, str]:
    *tokens, child = _tokenize_path(path)
    selector = deque(tokens)
    current_node = target
    while len(selector) > 0:
        next_key = selector.popleft()

        if next_key not in current_node:
            current_node[next_key] = {}

        # if len(selector) == 0:
        #     return current_node[next_key]
        # else:
        current_node = current_node[next_key]

    if child is not None and child not in current_node:
        current_node[child] = {}

    return (current_node, child)


def patch_dict(target: dict, path: str, patch: dict) -> dict:
    new_dict = deepcopy(target)
    parent, child = _find_or_create_node(new_dict, path)

    if child is None:
        parent.update(patch)
    else:
        parent[child].update(patch)

    return new_dict


def put_dict(target: dict, path: str, put: dict) -> dict:
    new_dict = deepcopy(target)
    parent, child = _find_or_create_node(new_dict, path)

    if child is None:
        return put
    parent[child] = put

    return new_dict


def delete_dict(target: dict, path: str, value: None = None) -> dict:
    new_dict = deepcopy(target)
    parent, child = _find_or_create_node(new_dict, path)

    if child is None:
        raise ValueError("Cannot delete root of dict")
    del parent[child]

    return new_dict
