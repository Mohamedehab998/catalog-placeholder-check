# Catalog Placeholder Check

Compare two UTF-8 JSON translation catalogs to catch a missing key or a changed placeholder before the application formats the translated message. Works with flat JSON objects whose values are strings.

```json
{"cart.summary": "{name} has {count} items"}
```

A translation can freely reorder `{name}` and `{count}`. Removing, adding, or repeating a field changes the report. Escaped braces and one level of nested format fields are supported; duplicate JSON keys are rejected. The tool checks field names and counts, not whether a format spec is compatible with a runtime value. Use this with named Python format strings rather than ICU MessageFormat or positional placeholders.

```sh
python catalog_check.py en.json ar.json
python -m unittest -v
```

Python 3.10 or newer. No dependencies. JSON goes to stdout. Exit 0 means a match, 1 means there are findings, and 2 means the inputs could not be read or parsed. Licensed under 0BSD. Initial implementation prepared with assistance from OpenAI Codex.
