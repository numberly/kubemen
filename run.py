import difflib
import json
from os import getenv

import requests
import yaml
from flask import request
from flask_stupe.json import Stupeflask

app = Stupeflask(__name__)


ATTACHMENTS_STYLE = {
    "CREATE": {"color": "#228b22", "emoji": ":rocket:"},
    "UPDATE": {"color": "#1e90ff", "emoji": ":recycle:"},
    "DELETE": {"color": "#dc143c", "emoji": ":x:"}
}
MATTERMOST_HOOK_URL = getenv("MATTERMOST_HOOK_URL")


@app.route("/", methods=["GET"])
def get():
    return 200


# TODO: extract generation from diff
# TODO: ignore kubectl.kubernetes.io/last-applied-configuration diff
def yaml_diff(d1, d2):
    yaml1 = yaml.dump(d1)
    yaml2 = yaml.dump(d2)
    diff = difflib.unified_diff(yaml1.splitlines(keepends=True),
                                yaml2.splitlines(keepends=True),
                                n=2)  # number of context lines
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
    # TODO: append only if yaml-diff annotation if specified
    if operation == "UPDATE":
        diff = yaml_diff(review["request"]["oldObject"],
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
