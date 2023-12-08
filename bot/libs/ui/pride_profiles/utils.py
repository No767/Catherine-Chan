from .structs import SimpleProfileEntry, SimpleViewsEntry


class SimpleProfilesPageEntry:
    __slots__ = ("user_id", "name", "pronouns")

    def __init__(self, entry: SimpleProfileEntry):
        self.user_id = entry["user_id"]
        self.name = entry["name"]
        self.pronouns = entry["pronouns"]

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.user_id} | {self.pronouns or 'None'})"


class ViewsProfilePageEntry:
    __slots__ = ("user_id", "name", "views")

    def __init__(self, entry: SimpleViewsEntry):
        self.user_id = entry["user_id"]
        self.name = entry["name"]
        self.views = entry["views"]

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.user_id} | {self.views} view(s)))"
