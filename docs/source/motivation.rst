Motivation
==========

This page details the motivation on why I decided to build this bot. 

One of the reasons why I wanted to build this bot is seeing the lack of active LGBTQ+ focused bots. The biggest one I could find was Jade's `PrideBot <https://top.gg/bot/1066641327116255333>`_, which is currently down and has message contents issues. (gotta get that approved). And when looking up at pride bots, they all pretty much do exactly the same thing. I wanted a bot that would be useful just like Akari and Kumiko, and also be up with the latest Discord technologies and features (and general tech as well). Thus, Catherine-Chan was born. 

The goal of Catherine-Chan is to completely replace Jade's `PrideBot <https://top.gg/bot/1066641327116255333>`_ (don't think about inviting it bc it's down and has message content issues. pretty sure there are no plans to revive the bot). So, why try to replace PrideBot? I'll address my grievances in the next section.

Grievances of PrideBot
^^^^^^^^^^^^^^^^^^^^^^

**td;lr: Use Catherine-Chan instead of PrideBot bc Catherine-Chan completely outperforms PrideBot in every way possible, and is also generally more user friendly.**

Upon reviewing the codebase of PrideBot, I found plenty of bad practices, poor programming techniques, and a very poorly maintained codebase. No documentation, just the source code. That's fine, and some libraries like ``asqlite`` don't have proper documentation. But with that bot in 100 servers, I felt like I needed to make one that would outshine PrideBot.

With PrideBot, there was multiple severe and problematic approaches to how the bot works. Here are the problematic reasoning for why PrideBot really is not the best choice for a bot:

1. **PrideBot uses MongoDB**

Fundamentally PrideBot uses MongoDB (with pymongo) for the database. To me, that's an extremely bad choice. Why? See this reasoning made by dauds on the discord.py server:

    "MongoDB is a NoSQL database that stores data as documents in BSON format. Not recommended in general as most of Discord data you are storing is relational (e.g. economy things) while mongodb is for non-relational data, hence there is no reason to use NoSQL over SQL to store relational data." - dauds

In this case, data **is** relational. One user can have one pride profile, have multiple suggestions for the pronouns tester, and own multiple tonetags. In fact, with Catherine-Chan, it's mapped out exactly like this.

2. **PrideBot uses pymongo**

The major issue is that Jade, the creator of PrideBot, uses PyMongo. Pymongo works fine for using Mongo for **regular synchronous** Python applications, but for async ones, this causes something called "blocking". Now, you may be wondering: What does blocking mean? For context, Python functions are ran one by one. If there is something that Function A is doing, Function B has to wait. In terms of async, when Function A just starting doing something, Function B already is working on something else. This is the basics of AsyncIO. In order to achieve asyncio, there needs to be something called the `event loop <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Event_loop>`_. When you run synchronous code, it blocks the event loop, which prevents your async functions from working. And when you spend time running queries for pymongo, **you block your whole entire bot from running**. Which essentially renders your bot useless.

Oh also PyMongo quite literally has `connection pooling set up on each client <https://pymongo.readthedocs.io/en/stable/faq.html#how-does-connection-pooling-work-in-pymongo>`_. So you are just constantly making connections and then closing them rapidly, and sometimes multiple can be created from one command. Over and over again. And sometimes 2 or more times per command!

3. **Lack of PEP8 standards and poor code**

Jade is known to quite literally avoid PEP8 standards and do it her way because it's a "preference". In terms of a bot like this, where people aren't going to look through the source code, it's fine. But what happens is if you have other people looking through your work in order to learn (maybe bc the pridebot is their favorite or something), you end up setting a bad example for others. These people won't know what is good and bad within the Python community, so they will just copy it and when they now want to contribute to other projects, more than likely folk will go ahead and tell you to use PEP8 as the standard instead. This gets even worse if you are working as a team.

Not only a lack of standards enables that, but the code is written extremely poorly. No standards, and full of bad practices. Let's take `this one <https://github.com/LilbabxJJ-1/PrideBot/blob/master/commands/support.py#L3>`_ for example:

.. code-block:: Python

    from tokens import *

Like ok what is even the ``tokens`` package? What is it importing? In general, it's bad practice and worse of all, it completely pollutes the namespace of your file now. The imported functions from ``tokens`` may conflict with the functions with the same name, which means you end up shadowing variables, functions, etc.

Let's also take this `section of code <https://github.com/LilbabxJJ-1/PrideBot/blob/master/main.py#L19C1-L36C60>`_ for example:

