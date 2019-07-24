import json
from os import getenv

import requests
from flask import request
from flask_stupe.json import Stupeflask

app = Stupeflask(__name__)


MATTERMOST_HOOK_URL = getenv("MATTERMOST_HOOK_URL")


@app.route("/", methods=["GET"])
def get():
    return 200


@app.route("/", methods=["POST"])
def post():
    review = request.get_json()
    review["response"] = {"uid": review["request"]["uid"], "allowed": True}
    obj = review["request"]["object"]

    username = review["request"]["userInfo"]["username"]
    text = "#release | **{}** by {} | :rocket:\n".format(obj["kind"], username)

    for container in obj["spec"]["template"]["spec"]["containers"]:
        text += "  - `{}`\n".format(container["image"])

    requests.post(MATTERMOST_HOOK_URL, data=json.dumps({"text": text}))
    return review


if __name__ == "__main__":
    app.run()
