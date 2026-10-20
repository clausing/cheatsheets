import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import print_cheatsheets as renderer


class RendererTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=renderer.ROOT)
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / 'sample.md'
        self.source.write_text('# Sample\n', encoding='utf-8')
        self.pdf = self.root / 'sample-print.pdf'
        self.preview = self.root / 'sample-print.html'

    def run_renderer(self):
        with patch.object(renderer, 'ROOT', self.root), \
                patch('sys.argv', ['print_cheatsheets.py', '-H']), \
                contextlib.redirect_stdout(io.StringIO()):
            renderer.main()

    def test_render_failure_preserves_outputs(self):
        self.pdf.write_bytes(b'old PDF')
        self.preview.write_bytes(b'old HTML')
        with patch.object(renderer.HTML, 'write_pdf', side_effect=OSError('write failed')):
            with self.assertRaisesRegex(OSError, 'write failed'):
                self.run_renderer()
        self.assertEqual(self.pdf.read_bytes(), b'old PDF')
        self.assertEqual(self.preview.read_bytes(), b'old HTML')

    def test_missing_image_fails_and_preserves_outputs(self):
        self.source.write_text('![diagram](missing-image.png)', encoding='utf-8')
        self.pdf.write_bytes(b'old PDF')
        with self.assertRaisesRegex(RuntimeError, 'missing-image.png'):
            self.run_renderer()
        self.assertEqual(self.pdf.read_bytes(), b'old PDF')
        self.assertFalse(self.preview.exists())

    def test_replacement_failure_preserves_file_and_cleans_temporary(self):
        self.pdf.write_bytes(b'old PDF')
        with patch.object(Path, 'replace', side_effect=OSError('replace failed')):
            with self.assertRaisesRegex(OSError, 'replace failed'):
                renderer.atomic_write(self.pdf, b'new PDF')
        self.assertEqual(self.pdf.read_bytes(), b'old PDF')
        self.assertEqual(sorted(p.name for p in self.root.iterdir()),
                         ['sample-print.pdf', 'sample.md'])

    def test_license_is_in_footer_only_and_source_is_preserved(self):
        source = '# Sample\n\n' + renderer.LICENSE_MARKDOWN + '\n'
        self.source.write_text(source, encoding='utf-8')
        self.run_renderer()
        html = self.preview.read_text(encoding='utf-8')
        self.assertEqual(html.count('The Unlicense — Public Domain'), 1)
        self.assertNotIn('The Unlicense', html.split('<main>', 1)[1])
        self.assertEqual(self.source.read_text(encoding='utf-8'), source)
        self.assertTrue(self.pdf.read_bytes().startswith(b'%PDF-'))

    def test_render_error_handler_is_removed(self):
        logger = renderer.logging.getLogger('weasyprint')
        handlers = list(logger.handlers)
        with patch.object(renderer.HTML, 'write_pdf', side_effect=OSError('failed')):
            with self.assertRaises(OSError):
                renderer.render_pdf('<p>Sample</p>', self.root)
        self.assertEqual(logger.handlers, handlers)


if __name__ == '__main__':
    unittest.main()