.. code-block:: python

    @bot.event
    async def on_interaction(interaction):
        count = profiles.find_one({"_id": "total_commands"})
        if count is None:
            new = {
                "_id": "total_commands",
                "Count": 0
            }
            profiles.insert_one(new)
        else:
            profiles.update_one({"_id": "total_commands"}, {"$set": {"Count": count["Count"] + 1}})
        users = banned.find_one({"get": "get"})
        for i in users["Banned"]:
            if interaction.user.id == i:
                await interaction.channel.send("You have been banned from using this bot\nTo dispute this, join the support server")
                return
        else:
            await bot.process_application_commands(interaction)

This is the blacklisting system. ``profiles.find_one({"_id": "total_commands"})`` is straight up blocking code. And generally there are better ways to handle this. The code in general is extremely bad and was a nightmare for me to even figure out. The reason why it's so problematic is that this is being ran on **every single interaction**. So whenever you press a button, that piece of blocking code is being ran. When you scale this up to production, you will have multiple if not more than 10+ people using your bot at once, which is so important that heavy I/O or CPU operations be done async.

Now comparing it to Catherine-Chan's blacklisting system:

``catherinecore.py``

.. code-block:: python

    class CatherineCommandTree(CommandTree):
        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            bot: Catherine = interaction.client  # type: ignore
            if (
                bot.owner_id == interaction.user.id
                or bot.application_id == interaction.user.id
            ):
                return True

            blacklisted_status = await get_or_fetch_blacklist(
                bot, interaction.user.id, bot.pool
            )
            if blacklisted_status is True:
                await interaction.response.send_message(
                    f"My fellow user, {interaction.user.mention}, you are blacklisted."
                )
                return False
            return True

``libs/utils/blacklist.py``

.. code-block:: python

    async def get_or_fetch_blacklist(bot, id: int, pool: asyncpg.Pool) -> bool:
        """Gets or fetches a user's blacklist status

        Args:
            bot (Catherine): The bot instance
            id (int): The user's ID
            pool (asyncpg.Pool): A global connection pool

        Returns:
            bool: The user's blacklist status
        """
        if id in bot.blacklist_cache:
            return bot.blacklist_cache[id]

        query = """
        SELECT blacklist_status
        FROM blacklist
        WHERE id = $1;
        """
        record = await pool.fetchrow(query, id)
        if record is None:
            return False
        bot.blacklist_cache[id] = record["blacklist_status"]
        return record["blacklist_status"]

Catherine-Chan's blacklisting system takes a bit to explain, but it's fairly standard. Within the setup hook, the code queries the PostgreSQL database for the blacklisted users and guilds. This is then converted into a dict, which is assigned to a private attribute within ``Catherine``. The attribute can be only accessed through a property (which later may or may be cached for faster performance), and that essentially gives us a read-only 1:1 mapping of the data from the database. The data will always be guaranteed 1:1 as the cache is always updated. During the ``interaction_check`` in the subclassed ``CommandTree``, the code looks up the user on the blacklist cache, and if not found, pulls it from the database and updates the cache wth the data (in fact, most if not all of Kumiko's ``get_or_fetch*`` coroutines work like this). The code only reads from the cache, thus when checking if the user is blacklisted or not, the operation is extremely quick and has no performance impacts on the bot.


4. **Catherine-Chan vs PrideBot**

Now on to the last part: comparing the both of them. Here's a table comparing the both of them:

+------------------------+----------------+----------+
| Info / Questions       | Catherine-Chan | PrideBot |
+========================+================+==========+
| Discord Framework      | discord.py     | Pycord   |
+------------------------+----------------+----------+
| Framework Version      | v2.3.2 (v0.2.x)| Unknown  |
+------------------------+----------------+----------+
| Memory Usage           | 66MB (v0.2.x)  | Unknown  |
+------------------------+----------------+----------+
| Database               | PostgreSQL     | MongoDB  |
+------------------------+----------------+----------+
| Database Driver        | asyncpg        | pymongo  |
+------------------------+----------------+----------+
| Documented (code)?     | Mostly         | None     |
+------------------------+----------------+----------+
| Documented (features)? | Mostly         | Mostly   |
+------------------------+----------------+----------+
| Uvloop accelerated?    | Yes            | No       |
+------------------------+----------------+----------+
| Prefix                 | ``/``          | ``/``    |
+------------------------+----------------+----------+
| Best Practices?        | Yes            | No       |
+------------------------+----------------+----------+

Generally, Catherine-Chan outperforms PrideBot on most parts. Thus you should probably want to use Catherine-Chan.