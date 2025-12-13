from typing import Any

from discord.ext import menus

from .paginator import CatherinePages


class SimplePageSource(menus.ListPageSource):
    async def format_page(self, menu: CatherinePages, page: Any):
        pages = []
        for index, entry in enumerate(page, start=menu.current_page * self.per_page):
            pages.append(f"{index + 1}. {entry}")

        maximum = self.get_max_pages()
        if maximum > 1:
            footer = (
                f"Page {menu.current_page + 1}/{maximum} ({len(self.entries)} entries)"
            )
            menu.embed.set_footer(text=footer)

        menu.embed.description = "\n".join(pages)
        return menu.embed
