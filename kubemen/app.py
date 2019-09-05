import importlib
import logging
import re

from flask import current_app, request
from flask_stupe.json import Stupeflask

from kubemen.tools import get_diff

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

    # Validate the username against the regexp and format it
    username_regexp = current_app.config.get("USERNAME_REGEXP")
    username_format = current_app.config.get("USERNAME_FORMAT")
    username = review["request"]["userInfo"]["username"]
    match = re.match(username_regexp, username)
    if not match:
        return review
    username = username_format.format(*match.groups())

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

    # Extract list of images for a Deployment creation or update
    images = []
    if (kind == "Deployment" and operation != "DELETE"
        and "spec" in object and "template" in object["spec"]
        and "spec" in object["spec"]["template"]
        and "containers" in object["spec"]["template"]["spec"]
        and object["spec"]["template"]["spec"]["containers"]):
        for container in object["spec"]["template"]["spec"]["containers"]:
            images.append(container["image"])

    # Generate diff of resource configuration for updates except for Secrets
    diff = None
    if operation == "UPDATE" and kind != "Secret":
        useless_paths = current_app.config.get("USELESS_DIFF_PATHS_REGEXPS")
        diff = get_diff(review["request"]["oldObject"],
                        review["request"]["object"],
                        useless_paths)

    fancyness_level = current_app.config.get("FANCYNESS_LEVEL", 2)
    icons_base_url = current_app.config.get("ICONS_BASE_URL", "")

    # Dispatch to connectors
    for connector in current_app.config.get("ENABLED_CONNECTORS"):
        module_name = "kubemen.connectors.{}".format(connector)
        module = importlib.import_module(module_name)
        if not hasattr(module, "send"):
            logging.warning("Invalid connector: {}".format(connector))
        else:
            config_namespace = connector.upper() + "_"
            config = current_app.config.get_namespace(config_namespace)
            module.send(operation, hashtag, namespace, kind, name, username,
                        images, diff, fancyness_level, icons_base_url,
                        **config)
    return review


__all__ = ["app"]
