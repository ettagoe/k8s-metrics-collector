import re


def replace_illegal_chars(value):
    if type(value) == str:
        return _replace_illegal_chars(value)
    elif type(value) == dict:
        return _replace_dict_illegal_chars(value)
    elif type(value) == list:
        return _replace_list_illegal_chars(value)
    else:
        return value


def _replace_illegal_chars(value: str) -> str:
    value = value.strip().replace(".", "_")
    return re.sub('\s+', '_', value)


def _replace_list_illegal_chars(list_: list) -> list:
    return [replace_illegal_chars(v) for v in list_]


def _replace_dict_illegal_chars(dict_: dict) -> dict:
    return {replace_illegal_chars(k): replace_illegal_chars(v) for k, v in dict_.items()}
