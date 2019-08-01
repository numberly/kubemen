import difflib
import json
from os import getenv

import requests
import yaml
from flask import request
from flask_stupe.json import Stupeflask

app = Stupeflask(__name__)


EMOJIS = {"CREATE": ":rocket:",
          "UPDATE": ":recycle:",
          "DELETE": ":x:"}
MATTERMOST_HOOK_URL = getenv("MATTERMOST_HOOK_URL")


@app.route("/", methods=["GET"])
def get():
    return 200


def yaml_diff(d1, d2):
    yaml1 = yaml.dump(d1)
    yaml2 = yaml.dump(d2)
    diff = difflib.unified_diff(yaml1.splitlines(keepends=True),
                                yaml2.splitlines(keepends=True))
    return ''.join(diff)


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

    text = "{} | {} | {} | {} **{}** {}d by *{}*"
    text = text.format(EMOJIS[operation], hashtag, namespace, kind, name,
                       operation.lower(), username.split("@")[0])

    # Append list of images to message for a Deployment
    if kind == "Deployment" and operation != "DELETE":
        spec = review["request"]["object"]["spec"]["template"]["spec"]
        for container in spec["containers"]:
            text += "\n  - `{}`".format(container["image"])

    # Append diff of resource configuration for updates
    if operation == "UPDATE":
        diff = yaml_diff(review["request"]["oldObject"],
                         review["request"]["object"])
        text += "\n```diff\n{}\n```".format(diff)

    requests.post(MATTERMOST_HOOK_URL, data=json.dumps({"text": text}))
    return review


if __name__ == "__main__":
    app.run()
