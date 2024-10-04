Entire rewrite of core components of Catherine-Chan

> [!CAUTION]
> This release essentially is a rewrite. Stuff **will** break, and changes are not finalized.
> If you run into any issues, feel free to submit a GitHub issues report.

## ✨ TD;LR

- Entirely rewrote core components of the codebase (See below for further information)

## 🛠️ Changes

- Upgraded discord.py to v2.4.0 (https://github.com/No767/Catherine-Chan/pull/184)
- New requirements.txt for dependencies (https://github.com/No767/Catherine-Chan/pull/173)
- Fixed pygit2 deprecations (https://github.com/No767/Catherine-Chan/pull/176)
- Fixed inaccurate member counts with Prometheus (https://github.com/No767/Catherine-Chan/pull/181)
- General codebase maintenance (https://github.com/No767/Catherine-Chan/pull/204)

## ✨ Additions

- Rewrote:
  - Unit tests (https://github.com/No767/Catherine-Chan/pull/18)
  - Prometheus exporter (https://github.com/No767/Catherine-Chan/pull/170, https://github.com/No767/Catherine-Chan/pull/178)
  - Docker support (https://github.com/No767/Catherine-Chan/pull/197)
  - Blacklist (https://github.com/No767/Catherine-Chan/pull/185)
  - Error Handlers (https://github.com/No767/Catherine-Chan/pull/188)
  - Database migrations (https://github.com/No767/Catherine-Chan/pull/180)
  - Pride Profiles (https://github.com/No767/Catherine-Chan/pull/198)
  - HRT Conversion (https://github.com/No767/Catherine-Chan/pull/200)
  - Pronouns (https://github.com/No767/Catherine-Chan/pull/207)
- Include Taskfile (https://github.com/No767/Catherine-Chan/pull/208)

## ➖ Removals

- Tonetags (https://github.com/No767/Catherine-Chan/pull/183)
