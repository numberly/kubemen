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

    This endpoint is dryRun-aware, meaning no message will be sent for a
    request with dryRun: true.

    :json: A complete `AdmissionReview object
           <https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/#webhook-request-and-response>`_
    """
    review = request.get_json(force=True)
    review["response"] = {"uid": review["request"]["uid"], "allowed": True}

    if review.get("dryRun"):
        logging.debug("Skipping dryRun")
        return review

    annotations_prefix = current_app.config.get("ANNOTATIONS_PREFIX")
    useless_paths = current_app.config.get("USELESS_DIFF_PATHS_REGEXPS")
    change = Change(review=review, annotations_prefix=annotations_prefix,
                    useless_paths=useless_paths)
    logging.debug("{}: {} {}/{} ({})".format(change.operation, change.kind,
                                             change.namespace, change.name,
                                             change.username))

    username_regexp = current_app.config.get("USERNAME_REGEXP")
    username_format = current_app.config.get("USERNAME_FORMAT")
    match = re.match(username_regexp, change.username)
    if not match:
        logging.debug("Skipping mismatching username")
        return review
    formatted_username = username_format.format(*match.groups())
    user = User(name=change.username, formatted_name=formatted_username)

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
                logging.debug("Calling connector: {}".format(connector_path))
                connector.send(change, character, user)
    return review


__all__ = ["app"]
