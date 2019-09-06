import importlib
import logging
import random
import re

from flask import current_app, request
from flask_stupe.json import Stupeflask

from kubemen.models import Change, Character, User

CHARACTER_NAMES = ["Doctor Manhattan", "Nite Owl", "Ozymandias", "Rorschach",
                   "Silk Spectre", "The Comedian"]

app = Stupeflask("kubemen")
app.config["METADATA_WRAPPING"] = False


@app.route("/", methods=["GET"])
def health():
    """200 as a service, for Kubernetes probes"""
    return 200


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
    review.update(response={"uid": review["request"]["uid"], "allowed": True})

    username_regexp = current_app.config.get("USERNAME_REGEXP")
    username_format = current_app.config.get("USERNAME_FORMAT")
    username = review["request"]["userInfo"]["username"]
    match = re.match(username_regexp, username)
    if not match:
        return review
    formatted_username = username_format.format(*match.groups())
    user = User(name=username, formatted_name=formatted_username)

    useless_paths = current_app.config.get("USELESS_DIFF_PATHS_REGEXPS")
    change = Change(review=review, useless_paths=useless_paths)

    character_name = random.choice(CHARACTER_NAMES)
    character = Character(name=character_name)

    global_config = {
        "fancyness_level": current_app.config.get("FANCYNESS_LEVEL", 2),
        "icons_base_url": current_app.config.get("ICONS_BASE_URL", "")
    }

    # Dispatch to connectors
    for connector in current_app.config.get("ENABLED_CONNECTORS"):
        module_name = "kubemen.connectors.{}".format(connector)
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            logging.warning("Invalid connector: {}".format(connector))
        else:
            namespace = connector.upper() + "_"
            config = current_app.config.get_namespace(namespace)
            for key, value in global_config.items():
                config.setdefault(key, value)
            module.send(change, character, user, **config)
    return review


__all__ = ["app"]
