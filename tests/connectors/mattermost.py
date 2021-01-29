import json

import requests

from kubemen.connectors.mattermost import Mattermost


def test_send(app, change, character, user, mocker):
    mattermost = Mattermost(app.config, {})
    mocker.patch("requests.post")
    mattermost.send(change, character, user)
    args, kwargs = requests.post.call_args
    assert args[0] == app.config["MATTERMOST_HOOK_URL"]
    data = json.loads(kwargs["data"])
    assert change.operation in data["text"]
    assert change.namespace in data["text"]
    assert change.kind in data["text"]
    assert user.formatted_name in data["text"]
    assert character.icon_filename in data["icon_url"]
    assert character.name == data["username"]
    assert "channel" not in data
    assert data["attachments"][0]["thumb_url"]


def test_send_without_badge(app, change, character, user, mocker):
    app.config["MATTERMOST_ATTACH_BADGE"] = False
    mattermost = Mattermost(app.config, {})
    mocker.patch("requests.post")
    mattermost.send(change, character, user)
    args, kwargs = requests.post.call_args
    data = json.loads(kwargs["data"])
    assert "thumb_url" not in data["attachments"][0]


def test_send_without_images(app, change, character, user, mocker):
    app.config["MATTERMOST_ATTACH_IMAGES"] = False
    app.config["MATTERMOST_ATTACH_DIFF"] = True
    mattermost = Mattermost(app.config, {})
    mocker.patch("requests.post")
    mattermost.send(change, character, user)
    args, kwargs = requests.post.call_args
    data = json.loads(kwargs["data"])
    assert len(data["attachments"][0]["fields"]) == 1
    assert "diff" in data["attachments"][0]["fields"][0]["title"]


def test_send_without_diff(app, change, character, user, mocker):
    app.config["MATTERMOST_ATTACH_IMAGES"] = True
    app.config["MATTERMOST_ATTACH_DIFF"] = False
    mattermost = Mattermost(app.config, {})
    mocker.patch("requests.post")
    mattermost.send(change, character, user)
    args, kwargs = requests.post.call_args
    data = json.loads(kwargs["data"])
    assert len(data["attachments"][0]["fields"]) == 1
    assert data["attachments"][0]["fields"][0]["title"] == "Images"


def test_send_without_attachments(app, change, character, user, mocker):
    app.config["MATTERMOST_ATTACH_IMAGES"] = False
    app.config["MATTERMOST_ATTACH_DIFF"] = False
    mattermost = Mattermost(app.config, {})
    mocker.patch("requests.post")
    mattermost.send(change, character, user)
    args, kwargs = requests.post.call_args
    data = json.loads(kwargs["data"])
    assert "attachments" not in data


def test_send_with_channel_id(app, change, character, user, mocker):
    app.config["MATTERMOST_CHANNEL_ID"] = "foo"
    mattermost = Mattermost(app.config, {})
    mocker.patch("requests.post")
    mattermost.send(change, character, user)
    args, kwargs = requests.post.call_args
    data = json.loads(kwargs["data"])
    assert data["channel"] == "foo"


def test_send_without_random_character(app, change, character, user, mocker):
    app.config["MATTERMOST_USERNAME"] = "Kubemen"
    app.config["MATTERMOST_ICON_URL"] = "kubernetes.png"
    app.config["MATTERMOST_USE_RANDOM_CHARACTER"] = False
    mattermost = Mattermost(app.config, {})
    mocker.patch("requests.post")
    mattermost.send(change, character, user)
    args, kwargs = requests.post.call_args
    data = json.loads(kwargs["data"])
    assert "Kubemen" in data["username"]
    assert "kubernetes.png" in data["icon_url"]
