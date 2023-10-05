import discord


class Embed(discord.Embed):
    """Catherine's custom default embed"""

    def __init__(self, **kwargs):
        kwargs.setdefault("color", discord.Color.from_rgb(236, 189, 255))
        super().__init__(**kwargs)


class SuccessEmbed(discord.Embed):
    """Kumiko's custom success action embed"""

    def __init__(self, **kwargs):
        kwargs.setdefault("color", discord.Color.from_rgb(75, 181, 67))
        kwargs.setdefault("title", "Action successful")
        kwargs.setdefault("description", "The action requested was successful")
        super().__init__(**kwargs)


class ErrorEmbed(discord.Embed):
    """Kumiko's custom error embed"""

    def __init__(self, **kwargs):
        kwargs.setdefault("color", discord.Color.from_rgb(214, 6, 6))
        kwargs.setdefault("title", "Oh no, an error has occurred!")
        kwargs.setdefault(
            "description",
            "Uh oh! It seems like the command ran into an issue! For support, please visit [Catherine-Chan's Support Server](https://discord.gg/ns3e74frqn) to get help!",
        )
        super().__init__(**kwargs)


class ConfirmEmbed(discord.Embed):
    """Kumiko's custom confirm embed"""

    def __init__(self, **kwargs):
        kwargs.setdefault("color", discord.Color.from_rgb(255, 191, 0))
        kwargs.setdefault("title", "Are you sure?")
        super().__init__(**kwargs)


class EstrogenEmbed(discord.Embed):
    def __init__(self, **kwargs):
        kwargs.setdefault("color", discord.Color.from_str("#F7A8B8"))
        kwargs.setdefault("title", "Estradiol Level Conversions")
        super().__init__(**kwargs)


class ProgEmbed(discord.Embed):
    def __init__(self, **kwargs):
        kwargs.setdefault("color", discord.Color.from_str("#FFFFFF"))
        kwargs.setdefault("title", "Progesterone Level Conversions")
        super().__init__(**kwargs)


class TestosteroneEmbed(discord.Embed):
    def __init__(self, **kwargs):
        kwargs.setdefault("color", discord.Color.from_str("#55CDFC"))
        kwargs.setdefault("title", "Testosterone Level Conversions")
        super().__init__(**kwargs)
