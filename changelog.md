QOL changes with the dictionary commands, new HRT conversion commands and bug fixes

## ✨ TD;LR

- Properly applied markdown formatting for dictionary commands
- Re-wrote HRT conversion commands
- Proper bug fixes

## 🛠️ Changes

- Rewrite blacklist system to use an LRU cache (this provides a major speedup)
- Properly fix timeout errors with `CatherinePages` and `CatherineView`
- Rewrite dictionary commands with custom regex link formatter
- Load Jishaku in production (this allows for debug commands in production)
- Optionally provide a message response when a `CatherineView` times out (instead of just removing the view)
- Completely redo and retest HRT conversion commands
- Implement cog checks for dev tools cog
- Split HRT conversion commands into subcommands instead of one big command
- Fix a bug where the default unit to convert to had an 0.0 instead of the user given value
- Clean up `/about` command and include an "about me" description

## ✨ Additions

- Prolactin conversion
- Formatted dictionary entries

## ➖ Removals

- Old blacklist caches