import pytest

from kubemen.models import Change, Character


@pytest.fixture
def change(review):
    return Change(review=review, useless_paths=[])


def test_change_operation(change):
    assert change.operation == "UPDATE"


def test_change_operation_without_diff(change):
    del change.review["request"]["oldObject"]["spec"]
    del change.review["request"]["object"]["spec"]
    assert change.operation == "RELOAD"


def test_change_name(change):
    assert change.name == "the-answer-to-the-ultimate-question"


def test_change_kind(change):
    assert change.kind == "Deployment"


def test_change_images(change):
    assert len(change.images) == 1
    assert change.images[0] == "6.9"


def test_change_images_without_image(change):
    del change.review["request"]["object"]["spec"]
    assert change.images == []


def test_change_diff(change):
    assert len(change.diff)


def test_change_diff_for_secrets(change):
    change.review["request"]["oldObject"]["kind"] = "Secret"
    change.review["request"]["object"]["kind"] = "Secret"
    assert change.diff is None


def test_change_namespace(change):
    assert change.namespace == "magrathea"


@pytest.fixture
def character(review):
    return Character(name="Foo Bar")


def test_character_icon_filename(character):
    assert character.icon_filename == "foo_bar.png"
