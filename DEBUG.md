# Debug Environment Variables

Globally, setting `DEBUG=1` will set the logging level to DEBUG.

## `--download`

### FORCE_SNAPSHOT

You can choose the exact Wiktionary dump to download by using `FORCE_SNAPSHOT=YYYYMMDD`.

## `--get-word`

### NO_COLORS

Setting `NO_COLORS=1` will remove all markup styling (italic, bold, etc.).

### KEEP_UNFINISHED

When an error happens in transforming/expanding a definition, the definition will be skipped (not the entire word, just the definition).
Re-run the command prepending `KEEP_UNFINISHED=1` to display the raw HTML, and be able to see where the issue comes from.

## `--parse`

Lst all words not taken into account with current head sections:

```shell
DEBUG_PARSE=1 python -m wikidict LOCALE --parse >out.log
```

## `--render`

### DEBUG_SECTIONS

Lst all unhandled sections:

```shell
DEBUG_SECTIONS=1 python -m wikidict LOCALE --render | sort -u >out.log
```

Make words under a given section to fail:

```shell
DEBUG_SECTIONS="<section>" python -m wikidict LOCALE --render
```

Example with the RO dictionary, and the "{{unități}}" section:

```shell
DEBUG_SECTIONS='{{unități}}' python -m wikidict ro --render
```

### DEBUG_EMPTY_WORDS

List all unhandled words:

```shell
DEBUG_EMPTY_WORDS=1 python -m wikidict LOCALE --render >out.log 2>&1
```

### DEBUG_LUA

Useful to debug Lua expansion issues.

For example, to log all words for each process in order to be able to catch problematic words in a second time (mostly to catch infinite loops):

```shell
DEBUG_LUA=1 python -m wikidict LOCALE --render > LOG_FILE 2>&1
tail -f LOG_FILE
# (and when the ouput hangs, hit CTRL+C, multiple times if needed)
python log-analyzer.py LOG_FILE
```

If more details are needed, use `DEBUG_LUA=2` to print Lua errors in real time.

## `--show-pos`

### DEBUG_POS

This is useful to list all found part of speech (POS). To be used after `--render` to have the full dictionary ready to be analyzed.
