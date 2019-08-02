import difflib
import json
import re
from os import getenv

import requests
from flask import request
from flask_stupe.json import Stupeflask

app = Stupeflask(__name__)


ATTACHMENTS_STYLE = {
    "CREATE": {"color": "#228b22", "emoji": ":rocket:"},
    "UPDATE": {"color": "#1e90ff", "emoji": ":recycle:"},
    "DELETE": {"color": "#dc143c", "emoji": ":x:"}
}
USELESS_PATHS = (
    r'\.metadata\.generation',
    r'.*\.annotations\["kubectl\.kubernetes\.io/last-applied-configuration"\]',
    r'.*\.annotations\["kubectl\.kubernetes\.io/restartedAt"\]'
)
MATTERMOST_HOOK_URL = getenv("MATTERMOST_HOOK_URL")


@app.route("/", methods=["GET"])
def get():
    """200 as a service, for Kubernetes probes"""
    return 200


def flatten(o):
    """Flatten dicts and lists, recursively, JSON-style

    It's a generator that yields key-value pairs.

    Example:
        >>> dict(flatten({"a": [{"b": 1}, [2, 3], 4, {"c.d": 5, True: 6}]}))
        {'.a[0].b': 1,
         '.a[1][0]': 2,
         '.a[1][1]': 3,
         '.a[2]': 4},
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


def exclude_useless_paths(o):
    for key, value in o:
        for path in USELESS_PATHS:
            if re.match(path, key):
                break
        else:
            yield key, value


def dump(o):
    for key, value in exclude_useless_paths(flatten(o)):
        yield "{}: {}\n".format(key, json.dumps(value))


def get_diff(d1, d2):
    diff = difflib.unified_diff(tuple(dump(d1)), tuple(dump(d2)), n=0)
    return "".join(list(diff)[2:])  # remove control and blank lines


@app.route("/", methods=["POST"])
def post():
    review = request.get_json()
    review["response"] = {"uid": review["request"]["uid"], "allowed": True}

    # Skip alerting if the operation was not manual
    username = review["request"]["userInfo"]["username"]
    if "@numberly.com" not in username:
        return review

    operation = review["request"]["operation"]
    if operation == "DELETE":
        hashtag = "#unrelease"
        kind = review["request"]["oldObject"]["kind"]
        name = review["request"]["oldObject"]["metadata"]["name"]
    else:
        hashtag = "#release"
        kind = review["request"]["object"]["kind"]
        name = review["request"]["object"]["metadata"]["name"]
    namespace = review["request"]["namespace"]

    color = ATTACHMENTS_STYLE[operation]["color"]
    emoji = ATTACHMENTS_STYLE[operation]["emoji"]
    text = "{} | {} | **{}** | {} **{}** *{}d* by `{}`"
    text = text.format(emoji, hashtag, namespace, kind, name,
                       operation.lower(), username.split("@")[0])
    attachment = {"color": color, "fields": []}

    # Append list of images to message for a Deployment update
    if kind == "Deployment" and operation != "DELETE":
        field = {"short": False,
                 "title": "Images",
                 "value": ""}
        spec = review["request"]["object"]["spec"]["template"]["spec"]
        for container in spec["containers"]:
            field["value"] += "- `{}`\n".format(container["image"])
        attachment["fields"].append(field)

    # Append diff of resource configuration for updates
    if operation == "UPDATE":
        diff = get_diff(review["request"]["oldObject"],
                        review["request"]["object"])
        field = {"short": False,
                 "title": "YAML configuration diff",
                 "value": "```diff\n{}```".format(diff)}
        attachment["fields"].append(field)

    # TODO: retrieve channel_id from annotation
    # TODO: change icon_url/username based on resource
    message = {"channel_id": "bot",
               "text": text}
    if attachment["fields"]:
        message.update({"attachments": [attachment]})
    requests.post(MATTERMOST_HOOK_URL, data=json.dumps(message))
    return review


if __name__ == "__main__":
    app.run()
