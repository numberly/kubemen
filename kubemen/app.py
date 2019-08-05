import json
import random

import requests
from flask import current_app, request
from flask_stupe.json import Stupeflask

from kubemen.diff import get_diff

app = Stupeflask("kubemen")


ATTACHMENTS_STYLE = {
    "CREATE": {"color": "#228b22", "emoji": ":rocket:"},
    "UPDATE": {"color": "#1e90ff", "emoji": ":recycle:"},
    "DELETE": {"color": "#dc143c", "emoji": ":x:"}
}
WATCHMEN_MEMBERS = ["Doctor Manhattan", "Nite Owl", "Ozymandias",
                    "Rorschach", "Silk Spectre", "The Comedian"]


@app.route("/", methods=["GET"])
def get():
    """200 as a service, for Kubernetes probes"""
    return 200


# TODO: validate admission review schema
@app.route("/", methods=["POST"])
def post():
    """TODO: write docstring"""
    review = request.get_json(force=True)
    review.update(response={"uid": review["request"]["uid"], "allowed": True})

    # Skip alerting and allow admission request if the operation was not manual
    username = review["request"]["userInfo"]["username"]
    service_accounts_prefix = current_app.config.get("SERVICE_ACCOUNTS_PREFIX")
    if service_accounts_prefix and service_accounts_prefix in username:
        return review
    usernames_domain = current_app.config.get("USERNAMES_DOMAIN")
    if usernames_domain and usernames_domain not in username:
        username = username.split("@")[0]
        return review

    operation = review["request"]["operation"]
    if operation == "DELETE":
        hashtag = "#unrelease"
        object = review["request"]["oldObject"]
    else:
        hashtag = "#release"
        object = review["request"]["object"]

    kind = object["kind"]
    name = object["metadata"]["name"]
    namespace = review["request"]["namespace"]

    color = ATTACHMENTS_STYLE[operation]["color"]
    emoji = ATTACHMENTS_STYLE[operation]["emoji"]
    text = current_app.config.get("MATTERMOST_TEXT_MESSAGE_FORMAT")
    text = text.format(emoji=emoji, hashtag=hashtag, namespace=namespace,
                       kind=kind, name=name, operation=operation.lower(),
                       username=username)
    attachment = {"color": color, "fields": []}

    # Append list of images to message for a Deployment update
    if (kind == "Deployment" and operation != "DELETE"
        and "spec" in object and "template" in object["spec"]
        and "spec" in object["spec"]["template"]
        and "containers" in object["spec"]["template"]["spec"]
        and object["spec"]["template"]["spec"]["containers"]):
        field = {"short": False,
                 "title": "Images",
                 "value": ""}
        for container in object["spec"]["template"]["spec"]["containers"]:
            if "image" in container:
                field["value"] += "- `{}`\n".format(container["image"])
        if field["value"]:
            attachment["fields"].append(field)

    # Append diff of resource configuration for updates
    if operation == "UPDATE":
        diff = get_diff(review["request"]["oldObject"],
                        review["request"]["object"])
        if diff:
            field = {"short": False,
                     "title": "YAML configuration diff",
                     "value": "```diff\n{}```".format(diff)}
            attachment["fields"].append(field)

    # TODO: retrieve channel_id from annotation
    message = {"channel_id": "bot", "text": text}

    # Randomly select a Watchmen member as notifier
    username = random.choice(WATCHMEN_MEMBERS)
    filename = username.lower().replace(" ", "_")
    icons_base_url = current_app.config.get("ICONS_BASE_URL")
    icon_url = icons_base_url.format(filename)
    message.update(username=username, icon_url=icon_url)

    # Update attachment with thumb_url and append it to message
    if attachment["fields"]:
        thumb_url = icons_base_url.format("kubemen")
        attachment.update(thumb_url=thumb_url)
        message.update({"attachments": [attachment]})

    # Send Mattermost notification and allow admission request
    mattermost_hook_url = current_app.config.get("MATTERMOST_HOOK_URL")
    requests.post(mattermost_hook_url, data=json.dumps(message))
    return review


__all__ = ["app"]
