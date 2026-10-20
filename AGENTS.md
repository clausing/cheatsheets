# Repository Guidelines

## Project Structure & Module Organization

This project contains command-line reference sheets for `fd`/`fdfind` and `rg`/ripgrep.

- `fd-cheatsheet.md` and `rg-cheatsheet.md` contain the editable reference text.
- `*-cheatsheet-print.html` contains printable HTML previews.
- `print_cheatsheets.py` converts Markdown into PDFs and optionally HTML, using Python Markdown and WeasyPrint. Print styles live in its embedded `CSS` string.

There is no separate application, test directory, or asset pipeline.

## Build, Test, and Development Commands

The renderer requires the Python `markdown` and `weasyprint` packages, plus WeasyPrint’s system dependencies.

- `python3 print_cheatsheets.py --help`: display supported layout options.
- `python3 print_cheatsheets.py fd-cheatsheet.md rg-cheatsheet.md`: render only the named Markdown files.
- `python3 print_cheatsheets.py`: generate PDFs with US Letter landscape pages and three columns.
- `python3 print_cheatsheets.py -H --paper-size a4 --portrait --columns 2`: generate PDFs and HTML with a custom layout.

Without filenames, the script reads all `*.md` files beside it except `AGENTS.md` and writes generated files alongside them. Existing generated files at the destination are overwritten.

## Coding Style & Naming Conventions

Match the existing Python style: four-space indentation, snake_case functions and variables, and uppercase module constants. Keep changes focused; no formatter or linter configuration is provided.

Use `TOOL-cheatsheet.md` for source documents and `TOOL-cheatsheet-print.html` or `.pdf` for rendered versions. Structure Markdown with descriptive headings, compact switch tables, and fenced `bash` examples. Preserve tool-version verification notes when updating examples.

## Testing Guidelines

No automated test framework or coverage threshold is configured. Verify changed command examples against the installed tool’s help and record the version used. After renderer changes, generate both sheets and inspect PDFs and HTML for clipped tables, broken code wrapping, and column breaks. Confirm PDFs are nonempty. Review source edits separately from generated output changes.

## Commit & Pull Request Guidelines

Git history is unavailable in this checkout, so an existing commit convention cannot be established. Use concise, imperative commit subjects. In pull requests, describe the affected tool, changed behavior, and verification performed. Include preview screenshots for layout changes and link relevant issues when available. Clearly disclose checks that could not run.
