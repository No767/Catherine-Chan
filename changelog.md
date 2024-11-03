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
- General codebase maintenance (https://github.com/No767/Catherine-Chan/pull/204, https://github.com/No767/Catherine-Chan/pull/223)
- Migrated to Lefthook and optimized pre-commit hooks (https://github.com/No767/Catherine-Chan/pull/218)
- Use JSON decoder provided by msgspec (https://github.com/No767/Catherine-Chan/pull/222)
- Use proper type checking imports (https://github.com/No767/Catherine-Chan/pull/216)
- Fix exception violations with pronouns tester (https://github.com/No767/Catherine-Chan/pull/212)
- Migrate from Bandit, Black, Autoflake and Isort to Ruff (https://github.com/No767/Catherine-Chan/pull/218, https://github.com/No767/Catherine-Chan/pull/223)
- Prevent unsanitized queries from creating Cloudflare errors (https://github.com/No767/Catherine-Chan/pull/226, https://github.com/No767/Catherine-Chan/pull/227)

## ✨ Additions

- Rewrote:
  - Unit tests (https://github.com/No767/Catherine-Chan/pull/189)
  - Prometheus exporter (https://github.com/No767/Catherine-Chan/pull/170, https://github.com/No767/Catherine-Chan/pull/178)
  - Docker support (https://github.com/No767/Catherine-Chan/pull/197)
  - Blacklist (https://github.com/No767/Catherine-Chan/pull/185)
  - Error Handlers (https://github.com/No767/Catherine-Chan/pull/188)
  - Database migrations (https://github.com/No767/Catherine-Chan/pull/180)
  - Pride Profiles (https://github.com/No767/Catherine-Chan/pull/198)
  - HRT Conversion (https://github.com/No767/Catherine-Chan/pull/200)
  - Pronouns (https://github.com/No767/Catherine-Chan/pull/207)
  - Dictionary (https://github.com/No767/Catherine-Chan/pull/221)
  - Documentation (https://github.com/No767/Catherine-Chan/pull/224)
- Include Taskfile (https://github.com/No767/Catherine-Chan/pull/208)

## ➖ Removals

- Tonetags (https://github.com/No767/Catherine-Chan/pull/183)
- pre-commit (https://github.com/No767/Catherine-Chan/pull/218)
