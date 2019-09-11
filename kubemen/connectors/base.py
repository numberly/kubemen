import logging

from kubemen.tools import cast


def _filter_prefix(d, prefix):
    """Yield formatted key-values pairs when key matches a prefix"""
    for key, value in d.items():
        if key.startswith(prefix):
            key = key.replace(prefix, "")
            key = key.lower()
            key = key.replace("-", "_")
            yield key, value


class Connector:
    """Base class for all connectors

    Connectors must implement the :meth:`~Connector.send` method.

    Any option related to this connector found in the environment or in the
    annotations will be added as an attribute of the instance itself, and thus
    accesible throught ``self`` inside :meth:`~Connector.send` (or any other
    method).

    Only environment variables and annotations that are prefixed with the
    connector's name are taken into account. Since both environment variables
    and annotations can only be represented as strings, their values are
    automatically casted in the type defined by the default value in
    `config.py`_ (or kept as string if their is no default value).

    For example, a ``Foo`` connector can be configured through the environment
    with the ``FOO_`` prefix. ``FOO_BAR_BAZ=1`` would result in
    ``Foo().bar_baz``` being ``1``, as integer or string depending on the
    default value in `config.py`_. Then it could be overriden later with an
    annotation of a watched resource: ``kubemen.numberly.com/foo.bar-baz: 1``.

    :param dict environment: Environment variables that might configure this
                             connector
    :param dict annotations: Annotations that might configure this connector

    .. _`config.py`: #module-config
    """

    def __init__(self, environment, annotations):
        name = self.__class__.__name__

        environment_prefix = self.__class__.__name__.upper() + "_"
        for key, value in _filter_prefix(environment, environment_prefix):
            setattr(self, key, value)

        annotations_prefix = self.__class__.__name__.lower() + "."
        for key, value in _filter_prefix(annotations, annotations_prefix):
            try:
                current_value = getattr(self, key)
            except AttributeError:
                logging.warning("'{}': unkown option '{}', ignoring option"
                                .format(name, key))
                continue
            try:
                value = cast(current_value, value)
            except ValueError:
                logging.warning("'{}': can not cast '{}', ignoring option"
                                .format(name, key, type(value)))
                continue
            setattr(self, key, value)

        logging.debug("{}: {}".format(name, self.__dict__))

    def send(self, change, character, user):
        """
        :param change: What changed on Kubernetes
        :type change: :class:`~kubemen.models.Change`
        :param character: A random Watchmen character
        :type character: :class:`~kubemen.models.Character`
        :param user: The user that modified the resource
        :type user: :class:`~kubemen.models.User`
        """
        raise NotImplementedError
