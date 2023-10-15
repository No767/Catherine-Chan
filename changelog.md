# ✨ Catherine-Chan 0.4.0

This should be one of the last versions (before the topgg stuff gets included) going into prod before the topgg release. This release aims to fix a ton of issues, and brings in several new features.

## ✨ TD;LR

- Completely reworked tonetags module
- HRT converter
- Use Pyright style of public exports for all packages

## 🛠️ Changes

- Restate usage of code
- Fixed errors related to no tonetags
- Moved error handling to on the `CommandTree` directly
- Move all views (except one) and all modals to `CatherineView` and `CatherineModal`, which are subclasses of `discord.ui.View` and `discord.ui.Modal` respectively. (this reduces on code duplication)
- Use Pyright style of public exports for all packages
- Fix `/tonetags all` json encoding and pretty print for json

## ✨ Additions

- HRT Converter
- Checks for invalid pronouns examples
- Checks for invalid tonetag names
- Subclassed views and modals
- Expose some more metrics


## ➖ Removals

- Error Handler cog. Moved to `CatherineCommandTree`
