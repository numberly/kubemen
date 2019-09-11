import difflib
import functools
import importlib
import json
import re


def flatten(o):
    """Flatten dicts and lists, recursively, JSON-style

    It's a generator that yields key-value pairs.

    Example:
        >>> dict(flatten({"a": [{"b": 1}, [2, 3], 4, {"c.d": 5, True: 6}]}))
        {'.a[0].b': 1,
         '.a[1][0]': 2,
         '.a[1][1]': 3,
         '.a[2]': 4,
         '.a[3]["c.d"]': 5,
         '.a[3][true]': 6}
    """
    if isinstance(o, dict):
        for key, value in o.items():
            if isinstance(key, str) and "." in key:
                key = '["{}"]'.format(key)
            elif isinstance(key, str):
                key = ".{}".format(key)
            else:
                key = '[{}]'.format(json.dumps(key))
            for subkey, subvalue in flatten(value):
                yield key + subkey, subvalue
    elif isinstance(o, list):
        for index, value in enumerate(o):
            for subkey, subvalue in flatten(value):
                yield "[{}]".format(index) + subkey, subvalue
    else:
        yield "", o


def exclude_useless_paths(o, useless_paths):
    if useless_paths is None:
        useless_paths = []
    for key, value in o:
        for path in useless_paths:
            if re.match(path, key):
                break
        else:
            yield key, value


def dump(o, useless_paths=None):
    for key, value in exclude_useless_paths(flatten(o),
                                            useless_paths):
        yield "{}: {}\n".format(key, json.dumps(value))


def get_diff(d1, d2, useless_paths=None):
    diff = difflib.unified_diff(tuple(dump(d1, useless_paths)),
                                tuple(dump(d2, useless_paths)), n=0)
    return "".join(list(diff)[2:])  # remove control and blank lines


cached_property = functools.lru_cache()(property)


def import_class(path):
    try:
        module_path, cls_name = path.rsplit(".", 1)
    except ValueError:
        raise ValueError("'{}' is not a valid class path".format(path))
    module = importlib.import_module(module_path)
    try:
        cls = getattr(module, cls_name)
    except AttributeError:
        raise ImportError("'{}' does not exist in '{}'".format(cls_name, path))
    return cls


def cast(old, new):
    if type(old) == type(new):
        return new
    if isinstance(new, str):
        if isinstance(old, bool):
            if new in ("1", "true", "True"):
                return True
            if new in ("0", "false", "False"):
                return False
            raise ValueError
        if isinstance(old, (list, tuple)):
            new = new.split(",")
            if len(old):
                return type(old)(cast(old[0], o) for o in new)
    return type(old)(new)
