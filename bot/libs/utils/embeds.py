import traceback

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
        self.set_footer(text="Happened At")
        self.timestamp = discord.utils.utcnow()


class FullErrorEmbed(ErrorEmbed):
    def __init__(self, error: Exception, **kwargs):
        kwargs.setdefault("description", self._format_description(error))
        super().__init__(**kwargs)

    def _format_description(self, error: Exception) -> str:
        error_traceback = "\n".join(traceback.format_exception_only(type(error), error))
        desc = f"""
        Uh oh! It seems like the command ran into an issue! For support, please visit [Catherine-Chan's Support Server](https://discord.gg/ns3e74frqn) to get help!
        
        **Error**:
        ```{error_traceback}```
        """
        return desc


class TimeoutEmbed(discord.Embed):
    """Timed out embed"""

    def __init__(self, **kwargs):
        kwargs.setdefault("color", discord.Color.from_rgb(214, 6, 6))
        kwargs.setdefault("title", "\U00002757 Timed Out")
        kwargs.setdefault(
            "description", "Timed out waiting for a response. Cancelling action."
        )
        super().__init__(**kwargs)


class ConfirmEmbed(discord.Embed):
    """Kumiko's custom confirm embed"""

    def __init__(self, **kwargs):
        kwargs.setdefault("color", discord.Color.from_rgb(255, 191, 0))
        kwargs.setdefault("title", "Are you sure?")
        super().__init__(**kwargs)
