# rg / ripgrep cheatsheet

Search **file contents** recursively. To find files and directories by name, use `fd` / `fdfind`.

Verified against local `ripgrep 15.2.0` help on 2026-10-20 (UTC).

## Syntax and defaults

```bash
rg [OPTIONS] PATTERN [FILE_OR_DIRECTORY ...]
rg [OPTIONS] -e PATTERN1 -e PATTERN2 [PATH ...]
rg [OPTIONS] -f PATTERN_FILE [PATH ...]
command | rg [OPTIONS] PATTERN
```

With no path, searches the current directory recursively (or stdin when piped).
Patterns are case-sensitive regular expressions by default. Hidden entries,
ignored entries, and binary data are normally excluded from ordinary recursive
text searches. Explicit file arguments can override traversal filters.
Quote patterns with single quotes to prevent shell expansion.

## Matching switches

| Switch | Purpose |
| --- | --- |
| `-F`, `--fixed-strings` | Treat patterns as literal strings. |
| `-i`, `--ignore-case` | Case-insensitive matching. |
| `-s`, `--case-sensitive` | Force case-sensitive matching. |
| `-S`, `--smart-case` | Ignore case unless a pattern contains uppercase. |
| `-w`, `--word-regexp` | Match whole words. |
| `-x`, `--line-regexp` | Match whole lines. |
| `-v`, `--invert-match` | Select lines that do not match. |
| `-e PATTERN`, `--regexp PATTERN` | Add a pattern; repeat for OR matching. |
| `-f FILE`, `--file FILE` | Read patterns, one per line; OR matching. |
| `-P`, `--pcre2` | Use PCRE2 for lookaround/backreferences, if supported by the build. |
| `-U`, `--multiline` | Allow matches across line boundaries. |
| `--multiline-dotall` | With multiline mode, let `.` match newlines. |

Default regex supports alternation, groups, classes, and repetition, but not
lookaround/backreferences. An empty line in a pattern file matches every line.

## Scope and input switches

| Switch | Purpose |
| --- | --- |
| `-g GLOB`, `--glob GLOB` | Include matching paths; `!GLOB` excludes. Repeatable; later matching globs win. |
| `--iglob GLOB` | Case-insensitive path glob. |
| `-t TYPE`, `--type TYPE` | Include a built-in file type, such as `py` or `js`. |
| `-T TYPE`, `--type-not TYPE` | Exclude a file type. |
| `--type-list` | List recognized file types and their globs. |
| `--hidden` | Include hidden files/directories; ignore rules still apply. |
| `--no-ignore` | Disable ignore rules; hidden entries still need `--hidden`. |
| `-u` / `-uu` / `-uuu` | Disable ignores / also include hidden / also search binary files. |
| `-a`, `--text` | Treat binary data as text; can print arbitrary bytes. |
| `-L`, `--follow` | Follow symbolic links during traversal. |
| `--max-depth N` | Limit directory traversal depth. |
| `--max-filesize SIZE` | Skip files larger than SIZE; suffixes `K`, `M`, `G` use powers of 1024. |
| `--one-file-system` | Do not descend into another filesystem. |
| `-E ENCODING`, `--encoding ENCODING` | Decode a specified encoding, e.g. `utf-16le`. |
| `-z`, `--search-zip` | Search supported compressed streams using available external decompressors; not a general ZIP/TAR archive walker. |
| `--files` | List eligible file paths without searching contents. |
| `--no-config` | Ignore settings from `RIPGREP_CONFIG_PATH`. |

## Output and control switches

| Switch | Purpose |
| --- | --- |
| `-n`, `--line-number` | Include line numbers, including when piping or saving. |
| `-H`, `--with-filename` | Always show filenames. |
| `-I`, `--no-filename` | Suppress filenames; does **not** disable ignore rules. |
| `--no-heading` | Prefix matching lines with paths instead of using file headings. |
| `--column` | Include 1-based byte column numbers. |
| `-A N`, `-B N`, `-C N` | Show N lines after, before, or on both sides of matches. |
| `-o`, `--only-matching` | Print matching parts only. |
| `-l`, `--files-with-matches` | Print only paths with a match. |
| `--files-without-match` | Print only paths with no match. |
| `-c`, `--count` | Count matching lines per file in ordinary line mode. |
| `--count-matches` | Count individual matches per file. |
| `--include-zero` | Include zero counts in count output. |
| `-m N`, `--max-count N` | Stop after N matching lines **per file**. |
| `-q`, `--quiet` | No stdout; stop when a match is found. |
| `-0`, `--null` | Follow printed filenames with NUL; useful with `-l` or `--files`. |
| `--json` | Emit JSON Lines search events and a summary. |
| `--stats` | Append search statistics. |
| `--sort path` | Sort traversal/results by path; disables parallel searching. |
| `-j N`, `--threads N` | Set thread count. |
| `--color never` | Disable color for reports/pipelines. |
| `-r TEXT`, `--replace TEXT` | Replace matches in **printed output only**; never edits files. |
| `--debug` | Explain filtering and other search decisions on stderr. |
| `-h`, `--help`, `-V`, `--version` | Short help, detailed help, version. |

