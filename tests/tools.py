import random
import sys

import pytest

from kubemen.tools import (cached_property, cast, dump, exclude_useless_paths,
                           flatten, get_diff, import_class)


def test_flatten():
    d = dict(flatten({"a": [{"b": 1}, [2, 3], 4, {"c.d": 5, True: 6}]}))
    assert d == {'.a[0].b': 1,
                 '.a[1][0]': 2,
                 '.a[1][1]': 3,
                 '.a[2]': 4,
                 '.a[3]["c.d"]': 5,
                 '.a[3][true]': 6}


def test_exclude_useless_paths():
    d = {".foo.bar": 0,
         ".foo.baz": 1,
         ".foo.qux[0].foo": 2,
         ".foo.qux[0].bar": 3}
    useless_paths = [r"\.foo\.ba.*", r"\.foo\.qux\[[0-9]+\]\.bar"]
    iterator = exclude_useless_paths(d.items(), useless_paths)
    assert next(iterator)[1] == 2
    with pytest.raises(StopIteration):
        next(iterator)


def test_dump():
    t = tuple(dump(({"a": [{"b": 1}, [2, 3], 4, {"c.d": 5, True: 6}]})))
    assert t == ('.a[0].b: 1\n',
                 '.a[1][0]: 2\n',
                 '.a[1][1]: 3\n',
                 '.a[2]: 4\n',
                 '.a[3]["c.d"]: 5\n',
                 '.a[3][true]: 6\n')


def test_get_diff():
    d1 = {"a": [{"b": 1}, [2, 3], 4, {"c.d": 5, True: 6}]}
    d2 = {"a": [{"b": 2}, [2, 3], 4, {"c.d": 5, True: 7}]}

    diff = get_diff(d1, d2)
    assert diff == ('@@ -1 +1 @@\n'
                    '-.a[0].b: 1\n'
                    '+.a[0].b: 2\n'
                    '@@ -6 +6 @@\n'
                    '-.a[3][true]: 6\n'
                    '+.a[3][true]: 7\n')


def test_cached_property():
    class Foo:
        def randint(self):
            return random.randint(0, sys.maxsize)

    foo = Foo()
    assert foo.randint() != foo.randint()
    foo.randint = cached_property(foo.randint)
    assert foo.randint == foo.randint


def test_import_class():
    with pytest.raises(ValueError):
        import_class("invalid")
    with pytest.raises(ImportError):
        import_class("unknown.module.Class")
    with pytest.raises(ImportError):
        import_class("kubemen.UnknownClass")
    assert import_class("kubemen.connectors.base.Connector")


def test_cast():
    assert cast(0, 1) == 1
    assert cast("0", 1) == "1"
    assert cast(0, "1") == 1
    assert cast(False, "1") is True
    assert cast(False, "0") is False
    assert cast(False, "true") is True
    assert cast(False, "false") is False
    assert cast(False, "True") is True
    assert cast(False, "False") is False
    assert cast([False], "1") == [True]
    assert cast((False,), "1") == (True,)
    assert cast([], "0,1") == ["0", "1"]
    assert cast([False], "0,1") == [False, True]
    assert cast([False], "0,1") == [False, True]

    with pytest.raises(ValueError):
        cast(False, "invalid")
    with pytest.raises(ValueError):
        cast(0, "invalid")
