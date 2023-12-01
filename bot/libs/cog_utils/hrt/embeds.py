import discord


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


class ProlactinEmbed(discord.Embed):
    def __init__(self, **kwargs):
        kwargs.setdefault("color", discord.Color.from_str("#9C59D1"))
        kwargs.setdefault("title", "Prolactin Level Conversions")
        super().__init__(**kwargs)
