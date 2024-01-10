QOL and bug-fixing update. See below for details

## ✨ TD;LR

- Fixed unknown messages for timeout views
- Fixed registering for pride profiles and deletion

## 🛠️ Changes

- Require searching up using global usernames instead for pride profiles
- Account for pronouns in dictionary commands
- Removed button prompt for `/pride-profiles register`
- Improved deletion prompts for `/pride-profiles delete` and `/tonetags delete`
- Implement merged deletion backend for `/tonetags delete` and `/tonetags delete-id`

## ✨ Additions

- Improved cog reloader
- Nanika's signal handlers

## ➖ Removals

- `cysystemd` (causing duplicate logs)