import types

from kubemen.tools import cached_property, get_diff


class Change(types.SimpleNamespace):
    @cached_property
    def _operation(self):
        return self.review["request"]["operation"]

    @cached_property
    def operation(self):
        if not self.diff and self._operation == "UPDATE":
            return "RELOAD"
        return self._operation

    @cached_property
    def object(self):
        if self._operation == "DELETE":
            return self.review["request"]["oldObject"]
        return self.review["request"]["object"]

    @cached_property
    def _annotations(self):
        return self.object["metadata"].get("annotations", {})

    @cached_property
    def annotations(self):
        annotations = {}
        for key, value in self._annotations.items():
            try:
                prefix, key = key.split("/", 1)
            except ValueError:
                continue
            if prefix == self.annotations_prefix:
                annotations[key] = value
        return annotations

    @cached_property
    def name(self):
        return self.object["metadata"]["name"]

    @cached_property
    def kind(self):
        return self.object["kind"]

    @cached_property
    def images(self):
        try:
            return [container["image"] for container
                    in self.object["spec"]["template"]["spec"]["containers"]]
        except KeyError:
            return []

    @cached_property
    def diff(self):
        if self._operation == "UPDATE" and self.kind != "Secret":
            return get_diff(self.review["request"]["oldObject"],
                            self.review["request"]["object"],
                            self.useless_paths)

    @cached_property
    def namespace(self):
        return self.review["request"]["namespace"]


class Character(types.SimpleNamespace):
    @cached_property
    def icon_filename(self):
        return self.name.lower().replace(" ", "_") + ".png"


class User(types.SimpleNamespace):
    pass
