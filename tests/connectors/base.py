import pytest

from kubemen.connectors.base import Connector, _filter_prefix


@pytest.fixture
def environment():
    return {
        "FOO": 0,
        "FOO_BAR": 1,
        "FOO_BAR_BAZ": 2
    }


@pytest.fixture
def annotations():
    return {
        "foo": 0,
        "foo.bar": 1,
        "foo.bar-baz": 2
    }


def test_filter_prefix(environment, annotations):
    expected = {
        "bar": 1,
        "bar_baz": 2
    }
    assert dict(_filter_prefix(environment, "FOO_")) == expected
    assert dict(_filter_prefix(annotations, "foo.")) == expected


def test_connector_init(environment, annotations):
    class Foo(Connector):
        pass

    foo = Foo(environment, {})
    assert foo.bar == 1
    assert foo.bar_baz == 2


def test_connector_init_annotations_precedence(environment, annotations):
    class Foo(Connector):
        pass

    annotations["foo.bar-baz"] = "1"
    foo = Foo(environment, annotations)
    assert foo.bar == 1
    assert foo.bar_baz == 1


def test_connector_init_unknown_annotations(annotations, caplog):
    class Foo(Connector):
        pass

    foo = Foo({}, annotations)
    assert "bar" in caplog.text
    assert "bar_baz" in caplog.text

    with pytest.raises(AttributeError):
        foo.bar
    with pytest.raises(AttributeError):
        foo.bar_baz


def test_connector_init_wrong_type(environment, annotations, caplog):
    class Foo(Connector):
        pass

    annotations["foo.bar"] = "one"
    annotations["foo.bar-baz"] = "two"

    foo = Foo(environment, annotations)
    assert "bar" in caplog.text
    assert "bar_baz" in caplog.text

    assert foo.bar == 1
    assert foo.bar_baz == 2


def test_connector_abstract_methods():
    class Foo(Connector):
        pass

    foo = Foo({}, {})
    with pytest.raises(NotImplementedError):
        foo.send(None, None, None)