## Practical examples

```bash
# Basic, case-insensitive, literal, and whole-word searches
rg -n 'error' ./logs
rg -ni 'access denied' ./logs
rg -nF '192.0.2.10' ./logs
rg -nw 'root' ./exports

# Regex alternatives, anchored lines, and multiple patterns (OR)
rg -n 'error|warning|critical' ./logs
rg -n '^Failed password' ./logs
rg -n -e 'timeout' -e 'connection refused' ./logs

# Literal IOC list: one indicator per line, no blank lines
rg -nF -f ./analysis/iocs.txt ./exports

# Select extensions or built-in types; exclude directories
rg -n -g '*.log' -g '!archive/**' 'error' ./logs
rg -n -t py -g '!tests/**' 'subprocess' .
rg --type-list

# Include ignored files; hidden entries are still excluded
rg -n -u 'needle' ./exports

# Include both ignored and hidden files; retain normal binary detection
rg -n -uu 'needle' ./exports

# Equivalent long options for -uu
rg -n --hidden --no-ignore 'needle' ./exports

# Context, matching paths, and files with no match
rg -n -C 3 'authentication failure' ./logs
rg -l 'ERROR' ./logs
rg --files-without-match 'SUCCESS' ./logs

# Count matching lines versus individual occurrences
rg -c 'error' ./logs
rg --count-matches 'error' ./logs

# Extract matches; -I suppresses filename prefixes
rg -I -o '\b[0-9a-fA-F]{64}\b' ./exports

# PCRE2 lookbehind (requires PCRE2 support)
rg -nP '(?<=user=)[^ ]+' ./logs

# Match across newlines; .*? may span line breaks
rg -n -U --multiline-dotall 'BEGIN.*?END' ./exports

# Decode text and search supported compressed files
rg -n -E utf-16le 'PowerShell' ./exports/events.txt
rg -n -z 'error' ./logs

# Preview eligible filenames or diagnose skipped files
rg --files -g '*.json' ./exports
rg --debug 'needle' ./exports

# Pattern beginning with a dash
rg -n -e '-EncodedCommand' ./exports

# Replace only in output; shell single quotes preserve capture references
rg -n 'user=([^ ]+)' -r 'account=$1' ./logs

# Filename-safe pipeline (GNU xargs)
rg -l -0 'ERROR' ./logs | xargs -0 -r sha256sum --

# Save plain text or structured results; create ./reports first if needed
rg --no-config -nH --no-heading --color never --sort path \
  'error' ./logs > ./reports/error-matches.txt
rg --no-config --json 'error' ./logs > ./reports/error-matches.jsonl

# Use search status in a script
if rg -q 'ERROR' ./logs/app.log; then
  printf '%s\n' 'ERROR found'
fi
```

## Exit status and common pitfalls

- **0:** at least one match; **1:** no matches; **2:** error. In quiet mode, finding a match can yield 0 even if an error also occurred. Inspect stderr when completeness matters.
- `-c` counts matching lines, not occurrences; use `--count-matches` for occurrences. Multiline counting has different semantics; consult `rg --help`.
- `rg -g '*.log' 'error'` searches contents of selected files. `rg --files -g '*.log'` lists paths only.
- `-uu` includes hidden/ignored entries but retains binary filtering. `-uuu` enables binary searching; `-a` treats binary bytes as printable text.
- `-0` separates filenames, not matching lines. Use `rg -l -0` or `rg --files -0` when piping paths to `xargs -0`.
- `--json` cannot be combined with filename-only or count output modes.
- Flags differ between tools: fd `-H` means hidden; rg `-H` means show filenames. fd `-l` means details; rg `-l` means paths with matches.
- Search results are not a substitute for a complete forensic parser. For evidence, use read-only mounts and route saved output to analysis/report directories.

Reference used: local `rg --help`. Upstream: <https://github.com/BurntSushi/ripgrep>.

---

[The Unlicense — Public Domain](https://unlicense.org/)

Attribution is appreciated but not required.
