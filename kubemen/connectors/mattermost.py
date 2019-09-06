import json
from urllib.parse import urljoin

import requests

MESSAGE_STYLE = {
    "CREATE": {"color": "#228b22", "emoji": ":rocket:"},
    "UPDATE": {"color": "#1e90ff", "emoji": ":zap:"},
    "RELOAD": {"color": "#ff8c00", "emoji": ":recycle:"},
    "DELETE": {"color": "#dc143c", "emoji": ":x:"}
}


def send(change, character, user, *, fancyness_level, hook_url, icons_base_url,
         text_message_format, **_):
    fields = []
    if change.images:
        value = ""
        for image in change.images:
            value += "- `{}`\n".format(image)
        fields.append({"title": "Images", "value": value})
    if change.diff:
        fields.append({"title": "YAML configuration diff",
                       "value": "```diff\n{}```".format(change.diff)})

    hashtag = "#unrelease" if change.operation == "DELETE" else "#release"
    emoji = MESSAGE_STYLE[change.operation]["emoji"]
    text = text_message_format.format(emoji=emoji, hashtag=hashtag,
                                      namespace=change.namespace,
                                      kind=change.kind, name=change.name,
                                      operation=change.operation,
                                      username=user.formatted_name)

    # TODO: retrieve channel_id from annotation
    message = {"channel_id": "bot", "text": text}
    if fields:
        color = MESSAGE_STYLE[change.operation]["color"]
        attachment = {"color": color, "fields": fields}
        message.update({"attachments": [attachment]})

    if fancyness_level > 0 and fields:
        thumb_url = urljoin(icons_base_url, "kubemen.png")
        message["attachments"][0].update(thumb_url=thumb_url)
    if fancyness_level > 1:  # TODO: test fancyness
        icon_url = urljoin(icons_base_url, character.icon_filename)
        message.update(username=character.name, icon_url=icon_url)

    requests.post(hook_url, data=json.dumps(message))
