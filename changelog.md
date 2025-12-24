## Catherine-Chan [1.1.0](https://github.com/No767/Catherine-Chan/tree/1.1.0) - 2025-12-24

### Bug fixes

- Explictly prevent bad actors by checking origin metadata ([#263](https://github.com/No767/Catherine/issues/263))

### Features

- Prepare for SQL deployment by migrating from `SERIAL` to `IDENTITY` columns and upgrade PostgreSQL from 17 to 18 ([#258](https://github.com/No767/Catherine/issues/258))
- Handle cases of writes with systemd and ensuring functionality works ([#261](https://github.com/No767/Catherine/issues/261))
- Handle prefix-based errors ([#262](https://github.com/No767/Catherine/issues/262))

### Removals and backward incompatible breaking changes

- Modernize and restructure codebase (does not affect user behavior, but only developer experience) ([#250](https://github.com/No767/Catherine/issues/250))

### Improved documentation

- Modernize and reorganize docs ([#252](https://github.com/No767/Catherine/issues/252))

### Miscellaneous internal changes

- Fix auto-approve workflow by providing `secrets.GITHUB_TOKEN` ([#253](https://github.com/No767/Catherine/issues/253))
- Add custom action to process changelogs for release ([#254](https://github.com/No767/Catherine/issues/254))
- Properly ensure dependency caches are utilized in workflows ([#255](https://github.com/No767/Catherine/issues/255))
- Add, adapt to hardened systemd service configuration, and compress rotated logs using `gzip` or `zstd` ([#257](https://github.com/No767/Catherine/issues/257))
- Disable caching dependencies in workflows ([#259](https://github.com/No767/Catherine/issues/259))
- Reflect supported Python versions in `README.md` ([#260](https://github.com/No767/Catherine/issues/260))
