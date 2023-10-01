Motivation
==========

This page details the motivation on why I decided to build this bot. 

One of the reasons why I wanted to build this bot is seeing the lack of active LGBTQ+ focused bots. 
The biggest one I could find was Jade's `PrideBot <https://top.gg/bot/1066641327116255333>`_, which is currently down and has message contents issues. (gotta get that approved). 
And when looking up at pride bots, they all pretty much do exactly the same thing. I wanted a bot that would be useful 
just like Akari and Kumiko, and also be up with the latest Discord technologies and features (and general tech as well). Thus, Catherine-Chan was born. 

The goal of Catherine-Chan is to completely replace Jade's PrideBot. So, why try to replace PrideBot? I'll address my grievances in the next section.

Grievances of PrideBot
^^^^^^^^^^^^^^^^^^^^^^

**td;lr: Use Catherine-Chan instead of PrideBot bc Catherine-Chan completely outperforms PrideBot in every way possible, and is also generally more user friendly.**

Upon reviewing the codebase of PrideBot, I found plenty of bad practices, poor programming techniques, and a very poorly maintained codebase. No documentation, just the source code. 
That's fine, and some libraries like ``asqlite`` don't have proper documentation. But with that bot in 100 servers, I felt like I needed to make one that would outshine PrideBot.

With PrideBot, there was multiple severe and problematic approaches to how the bot works. Here are the problematic reasoning for why PrideBot really is not the best choice for a bot:

Database Choices
^^^^^^^^^^^^^^^^

Fundamentally PrideBot uses MongoDB (with pymongo) for the database. To me, that's an extremely bad choice. Why? See this reasoning made by dauds on the discord.py server:

    "MongoDB is a NoSQL database that stores data as documents in BSON format. Not recommended in general as most of Discord data you are storing is relational 
    (e.g. economy things) while mongodb is for non-relational data, hence there is no reason to use NoSQL over SQL to store relational data." - dauds

In this case, data **is** relational. One user can have one pride profile, have multiple suggestions for the pronouns tester, and own multiple tonetags. 
In fact, with Catherine-Chan, it's mapped out exactly like this. But what's even more pressing is the driver itself that is used.

The Use of Pymongo in an async context
--------------------------------------

The major issue is that Jade, the creator of PrideBot, uses PyMongo. 
Pymongo works fine for using Mongo for **regular synchronous** Python applications, 
but for async ones, this causes something called "blocking". 
Now, you may be wondering: What does blocking mean? For context, Python functions are ran one by one. 
If there is something that Function A is doing, Function B has to wait. 
In terms of async, when Function A just starting doing something, Function B already is working on something else. 
This is the basics of AsyncIO. In order to achieve asyncio, there needs to be something called the `event loop <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Event_loop>`_. 
When you run synchronous code, it blocks the event loop, which prevents your async functions from working. 
And when you spend time running queries for pymongo, **you block your whole entire bot from running**. Which essentially renders your bot useless.
To compound this, on **every single command**, short-lived connections backed only by 1 connection are made. This introduces a ton of overhead performances, 
therefore slowing down the bot heavily.

.. note:: 

    FastAPI has a section on the gist of concurrency using asyncio, and it's a good read. 
    Although it's made for FastAPI, the ideas are exactly the same for discord.py.
    You can find it `here <https://fastapi.tiangolo.com/async/>`_. 

Overloading the Database
------------------------

The idea of connection pooling is to maintain a queue or pool of ready-to-go connections that can be acquired, and released once done.
Now what's the benefits of doing this? Massive performance gains, reduced overhead performance, and reduced quick short-lived connections.
Connection pooling is also able to reduce latency as well. In the case of PyMongo, 
it's handled automatically `every single time you make a new client <https://pymongo.readthedocs.io/en/stable/faq.html#how-does-connection-pooling-work-in-pymongo>`_.

This is compounded by the fact that on every single command, these connection pools are rapidly created and discarded. Sometimes 2 to 3 connection pools are set up on **every single command**.

Scaling MongoDB
---------------

My theory behind the decision to use MongoDB boils down to MongoDB's ability to cluster and shard databases.
MongoDB is extremely good when it comes to schema-less data and at insane volumes of it. But PostgreSQL can effectively do the same.
`CockroachDB <https://www.cockroachlabs.com/>`_ exists as an SQL RDBMS that has the ability to scale to massive workloads.
`Citus <https://www.citusdata.com/>`_ exists as a PostgreSQL extension that allows PosgreSQL to completely scale to massive industrial workloads and with clustering as well.
Both of these options are used widely in industry and by Fortune 100 companies, with `CitusData being acquired by Microsoft <https://www.citusdata.com/blog/2019/01/24/microsoft-acquires-citus-data/>`_ 
and used internally in Microsoft Azure.

