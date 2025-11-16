import os
import tempfile
from pathlib import Path

from accudoc.smart_search import search_repository


def test_search_repository_exact_match():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / 'README.md').write_text('Hello AccuDoc Smart Search\nFind me here', encoding='utf-8')
        (root / 'code.py').write_text('# sample\nvalue = 42\n', encoding='utf-8')

        results = search_repository(root, 'Find me', mode='exact', limit=10)
        assert len(results) >= 1
        assert any('README.md' in r.path for r in results)


def test_search_repository_fuzzy_match():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / 'notes.txt').write_text('documentation generation pipeline', encoding='utf-8')

        # Intentionally misspelled query to trigger fuzzy
        results = search_repository(root, 'doc generashun', mode='fuzzy', limit=10)
        assert len(results) >= 1
        assert any('notes.txt' in r.path for r in results)
