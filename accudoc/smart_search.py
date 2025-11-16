"""
Smart repository search for AccuDoc.

Provides fast, dependency-free search across source files and docs with
exact and lightweight fuzzy matching using Python's standard library.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


DEFAULT_INCLUDE_EXTS = {
    '.md', '.markdown', '.txt', '.rst',
    '.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.yaml', '.yml',
    '.ini', '.toml', '.cfg', '.conf', '.css', '.html', '.xml'
}

DEFAULT_EXCLUDE_DIRS = {
    '.git', '.hg', '.svn', '__pycache__', 'node_modules', 'dist', 'build',
    '.venv', 'venv', '.idea', '.vscode', '.next', '.cache', '.pytest_cache'
}


@dataclass
class Match:
    path: str
    line_number: int
    line_content: str
    score: float
    context_before: List[str]
    context_after: List[str]


class SearchEngine:
    def __init__(
        self,
        root: str | Path,
        include_exts: Optional[Iterable[str]] = None,
        exclude_dirs: Optional[Iterable[str]] = None,
    ) -> None:
        self.root = Path(root)
        self.include_exts = {e.lower() if e.startswith('.') else f'.{e.lower()}'
                             for e in (include_exts or DEFAULT_INCLUDE_EXTS)}
        self.exclude_dirs = set(exclude_dirs or DEFAULT_EXCLUDE_DIRS)

    def _iter_files(self) -> Iterable[Path]:
        for dirpath, dirnames, filenames in os.walk(self.root):
            # Prune excluded dirs in-place for efficiency
            dirnames[:] = [d for d in dirnames if d not in self.exclude_dirs]
            for name in filenames:
                ext = os.path.splitext(name)[1].lower()
                if ext in self.include_exts:
                    yield Path(dirpath) / name

    @staticmethod
    def _fuzzy_score(query: str, text: str) -> float:
        q = query.strip().lower()
        t = text.strip().lower()
        if not q or not t:
            return 0.0
        # Exact substring gets a big boost
        if q in t:
            return 1.0
        # Fall back to SequenceMatcher ratio
        return SequenceMatcher(None, q, t).ratio()

    def _match_line(
        self,
        query: str,
        line: str,
        mode: str,
        threshold: float = 0.55,
    ) -> Optional[float]:
        if mode == 'exact':
            return 1.0 if query.lower() in line.lower() else None
        # fuzzy
        score = self._fuzzy_score(query, line)
        return score if score >= threshold else None

    def search(
        self,
        query: str,
        *,
        mode: str = 'fuzzy',
        limit: int = 50,
        context_lines: int = 2,
    ) -> List[Match]:
        results: List[Match] = []
        q = query.strip()
        if not q:
            return results

        for file_path in self._iter_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            except Exception:
                continue

            for i, line in enumerate(lines):
                score = self._match_line(q, line, mode)
                if score is None:
                    continue

                start_ctx = max(0, i - context_lines)
                end_ctx = min(len(lines), i + context_lines + 1)
                ctx_before = [l.rstrip('\n') for l in lines[start_ctx:i]]
                ctx_after = [l.rstrip('\n') for l in lines[i+1:end_ctx]]

                results.append(Match(
                    path=str(file_path),
                    line_number=i + 1,
                    line_content=lines[i].rstrip('\n'),
                    score=float(score),
                    context_before=ctx_before,
                    context_after=ctx_after,
                ))

                if len(results) >= limit:
                    break

            if len(results) >= limit:
                break

        # Sort by score descending, then shorter file paths first
        results.sort(key=lambda m: (-m.score, len(m.path)))
        return results[:limit]


def search_repository(
    root: str | Path,
    query: str,
    *,
    mode: str = 'fuzzy',
    limit: int = 50,
    context_lines: int = 2,
    include_exts: Optional[Iterable[str]] = None,
    exclude_dirs: Optional[Iterable[str]] = None,
) -> List[Match]:
    engine = SearchEngine(root, include_exts=include_exts, exclude_dirs=exclude_dirs)
    return engine.search(query, mode=mode, limit=limit, context_lines=context_lines)
