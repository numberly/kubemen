import logging
import random
import re

from flask import current_app, request
from flask_stupe.json import Stupeflask

from kubemen.models import Change, Character, User
from kubemen.tools import import_class

CHARACTER_NAMES = ["Doctor Manhattan", "Nite Owl", "Ozymandias", "Rorschach",
                   "Silk Spectre", "The Comedian"]

app = Stupeflask("kubemen")
app.config["METADATA_WRAPPING"] = False

if app.config.get("APP_DEBUG"):
    logging.getLogger().setLevel(logging.DEBUG)


@app.route("/", methods=["GET"])
def health():
    """200 as a service, for Kubernetes probes"""
    return "", 200


@app.route("/", methods=["POST"])
def kubemen():
    """Kubemen's entrypoint

    This endpoint extracts AdmissionReview data and send message on the chosen
    platforms.

    All review requests are allowed in order to be as transparent as
    possible for the cluster.

    :json: A complete `AdmissionReview object
           <https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/#webhook-request-and-response>`_
    """
    review = request.get_json(force=True)
    review["response"] = {"uid": review["request"]["uid"], "allowed": True}

    username_regexp = current_app.config.get("USERNAME_REGEXP")
    username_format = current_app.config.get("USERNAME_FORMAT")
    username = review["request"]["userInfo"]["username"]
    match = re.match(username_regexp, username)
    if not match:
        return review
    formatted_username = username_format.format(*match.groups())
    user = User(name=username, formatted_name=formatted_username)

    annotations_prefix = current_app.config.get("ANNOTATIONS_PREFIX")
    useless_paths = current_app.config.get("USELESS_DIFF_PATHS_REGEXPS")
    change = Change(review=review, annotations_prefix=annotations_prefix,
                    useless_paths=useless_paths)

    character_name = random.choice(CHARACTER_NAMES)
    character = Character(name=character_name)

    for connector_path in current_app.config.get("AVAILABLE_CONNECTORS"):
        try:
            connector_cls = import_class(connector_path)
        except (ImportError, ValueError) as error:
            logging.warning("Invalid connector: {}".format(error))
        else:
            connector = connector_cls(current_app.config, change.annotations)
            if connector.enable:
                connector.send(change, character, user)
    return review


__all__ = ["app"]
