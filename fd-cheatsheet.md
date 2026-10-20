# fd / fdfind cheatsheet

Find files and directories **by name**. To search file contents, use `rg`.

Verified against local `fdfind 9.0.0` help on 2026-10-20 (UTC).

## Command name and syntax

Ubuntu/Debian commonly install this tool as `fdfind`; other systems use `fd`.
All examples below use `fdfind`. Substitute `fd` if that is your executable.

```bash
fdfind [OPTIONS] [PATTERN] [SEARCH_ROOT ...]
fdfind                        # List entries below the current directory
fdfind invoice ./documents    # Names containing invoice
fdfind '' ./documents         # All eligible entries under this root
```

By default: recursive search, regular expression patterns, matching against the
basename, and smart case (case-insensitive unless the pattern contains uppercase).
Hidden entries and ignored entries are skipped. Git ignore rules normally require
a Git repository. Quote patterns to prevent shell expansion.

## Important switches

| Switch | Purpose |
| --- | --- |
| `-g`, `--glob` | Use a glob instead of a regex; useful for exact filenames. |
| `-F`, `--fixed-strings` | Literal substring search, rather than regex. |
| `-s`, `--case-sensitive` | Force case-sensitive matching. |
| `-i`, `--ignore-case` | Force case-insensitive matching. |
| `-p`, `--full-path` | Match the full absolute path instead of just the basename. |
| `-H`, `--hidden` | Include hidden entries; ignore rules still apply. |
| `-I`, `--no-ignore` | Disable ignore rules; hidden entries still need `-H`. |
| `-u`, `--unrestricted` | Include hidden and ignored entries (`-H -I`). |
| `-E GLOB`, `--exclude GLOB` | Exclude matching entries; repeatable. |
| `-t TYPE`, `--type TYPE` | Filter by entry type; see below. |
| `-e EXT`, `--extension EXT` | Filter extensions without a leading dot; repeatable. |
| `-d N`, `--max-depth N` | Limit traversal depth; `1` searches immediate children. |
| `--min-depth N`, `--exact-depth N` | Restrict result depth. |
| `-S SIZE`, `--size SIZE` | Filter file size; `+` means at least, `-` at most, neither means exact. |
| `--changed-within TIME` | Modification time newer than a date or duration. |
| `--changed-before TIME` | Modification time older than a date or duration. |
| `-o USER:GROUP`, `--owner USER:GROUP` | Filter owner/group; either side can be omitted. |
| `-L`, `--follow` | Traverse symlinked directories. |
| `--one-file-system` | Do not descend into another filesystem. |
| `-a`, `--absolute-path` | Print absolute paths. |
| `-l`, `--list-details` | Detailed listing similar to `ls -l`. |
| `-0`, `--print0` | NUL-delimit paths for filename-safe pipelines. |
| `-x CMD`, `--exec CMD` | Run a command for each result, in parallel by default. |
| `-X CMD`, `--exec-batch CMD` | Pass results together to a command; OS limits can split batches. |
| `-j N`, `--threads N` | Set search/execution threads; `1` makes `-x` sequential. |
| `--max-results N`, `-1` | Stop after N results, or after one result. |
| `-q`, `--quiet` | Print nothing; status 0 if a result exists, 1 if none. |
| `--show-errors` | Display filesystem traversal errors. |
| `--color never` | Disable color for saved output. |
| `-h`, `--help`, `-V`, `--version` | Short help, detailed help, version. |

Types: `f` file, `d` directory, `l` symlink, `x` executable file, `e` empty
file/directory, `s` socket, `p` named pipe, `b` block device, `c` character device.
Use `-t e -t f` for empty files or `-t e -t d` for empty directories.

## Practical examples

```bash
# Regex: exact filename, or alternative extensions
fdfind '^report\.csv$' ./documents
fdfind '\.(csv|json)$' ./exports

# Glob: exact name or wildcard
fdfind -g 'README.md' .
fdfind -g '*.log' ./logs

# Literal text containing regex metacharacters
fdfind -F 'report[final]' ./documents

# Files with either extension; directories; symlinks; empty files
fdfind -t f -e jpg -e png ./images
fdfind -t d -g '*cache*' .
fdfind -t l .
fdfind -t e -t f .

# Include hidden entries; ignore rules still apply
fdfind -H -t f -g '.env*' .

# Include ignored entries; hidden entries are still excluded
fdfind -I -t f -e log .

# Include both hidden and ignored entries (-H -I is equivalent to -u)
fdfind -H -I -t f -g '.env*' .

# Include hidden and ignored entries, excluding selected directories
fdfind -u -t f -E .git -E node_modules -e log .

# Match directory components too
fdfind -p -g '**/config/*.json' .

# Immediate children only
fdfind -d 1 -t f '' ./documents

# Size range: at least 10 MiB and at most 100 MiB
fdfind -t f -S +10mi -S -100mi ./exports

# Modified within 24 hours (relative to command execution)
TZ=UTC fdfind -t f --changed-within 1d ./logs

# Modification times strictly after/before these UTC boundaries
TZ=UTC fdfind -t f --changed-within '2026-10-01 00:00:00' \
  --changed-before '2026-10-02 00:00:00' ./logs

# Owner or group
fdfind -t f --owner root ./exports
fdfind -t f --owner :analysts ./exports

# Read-only commands on results; put -x/-X last
fdfind -t f -e log ./logs -j 1 -x sha256sum -- '{}'
fdfind -t f -e txt ./documents -X wc -l -- '{}'

# Filename-safe pipeline (GNU xargs: -r skips execution when input is empty)
fdfind -t f -e log -0 ./logs | xargs -0 -r sha256sum --

# Pattern beginning with a dash
fdfind -- '-backup' ./documents

# Save a sorted list; create ./reports first if needed
fdfind -a -t f --color never ./documents | LC_ALL=C sort > ./reports/file-list.txt
```

## Execution placeholders and common pitfalls

| Placeholder | Expansion |
| --- | --- |
| `{}` | Path |
| `{/}` | Basename |
| `{//}` | Parent directory |
| `{.}` | Path without extension |
| `{/.}` | Basename without extension |

- A bare pattern is a regex: `.` means any character; use `\.` for a literal dot.
- `-e log` selects extensions; it does not search file contents.
- `-x` executes programs directly. Shell pipelines/redirection require an explicit shell.
- Search and execution order are not guaranteed. Use NUL-aware sorting for filenames containing newlines (`sort -z`); line-based sorting is for ordinary filenames.
- Size units: `k/m/g` are decimal; `ki/mi/gi` are binary.
- Date filters use **modification time**, not creation time. Set `TZ=UTC` for UTC date interpretation.
- For evidence, search a read-only mount and use read-only child commands; `-x`/`-X` can run any program, including modifying ones.

Reference used: local `fdfind --help`. Upstream: <https://github.com/sharkdp/fd>.

---

[The Unlicense — Public Domain](https://unlicense.org/)

Attribution is appreciated but not required.