But in the context of a discord bot, PrideBot only managed to reach to 100 serves before being shut down. With the data created, 
it's something that even a single Postgres server will be able to handle. 
PostgreSQL can handle up to thousands of concurrent connections all happening at once. 
For instance, R. Danny, a bot that is in 9,000+ servers and used extremely actively by millions of users uses just one PostgreSQL server.

Enforcing the Lack of Code Standards
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Jade is known to quite literally avoid PEP8 standards and do it her way because it's a "preference". 
In terms of a bot like this, where people aren't going to look through the source code, it's fine. 
But what happens is if you have other people looking through your work in order to learn (maybe bc the pridebot is their favorite or something), you end up setting a bad example for others. 
These people won't know what is good and bad within the Python community, so they will just copy it and when they now want to contribute to other projects, 
more than likely folk will go ahead and tell you to use PEP8 as the standard instead. This gets even worse if you are working as a team. 
These are usually picked up from Youtube tutorials to spew bad practices everywhere, and users learning from them don't know better.

Not only a lack of standards enables that, but the code is written extremely poorly. No standards, and full of bad practices. 
Let's take `this one <https://github.com/LilbabxJJ-1/PrideBot/blob/master/commands/support.py#L3>`_ for example:


.. code-block:: Python

    from tokens import *

Like ok what is even the ``tokens`` package? What is it importing? In general, it's bad practice and worse of all, it completely pollutes the namespace of your file now. 
The imported functions from ``tokens`` may conflict with the functions with the same name, which means you end up shadowing variables, functions, etc. 
In retrospect, this is one of the ways taught by poor programmers to import and store your tokens.  

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

This is the blacklisting system. ``profiles.find_one({"_id": "total_commands"})`` is straight up blocking code. 
The reason why it's so problematic is that this is being ran on **every single interaction**. 
So whenever you press a button, that piece of blocking code is being ran. When you scale this up to production, 
you will have multiple if not more than 10+ people using your bot at once, 
which is so important that heavy I/O or CPU operations be done async.

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

