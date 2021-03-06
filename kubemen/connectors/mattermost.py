import json
from urllib.parse import urljoin

import requests

from kubemen.connectors.base import Connector


class Mattermost(Connector):
    _message_style = {
        "CREATE": {"color": "#228b22", "emoji": ":rocket:"},
        "UPDATE": {"color": "#1e90ff", "emoji": ":zap:"},
        "RELOAD": {"color": "#ff8c00", "emoji": ":recycle:"},
        "DELETE": {"color": "#dc143c", "emoji": ":x:"}
    }

    def send(self, change, character, user):
        fields = []
        if self.attach_images and change.images:
            value = "".join(["- `{}`\n".format(image)
                             for image in change.images])
            fields.append({"title": "Images", "value": value})
        if self.attach_diff and change.diff:
            fields.append({"title": "YAML configuration diff",
                           "value": "```diff\n{}```".format(change.diff)})

        hashtag = "#unrelease" if change.operation == "DELETE" else "#release"
        emoji = self._message_style[change.operation]["emoji"]
        text = self.text_message_format.format(emoji=emoji, hashtag=hashtag,
                                               namespace=change.namespace,
                                               kind=change.kind,
                                               name=change.name,
                                               operation=change.operation,
                                               username=user.formatted_name)
        message = {"text": text}

        if self.channel_id:
            message.update(channel=self.channel_id)

        if fields:
            color = self._message_style[change.operation]["color"]
            attachment = {"color": color, "fields": fields}
            message.update(attachments=[attachment])

        if self.attach_badge and fields:
            message["attachments"][0].update(thumb_url=self.badge_url)

        if self.use_random_character:
            icon_url = urljoin(self.icons_base_url, character.icon_filename)
            message.update(username=character.name, icon_url=icon_url)
        else:
            if self.username:
                message.update(username=self.username)
            if self.icon_url:
                message.update(icon_url=self.icon_url)

        requests.post(self.hook_url, data=json.dumps(message))
