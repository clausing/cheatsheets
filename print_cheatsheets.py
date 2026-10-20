#!/usr/bin/env python3
"""Convert Markdown files beside this script (except AGENTS.md) to PDF; optionally save HTML with -H.

Run from the repository root:
    python3 print_cheatsheets.py
    python3 print_cheatsheets.py fd-cheatsheet.md rg-cheatsheet.md

Dependencies (Ubuntu): sudo apt install python3-markdown weasyprint
Outputs: <source-stem>-print.pdf beside each source (also .html with -H)
Default layout: US Letter landscape, three columns.
Options: --paper-size, --landscape/--portrait, --columns, --save-html.
Existing generated outputs are overwritten; source Markdown is only read.
"""
from pathlib import Path
import argparse
import html
import sys
import markdown
from weasyprint import HTML

__description__ = 'Convert Markdown cheatsheets to printable PDFs and optional HTML.'
__author__ = 'Jim Clausing'
__version_info__ = (1, 0, 0)
__version__ = '.'.join(map(str, __version_info__))
__date__ = '2026-10-20'

ROOT = Path(__file__).resolve().parent
PAPER_SIZES = {
    'letter': (215.9, 279.4),
    'legal': (215.9, 355.6),
    'tabloid': (279.4, 431.8),
    'a3': (297, 420),
    'a4': (210, 297),
    'a5': (148, 210),
}
CSS = """
@page {
  size: PAPER_WIDTHmm PAPER_HEIGHTmm;
  margin: 10mm 10mm 18mm;
  @bottom-center { content: element(license-footer); }
}
footer { position: running(license-footer); text-align: center; font-size: 7pt; }
@media screen {
  body { display: flex; flex-direction: column; }
  footer { position: static; order: 1; margin-top: 8mm; }
}
* { box-sizing: border-box; }
body { margin: 0; color: #111; font: 8pt/1.3 Arial, sans-serif; }
main { column-count: COLUMN_COUNT; column-gap: 6mm; column-rule: .2mm solid #ddd; }
h1 { font-size: 15pt; margin-top: 0; }
h2 { font-size: 10pt; margin: 1em 0 .4em; }
h1, h2, h3 { break-after: avoid; }
p { margin: .4em 0; }
table { width: 100%; border-collapse: collapse; font-size: 7pt; }
th, td { text-align: left; vertical-align: top; border-bottom: 1px solid #ddd; padding: 3px; overflow-wrap: anywhere; }
tr { break-inside: avoid; }
pre { background: #f3f3f3; padding: 5px; white-space: pre-wrap; overflow-wrap: anywhere; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: .9em; }
pre code { font-size: 7pt; }
a { color: inherit; overflow-wrap: anywhere; }
ul { padding-left: 1.3em; }
@media screen {
  body { max-width: PAPER_WIDTHmm; margin: 20px auto; padding: 10mm; background: white; }
  html { background: #ddd; }
}
"""

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-V', '--version', action='version',
                        version=f'%(prog)s {__version__}')
    parser.add_argument('-H', '--save-html', action='store_true',
                        help='also save HTML previews alongside the PDFs')
    parser.add_argument('-p', '--paper-size', type=str.lower,
                        choices=PAPER_SIZES, default='letter',
                        help='paper size (default: letter)')
    orientation = parser.add_mutually_exclusive_group()
    orientation.add_argument('-l', '--landscape', dest='orientation',
                             action='store_const', const='landscape',
                             help='landscape orientation (default)')
    orientation.add_argument('-P', '--portrait', dest='orientation',
                             action='store_const', const='portrait',
                             help='portrait orientation')
    parser.set_defaults(orientation='landscape')
    parser.add_argument('-c', '--columns', type=int, choices=(1, 2, 3, 4),
                        default=3, help='number of columns (default: 3)')
    parser.add_argument('files', nargs='*', type=Path, metavar='FILE.md',
                        help='Markdown files to render (default: all *.md beside the script except AGENTS.md)')
    args = parser.parse_args()
    sources = args.files if args.files else sorted(ROOT.glob('*.md'))
    sources = list(dict.fromkeys(source.resolve() for source in sources
                                if source.name != 'AGENTS.md'))
    for source in sources:
        if source.suffix.lower() != '.md' or not source.is_file():
            parser.error(f'not an existing Markdown file: {source}')
    width, height = PAPER_SIZES[args.paper_size]
    if args.orientation == 'landscape':
        width, height = height, width
    css = (CSS.replace('PAPER_WIDTH', str(width))
           .replace('PAPER_HEIGHT', str(height))
           .replace('COLUMN_COUNT', str(args.columns)))
    for source in sources:
        destination = source.with_name(f'{source.stem}-print.html')
        body = markdown.markdown(source.read_text(encoding='utf-8'), extensions=['tables', 'fenced_code'])
        title = html.escape(f'{source.stem} — print')
        html_content = (
            '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            f'<title>{title}</title><style>{css}</style></head>'
            '<body><footer>'
            '<a href="https://unlicense.org/">'
            'The Unlicense — Public Domain</a><br>'
            'Attribution is appreciated but not required.'
            '</footer>'
            f'<main>{body}</main></body></html>\n'
        )
        if args.save_html:
            destination.write_text(html_content, encoding='utf-8')
            print(f'HTML: {destination}')
            sys.stdout.flush()
        pdf = destination.with_suffix('.pdf')
        HTML(string=html_content, base_url=str(source.parent)).write_pdf(str(pdf))
        if not pdf.is_file() or pdf.stat().st_size == 0:
            raise RuntimeError(f'PDF generation failed: {pdf}')
        print(f'PDF:  {pdf}')
        sys.stdout.flush()

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Conversion failed: {exc}', file=sys.stderr)
        sys.exit(1)