Catherine-Chan's blacklisting system takes a bit to explain, but it's fairly standard. 
Within the setup hook, the code queries the PostgreSQL database for the blacklisted users and guilds. 
This is then converted into a ``Dict[int, bool]``, which is assigned to a private attribute within ``Catherine``. 
The attribute can be only accessed through a property (which later may or may be cached for faster performance), 
and that essentially gives us a read-only 1:1 mapping of the data from the database. 
he data will always be guaranteed 1:1 as the cache is always updated. 
During the ``interaction_check`` in the subclassed ``CommandTree``, the code looks up the user on the blacklist cache, 
and if not found, pulls it from the database and updates the cache wth the data (in fact, most if not all of Kumiko's ``get_or_fetch*`` coroutines work like this). 
The code only reads from the cache, thus when checking if the user is blacklisted or not, the operation is extremely quick and has no performance impacts on the bot.

Design Decisions
^^^^^^^^^^^^^^^^

The design decision between Catherine-Chan and PrideBot are radically different.
Catherine-Chan was the innovation of 2 years of discord bot development, 
and spearheads on all of the design choices that I have learned from the community on the discord.py server and others.
It's also a cumulation of the designs I've picked up while working on Kumiko, Akari, Xelt, and others.

Pronouns Testing Module Design Decisions
----------------------------------------

One of the most evident is with the pronouns testing command. 
When it comes to this module, there are two major parts: Suggesting new examples and making them. 
Let's take a look at how both bots do it.

PrideBot's approach (`source here <https://github.com/LilbabxJJ-1/PrideBot/blob/master/commands/pronouns.py>`_):

Suggesting the examples

.. code-block:: python3

    @commands.slash_command(name="suggest-pronouns")
    async def suggestPronouns(self, ctx, sentence: discord.Option(description="A sentence that can be used to test pronouns")):
        """Suggest sentences we can use for the /testpronouns command"""
        embed = discord.Embed(title="Pronoun Sentence",
                              description=sentence,
                              color=0xA020F0)
        channel = await self.bot.fetch_channel(991806371815243836)
        await channel.send(embed=embed)
        await ctx.respond("Successfully submitted suggestion")
        return


Displaying a full example:

.. code-block:: python3

    @commands.slash_command(name="test-pronouns")
    async def testpronouns(self, ctx, name: discord.Option(description="Your name"), subjective_pronoun: discord.Option(description="Example: They | He | She"), objective_pronoun: discord.Option(description="Example: Them | Him | Her "), possessive_determiner: discord.Option(description="Example: Their | His | Her"),
                           possesive_pronoun: discord.Option(description="Example: Theirs | His | Hers"), reflective_pronoun: discord.Option(description="Example: Themself | Himself | Herself")):
        """Test out your pronouns! More pronoun slots soon"""
        send = random.choice(sentences).replace("NAME", name).replace("SUBJECT", subjective_pronoun).replace("PP", possesive_pronoun).replace("OBJECTIVE", objective_pronoun).replace("REFLECT", reflective_pronoun).replace("PD", possessive_determiner)
        embed = discord.Embed(title="Try out your pronouns!",
                              description=send,
                              color=0xA020F0)
        await ctx.respond(embed=embed)
        #await ctx.send("These may come out as incorrect grammatically since this is still very new")
        return

So let's analyze the decisions made. With PrideBot, the idea when it came to suggesting new ones was simple to only log them. 
In fact, you **can't** even suggest them as these are all hard-coded.
When it come to displaying them, each hard-coded sentence is replaced with the user's input. 
Variables in the form of uppercase words (for example, replacing with the given name denotes the variable ``NAME``).
And 6 ``.replace`` methods chained together are used to substitute the variables. The major issue with this design can be summarized as the following:

1. You can't even suggest examples as they are hard-coded.
2. You are met with 6 different options that needs to be filled out in order to run the command.


Catherine-Chan's Approach for testing pronouns (`source linked here <https://github.com/No767/Catherine-Chan/blob/main/bot/cogs/pronouns.py>`_):

Since the code for suggesting examples is extremely complicated, it can be found within the GitHub repo.

``bot/cogs/pronouns.py`` (Command to test pronouns)

.. code-block:: python3

    @app_commands.command(name="test")
    @app_commands.describe(
        name="The name to use in the sentence. This could be your own name or someone else's name"
    )
    async def test(self, interaction: discord.Interaction, name: str) -> None:
        """Basically a pronouns tester command"""
        # Based off of this query: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/tags.py#L182-L191
        query = """
        SELECT sentence
        FROM pronouns_examples
        OFFSET FLOOR(RANDOM() * (
            SELECT COUNT(*)
            FROM pronouns_examples
            WHERE approved = True
        ))
        LIMIT 1;
        """
        value = await self.pool.fetchval(query)
        if value is None:
            await interaction.response.send_message("Can't find any examples")
            return
        await interaction.response.send_modal(PronounsTesterModal(value, name))


``bot/libs/ui/pronouns/modals.py`` (Modal shown to input pronoun fields)

.. code-block:: python3

    import discord
    from libs.cog_utils.pronouns import (
        convert_to_proper_name,
        convert_to_proper_sentence,
        parse_pronouns_sentence,
    )


    class PronounsTesterModal(discord.ui.Modal, title="Input the fields"):
        def __init__(self, sentence: str, name: str):
            super().__init__()
            self.sentence = sentence
            self.name = name
            self.sp = discord.ui.TextInput(
                label="Subjective Pronoun", placeholder="Example: They | He | She"
            )
            self.op = discord.ui.TextInput(
                label="Objective Pronoun", placeholder="Example: Them | Him | Her "
            )
            self.pd = discord.ui.TextInput(
                label="Possessive Determiner", placeholder="Example: Their | His | Her"
            )
            self.pp = discord.ui.TextInput(
                label="Possessive Pronoun", placeholder="Example: Theirs | His | Hers"
            )
            self.rp = discord.ui.TextInput(
                label="Reflective Pronoun",
                placeholder="Example: Themselves | Himself | Herself",
            )

            self.add_item(self.sp)
            self.add_item(self.op)
            self.add_item(self.pd)
            self.add_item(self.pp)
            self.add_item(self.rp)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            # The new Regex-based solution to the pronouns tester command
            # Original: https://github.com/LilbabxJJ-1/PrideBot/blob/master/commands/pronouns.py#L15
            replacements = {
                "$subjective_pronoun": self.sp.value.lower(),
                "$objective_pronoun": self.op.value.lower(),
                "$possessive_pronoun": self.pp.value.lower(),
                "$possessive_determiner": self.pd.value.lower(),
                "$reflective_pronoun": self.rp.value.lower(),
                "$name": convert_to_proper_name(self.name),
            }
            parsed_sentence = parse_pronouns_sentence(replacements, self.sentence)
            complete_sentence = convert_to_proper_sentence(parsed_sentence)
            await interaction.response.send_message(complete_sentence)

``bot/libs/cog_utils/pronouns/__init__.py`` (utils to help with testing pronouns)

.. code-block:: python3

    import re
    from typing import Dict, List, Union

    # Thank you stack overflow
    # code comes from this: https://stackoverflow.com/a/15175239/16526522
    def parse_pronouns_sentence(replacements: Dict[str, str], sentence: str) -> str:
        regex = re.compile("(%s[s]?)" % "|".join(map(re.escape, replacements.keys())))
        return regex.sub(lambda mo: replacements[mo.group()], sentence)


    def convert_to_proper_sentence(sentence: str) -> str:
        regex = re.compile(r"((?<=[\.\?!]\s)(\w+)|(^\w+))")

        def cap(match: re.Match):
            return match.group().capitalize()

        return regex.sub(cap, sentence)


    def convert_to_proper_name(name: str) -> str:
        regex = re.compile("[^()0-9-]+")
        possible_match = regex.fullmatch(name)

        if possible_match is None:
            # If we didn't match any possible names, throw back the original name
            # Most of the times it will be improper, so we might as well just return the improper name so it does't just say None
            return name

        parsed_str = " ".join(
            word.title() if not word[0].isdigit() else word
            for word in possible_match.group().split()
        )
        return parsed_str

So what does this code exactly do? There are 3 main parts to this:

1. Obtaining the sentence with variables to substitute
2. Substituting the given pronouns and fields with ones inputted by the use
3. Cleaning up the final sentence

The first part is the easiest to understand. 
Instead of running the SQL query within the callback of the modal, we first pull it from the database.
This may seem odd to do, but it's better to have the example ready to go instead of pulling it within the callback of a modal,
since we also need to sub the pronouns in. Once we have it, the fields are in an dict 
where the keys are the variables we want to substitute out, and the values being what we want to substitute with.
The implementation uses Regex, and compiles a massive regex string which groups them together. From there,
we basically loop over the dict, and replace the variables. The last part is to clean it up. 
A sentence may end up looking like this: ``noelle is cute, isn't she?``. But we want it to be grammatically correct.
So we pass it to another function, which will smartly capitalize the sentence (so it becomes ``Noelle is cute, isn't she?``) instead. 
In cases where the name isn't the first word, the name is also passed through a regex which first detects if it's a name or not. If yes,
it will format it to a working name. If it's not, it will just return the original name (to prevent ``None`` from showing up). And
lastly we throw the cleaned sentence back at the user.

In Comparison to Catherine-Chan
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now on to the last part: comparing the both of them. Here's a table comparing the both of them:

+------------------------+----------------+----------+
| Info / Questions       | Catherine-Chan | PrideBot |
+========================+================+==========+
| Discord Framework      | discord.py     | Pycord   |
+------------------------+----------------+----------+
| Framework Version      | v2.3.2 (v0.2.x)| Unknown  |
+------------------------+----------------+----------+
| Memory Usage           | 75MB (v0.2.8)  | Unknown  |
+------------------------+----------------+----------+
| Database               | PostgreSQL     | MongoDB  |
+------------------------+----------------+----------+
| Database Driver        | asyncpg        | pymongo  |
+------------------------+----------------+----------+
| Documented (code)?     | Somewhat       | None     |
+------------------------+----------------+----------+
| Documented (features)? | Mostly         | Mostly   |
+------------------------+----------------+----------+
| Unit Tests?            | Yes (100%)     | No (0%)  |
+------------------------+----------------+----------+
| Uvloop accelerated?    | Yes            | No       |
+------------------------+----------------+----------+
| Prefix                 | ``/``          | ``/``    |
+------------------------+----------------+----------+
| Best Practices?        | Yes            | No       |
+------------------------+----------------+----------+

Generally, Catherine-Chan outperforms PrideBot on most parts. Thus you should probably want to use Catherine-Chan.