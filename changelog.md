# :tada: Catherine-Chan 0.1.1 :tada:

**Note**: The full changelog will be kept the same, but all this release does is to fix the release workflows.

The first stable version of Catherine-Chan. As of now, the codebase is extremely stable, and pretty much replaces Jade's PrideBot. This version rebuilds the whole entire bot using discord.py and all of the internals now use PostgreSQL. There are still features that are planned to be included by as of now, this version pretty much mimics PrideBot.

Since this a full re-implementation, the rest of this section will be the differences included from PrideBot. Again, the changelog doesn't cover every single change I made since there is a ton.

## ✨ TD;LR

- Fixes some release stuff.
- Reimplement everything that PrideBot has to offer to PostgreSQL (massive performance boost w/ asyncpg)
- Better interfaces for all of the commands
- The first version that pretty much has everything PrideBot has
- Pronouns tester command now relies on a `re.compile()` and a one-pass Regex implementation instead of 5 `.replace()` methods chained together

## 🛠️ Changes

- Proper documentation, including a full online docs
- PEP8 standardized code (unlike Jade's version, which is a mess of personal preferences and poor design) enforced by Ruff
- Pronouns tester command now relies on a one-pass regex sub implementation. This essentially removes the need to use `.replace()` a bunch of times. The implementation can be found [here](https://github.com/No767/Catherine-Chan/blob/main/bot/libs/cog_utils/pronouns/__init__.py#L48-L50).
- Now based on PostgreSQL (asyncpg) instead of MongoDB (pymongo)

## ✨ Additions

- Discord support server link and shilling
- Global error handler
- Dockerfile that actually works
- Proper CI/CD pipeline for unit testing, and linting code
- Proper docstrings instead of random strings
- Full unit tests (100% coverage!)
- Pronouns examples approval system
- Tone Tags support
- SonarCloud linting
- Pride Profiles
- Load ENVs based on Dev mode and production.

## ➖ Removals

- MongoDB support
- Random commands that don't work anymore
- Dictionary system (replaced with pronouns.pages support instead)
- And a ton of bad practices that were in PrideBot