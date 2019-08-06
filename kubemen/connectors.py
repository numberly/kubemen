import json
import random

import requests
from flask import current_app

ATTACHMENT_STYLE = {
    "CREATE": {"color": "#228b22", "emoji": ":rocket:"},
    "UPDATE": {"color": "#1e90ff", "emoji": ":recycle:"},
    "DELETE": {"color": "#dc143c", "emoji": ":x:"}
}
WATCHMEN_MEMBERS = ["Doctor Manhattan", "Nite Owl", "Ozymandias",
                    "Rorschach", "Silk Spectre", "The Comedian"]


def send_mattermost_message(operation, hashtag, namespace, kind, name,
                            username, images, diff, fancyness_level):
    color = ATTACHMENT_STYLE[operation]["color"]
    emoji = ATTACHMENT_STYLE[operation]["emoji"]
    text = current_app.config.get("MATTERMOST_TEXT_MESSAGE_FORMAT")
    text = text.format(emoji=emoji, hashtag=hashtag, namespace=namespace,
                       kind=kind, name=name, operation=operation.lower(),
                       username=username)

    attachment = {"color": color, "fields": []}
    if images:
        value = ""
        for image in images:
            value += "- `{}`\n".format(image)
        attachment["fields"].append({"short": False,
                                     "title": "Images",
                                     "value": value})
    if diff:
        attachment["fields"].append({"short": False,
                                     "title": "YAML configuration diff",
                                     "value": "```diff\n{}```".format(diff)})
    elif kind == "Deployment" and operation == "UPDATE":
        text = text.replace("updated", "reloaded")

    # TODO: retrieve channel_id from annotation
    message = {"channel_id": "bot"}
    icons_base_url = current_app.config.get("ICONS_BASE_URL")
    if fancyness_level > 0:
        thumb_url = icons_base_url.format("kubemen")
        attachment.update(thumb_url=thumb_url)
    if fancyness_level > 1:  # TODO: test fancyness
        # Randomly select a Watchmen member as notifier
        bot_username = random.choice(WATCHMEN_MEMBERS)
        icon_filename = bot_username.lower().replace(" ", "_")
        icon_url = icons_base_url.format(icon_filename)
        message.update(username=bot_username, icon_url=icon_url)

    message.update(text=text)
    if attachment["fields"]:
        message.update({"attachments": [attachment]})
    mattermost_hook_url = current_app.config.get("MATTERMOST_HOOK_URL")
    requests.post(mattermost_hook_url, data=json.dumps(message))
