# :sparkles: Catherine-Chan 0.2.0 :sparkles:

This release focuses on implementing the blacklisting system, as well patching up old parts of the code to be ready for production use.

## ✨ TD;LR

- Blacklist system - If you are on it, you effectively cannot even use the bot

## 🛠️ Changes

- Moved the informative pronouns commands into a separate `dictionary` group. (Makes more sense bc they fetch from a dict anyways)
- Updated doc requirements.txt
- Update release workflows to hopefully work better now
- Align code to best practices

## ✨ Additions

- Added IPC (using `discord-ext-ipcx`) in order to provide healthchecks
- Added Blacklisting system
- New `dictionary` cog

## ➖ Removals

-  None
