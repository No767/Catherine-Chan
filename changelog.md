# Catherine-Chan 0.5.0

QOL-focused update improving and updating many aspects of Catherine-Chan.
Note that there is still one more bug in regards to the `/hrt-convert` command.

## ✨ TD;LR

- Windows support through Winloop
- Several bug fixes

## 🛠️ Changes

- Use mention as prefix (this gets around the issue of message contents intents)
- Migrate blacklist module to be prefixed (including custom paginator)
- Fix interaction paginator and view timeout issues
- Force separate creation of PostgreSQL role within PostgreSQL Dockerfile
- Enforce LRU cache on blacklist cache
- Improved Dockerfile and included `.dockerignore`

## ✨ Additions

- Semi-Windows support through Winloop
- Mention prefix instead of text-based
- Top.gg links

## ➖ Removals

- None
