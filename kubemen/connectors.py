import json
import random
import urllib.parse

import requests
from flask import current_app

MESSAGE_STYLE = {
    "CREATE": {"color": "#228b22", "emoji": ":rocket:"},
    "UPDATE": {"color": "#1e90ff", "emoji": ":zap:"},
    "RELOAD": {"color": "#ff8c00", "emoji": ":recycle:"},
    "DELETE": {"color": "#dc143c", "emoji": ":x:"}
}
WATCHMEN_MEMBERS = ["Doctor Manhattan", "Nite Owl", "Ozymandias",
                    "Rorschach", "Silk Spectre", "The Comedian"]


def send_mattermost_message(operation, hashtag, namespace, kind, name,
                            username, images, diff, fancyness_level):
    fields = []
    if images:
        value = ""
        for image in images:
            value += "- `{}`\n".format(image)
        fields.append({"title": "Images", "value": value})
    if diff:
        fields.append({"title": "YAML configuration diff",
                       "value": "```diff\n{}```".format(diff)})
    elif kind == "Deployment" and operation == "UPDATE":
        operation = "RELOAD"

    emoji = MESSAGE_STYLE[operation]["emoji"]
    text = current_app.config.get("MATTERMOST_TEXT_MESSAGE_FORMAT")
    text = text.format(emoji=emoji, hashtag=hashtag, namespace=namespace,
                       kind=kind, name=name, operation=operation,
                       username=username)

    # TODO: retrieve channel_id from annotation
    message = {"channel_id": "bot", "text": text}
    if fields:
        color = MESSAGE_STYLE[operation]["color"]
        attachment = {"color": color, "fields": fields}
        message.update({"attachments": [attachment]})
    icons_base_url = current_app.config.get("ICONS_BASE_URL")
    if fancyness_level > 0 and fields:
        thumb_url = urllib.parse.urljoin(icons_base_url, "kubemen.png")
        message["attachments"][0].update(thumb_url=thumb_url)
    if fancyness_level > 1:  # TODO: test fancyness
        # Randomly select a Watchmen member as notifier
        bot_username = random.choice(WATCHMEN_MEMBERS)
        icon_filename = bot_username.lower().replace(" ", "_") + ".png"
        icon_url = urllib.parse.urljoin(icons_base_url, icon_filename)
        message.update(username=bot_username, icon_url=icon_url)

    mattermost_hook_url = current_app.config.get("MATTERMOST_HOOK_URL")
    requests.post(mattermost_hook_url, data=json.dumps(message))
