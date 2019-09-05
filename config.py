"""Default Kubemen configuration

This file is meant to reference all the environment variables that can be
passed to the application, and their default value.

Stupeflask will load its configuration from this file first, and then will try
to override each variable with what's defined in the process environment.

If a matching variable is found in the environment, its value will be casted to
the type of the default value defined here.
"""
# This is only useful when running locally. When using the Docker image, you
# should pass those as arguments of gunicorn with the GUNICORN_CMD_ARGS
# environment variable (GUNICORN_CMD_ARGS="-b 0.0.0.0:8080", for example).
APP_HOST = "0.0.0.0"
APP_PORT = 8080

# This is only useful when running locally (hot reload on code changes).
# Production setups must disable it by passing APP_DEBUG=0 as an environment
# variable.
APP_DEBUG = True

# How to display usernames, given the groups matched with USERNAME_REGEXP.
USERNAME_FORMAT = "{0}"

# What usernames should be taken in account and how it should be extracted.
USERNAME_REGEXP = r"(.*)@.*"
# If you want to keep everything, and not just the first part of an email as in
# the default value, use the following one (be cautious though, this will allow
# serviceaccounts).
# USERNAMES_REGEX = r"(.*)"

# RegExps of YAML paths that shouldn't be taken into account when searching
# differences between two versions of an object that changed.
USELESS_DIFF_PATHS_REGEXPS = (
    r'\.metadata\.generation',
    r'.*\.annotations\["kubectl\.kubernetes\.io/last-applied-configuration"\]',
    r'.*\.annotations\["kubectl\.kubernetes\.io/restartedAt"\]'
)

# How fancy the message should be, from 0 to 2 (connector dependent)
FANCYNESS_LEVEL = 2

# A base URL where the icons of Watchmen can be fetched
ICONS_BASE_URL = "https://raw.githubusercontent.com/numberly/kubemen/master/artwork/icons/"

ENABLED_CONNECTORS = (
    "mattermost",
    "email"
)

# Mattermost connector
MATTERMOST_HOOK_URL = ""
MATTERMOST_TEXT_MESSAGE_FORMAT = "{emoji} **{operation}** of `{kind}` **{name}** by `{username}` in `{namespace}` {hashtag}"
