# Cheatsheets

A collection of command-line cheatsheets I find useful.

- [fd / fdfind](fd-cheatsheet.md) · [Printable PDF](fd-cheatsheet-print.pdf)
- [rg / ripgrep](rg-cheatsheet.md) · [Printable PDF](rg-cheatsheet-print.pdf)

Generate PDFs with Python Markdown and WeasyPrint installed:

```bash
python3 print_cheatsheets.py
```

Render selected files or also save HTML previews:

```bash
python3 print_cheatsheets.py fd-cheatsheet.md rg-cheatsheet.md
python3 print_cheatsheets.py -H
```

Outputs are saved beside their source files. `README.md` and `AGENTS.md` are excluded.
Run `python3 print_cheatsheets.py --help` for layout options.

Released under [The Unlicense](LICENSE), a public domain dedication.

Attribution is appreciated but not required.
