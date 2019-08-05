"""Default Kubemen configuration

This file is meant to reference all the environment variables that can be
passed to the application, and their default value.

Stupeflask will load its configuration from this file first, and then will try
to override each variable with what's defined in the process environment.

If a matching variable is found in the environment, its value will be casted to
the type of the default value defined here.
"""
APP_HOST = "0.0.0.0"
APP_PORT = 8080
APP_DEBUG = True

MATTERMOST_HOOK_URL = ""
MATTERMOST_TEXT_MESSAGE_FORMAT = "{emoji} | {hashtag} | **{namespace}** | {kind} **{name}** *{operation}d* by `{username}`"
ICONS_BASE_URL = "https://raw.githubusercontent.com/numberly/kubemen/master/icons/{}.png"

USERNAME_FORMAT = "{0}"
USERNAME_REGEXP = r"(.*)@.*"

# Example: keep everything, not just the first part of an email.
# Be cautious though, this will allow serviceaccounts.
# USERNAMES_REGEX = r"(.*)"

USELESS_DIFF_PATHS = (
    r'\.metadata\.generation',
    r'.*\.annotations\["kubectl\.kubernetes\.io/last-applied-configuration"\]',
    r'.*\.annotations\["kubectl\.kubernetes\.io/restartedAt"\]'
)
