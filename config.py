"""
This file references all the environment variables that can be passed to the
application, and their default value.

Kubemen will load its configuration from this file first, and then will try to
override each variable with what is defined in the process environment. If a
matching variable is found in the environment, its value will be casted to the
type of the default value defined here.

Kubemen will then follow the same process if a matching annotation is found in
a watched resource, and modify its behavior for the handling of this particular
object. But only connector prefixed options can be modified this way.

Please refer to the description of :class:`~kubemen.connectors.base.Connector`
for more information on this behavior.
"""

#: This is only useful when running locally. When using the Docker image, you
#: should pass those as arguments of gunicorn with the ``GUNICORN_CMD_ARGS``
#: environment variable (``GUNICORN_CMD_ARGS="-b 0.0.0.0:8080"``, for example).
APP_HOST, APP_PORT = "0.0.0.0", 8080

#: This is only useful when running locally (hot reload on code changes).
#: Production setups must disable it by passing APP_DEBUG=0 as an environment
#: variable.
APP_DEBUG = True

#: Prefix to use for Kubemen-specific annotations. Must not contain a slash.
ANNOTATIONS_PREFIX = "kubemen.numberly.com"

#: How to display usernames, given the groups matched with
#: :obj:`~USERNAME_REGEXP`.
USERNAME_FORMAT = "{0}"

#: What usernames should be taken in account and how it should be extracted.
#: If you want to keep everything, and not just the first part of an email as
#: in the default value, use the following one (be cautious though, this will
#: allow serviceaccounts): ``USERNAMES_REGEX = r"(.*)"``
USERNAME_REGEXP = r"(.*)@.*"

#: RegExps of YAML paths that shouldn't be taken into account when searching
#: differences between two versions of an object that changed.
USELESS_DIFF_PATHS_REGEXPS = (
    r'\.metadata\.generation',
    r'.*\.annotations\["kubectl\.kubernetes\.io/last-applied-configuration"\]',
    r'.*\.annotations\["kubectl\.kubernetes\.io/restartedAt"\]'
)

#: List of connectors that can be used through annotations, even if the
#: connector is disabled globally.
AVAILABLE_CONNECTORS = (
    "kubemen.connectors.mattermost.Mattermost",
    "kubemen.connectors.email.Email"
)

#: Enable the Mattermost connector globally.
#: This can still be overriden for any given resource with the
#: ``kubemen.numberly.com/mattermost.enable`` annotation. See
#: :obj:`AVAILABLE_CONNECTORS` if you wish to forbid this connector.
MATTERMOST_ENABLE = True

#: Hook URL as defined with the "Incoming Webhook" configuration. This is the
#: URL that Kubemen will use to send messages to Mattermost.
MATTERMOST_HOOK_URL = ""

#: How to format messages sent to Mattermost.
MATTERMOST_TEXT_MESSAGE_FORMAT = "{emoji} **{operation}** of `{kind}` **{name}** by `{username}` in `{namespace}` {hashtag}"

#: Whether to add a fancy badge to attachments (it's more visible) or not.
MATTERMOST_ATTACH_BADGE = True

#: If :obj:`~MATTERMOST_ATTACH_BADGE` is true, define the badge URL.
MATTERMOST_BADGE_URL = "https://raw.githubusercontent.com/numberly/kubemen/master/artwork/icons/kubemen.png"

#: Whether to replace the default Mattermost webhook's avatar and name with a
#: Watchmen character (i.e. `Rorschach`, `Doctor Manhattan`, etc) or not.
MATTERMOST_USE_RANDOM_CHARACTER = True

#: If :obj:`~MATTERMOST_USE_RANDOM_CHARACTER` is true, define the base URL on
#: which the icons of Watchmen can be fetched.
MATTERMOST_ICONS_BASE_URL = "https://raw.githubusercontent.com/numberly/kubemen/master/artwork/icons/"

#: Enable the Email connector globally.
#: This can still be overriden for any given resource with the
#: ``kubemen.numberly.com/mattermost.enable`` annotation. See
#: :obj:`AVAILABLE_CONNECTORS` if you wish to forbid this connector.
EMAIL_ENABLE = True
