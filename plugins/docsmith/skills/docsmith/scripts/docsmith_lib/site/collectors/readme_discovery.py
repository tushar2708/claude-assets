# Vendored from smritea-cloud docs-site (generic, config-driven) — docsmith engine
"""Folder-doc discovery collector for the docs-site autogen pipeline.

A *folder doc* is a file that documents the directory it lives in. Three
filenames are folder docs: ``README.md``, ``AGENTS.md`` and ``CLAUDE.md``
(``FOLDER_DOC_FILENAMES``). This collector is the only one that collects
them; ``markdown_tree`` skips all three names, so no folder doc is
collected twice.

This collector recursively searches a configured list of root directories
(relative to the repo root) for folder docs. Because many such files share
the exact same filename, they cannot be copied flat into the autogen docs
tree without colliding. Instead, each discovered folder doc is copied to a
destination path derived from its parent directory path: all parent
segments except the last are preserved as nested subdirectories (with
underscores hyphenated for readability), and the last parent segment
becomes the output filename stem.

Output naming (``<dirs>`` = the hyphenated parent segments before the last
one, ``<parent>`` = the last parent segment):

    ============  ==========================================  ===========
    Folder doc    Output in a sub-folder                       Repo root
    ============  ==========================================  ===========
    README.md     ``<dirs>/<parent>.md``                       ``index.md``
    AGENTS.md     ``<dirs>/<parent>.md`` when the folder has    ``agents.md``
                  no collected README.md, else
                  ``<dirs>/<parent>-agents.md``
    CLAUDE.md     ``<dirs>/<parent>-claude.md``                ``claude.md``
    ============  ==========================================  ===========

The names are deterministic and the three folder docs of one folder never
share an output path. README.md outputs are the same as before AGENTS.md
and CLAUDE.md were collected, so existing README URLs do not change. A
README.md counts as "collected" for the AGENTS.md rule when it exists and
is not excluded by a source ``exclude`` glob or by the shared
``exclude.filenames`` list.

An ``AGENTS.md`` or ``CLAUDE.md`` that is a symlink is NOT collected: it
duplicates its target (typically ``CLAUDE.md -> AGENTS.md``), which is
collected on its own. A symlinked ``README.md`` is still collected.

Examples:
    ``cloud_backend/dataplane-api/README.md``
    -> ``readmes/cloud-backend/dataplane-api.md``

    ``cloud_backend/dataplane-api/AGENTS.md`` (folder also has README.md)
    -> ``readmes/cloud-backend/dataplane-api-agents.md``

    ``cloud_backend/dataplane-api/handlers/AGENTS.md`` (no README.md)
    -> ``readmes/cloud-backend/dataplane-api/handlers.md``

    ``python/README.md`` (single parent segment, no subdirectory)
    -> ``readmes/python.md``

    ``smritea-oss/oss_backend/smritea-oss-core/CLAUDE.md`` (regular file)
    -> ``readmes/smritea-oss/oss-backend/smritea-oss-core-claude.md``
"""

import fnmatch
import os
import re
import shutil
from pathlib import Path

import yaml

_FRONTMATTER_DELIMITER = '---'
_ATX_H1_PATTERN = re.compile(r'^#\s+(.+?)\s*$', re.MULTILINE)
_NUMERIC_PREFIX_PATTERN = re.compile(r'^\d+[-_.]*')
_README_FILENAME = 'README.md'
_AGENTS_FILENAME = 'AGENTS.md'
_CLAUDE_FILENAME = 'CLAUDE.md'

# Every folder-doc filename, in per-folder collection order. README.md comes
# first so a folder's README eligibility is known before AGENTS.md is named.
# markdown_tree imports this tuple to skip the same names.
FOLDER_DOC_FILENAMES = (_README_FILENAME, _AGENTS_FILENAME, _CLAUDE_FILENAME)

# Folder docs that are skipped when they are symlinks (they duplicate their target).
_SYMLINK_SKIPPED_FILENAMES = frozenset({_AGENTS_FILENAME, _CLAUDE_FILENAME})

# Output filename of each folder doc found directly at the repo root.
_ROOT_OUTPUT_FILENAMES = {
    _README_FILENAME: 'index.md',
    _AGENTS_FILENAME: 'agents.md',
    _CLAUDE_FILENAME: 'claude.md',
}

_AGENTS_STEM_SUFFIX = '-agents'
_CLAUDE_STEM_SUFFIX = '-claude'


def collect_readme_discovery(source: dict, repo_root: Path, autogen_docs_dir: Path, exclude_config: dict) -> list[dict]:
    """Discover folder docs under configured roots and copy them into the autogen docs tree.

    Folder docs are files named ``README.md``, ``AGENTS.md`` or ``CLAUDE.md``
    (see the module docstring for output naming and symlink handling).

    Args:
        source: Source configuration dict with keys ``id``, ``paths``,
            ``destination``, and ``exclude``.
        repo_root: Absolute path to the repository root.
        autogen_docs_dir: Absolute path to the autogen docs output directory.
        exclude_config: The `exclude:` section from `sources.yml`
            (`dir_basenames`, `dir_paths`, `filenames` lists) -- the single
            shared blacklist, not maintained separately per collector.

    Returns:
        A list of dicts, one per successfully collected folder doc, each
        with keys: ``source_id``, ``source_path``, ``output_path``,
        ``title``, ``okf_type``.
    """
    source_id = source['id']
    root_paths = source['paths']
    destination_subdir = source['destination']
    exclude_patterns = source.get('exclude', [])
    excluded_dir_basenames = set(exclude_config.get('dir_basenames', []))
    excluded_dir_paths = list(exclude_config.get('dir_paths', []))
    excluded_filenames = set(exclude_config.get('filenames', []))

    collected: list[dict] = []
    for root_path in root_paths:
        root_dir = repo_root / root_path
        collected.extend(
            _collect_from_root(
                source_id=source_id,
                root_dir=root_dir,
                repo_root=repo_root,
                autogen_docs_dir=autogen_docs_dir,
                destination_subdir=destination_subdir,
                exclude_patterns=exclude_patterns,
                excluded_dir_basenames=excluded_dir_basenames,
                excluded_dir_paths=excluded_dir_paths,
                excluded_filenames=excluded_filenames,
            )
        )
    return collected


def _collect_from_root(
    source_id: str,
    root_dir: Path,
    repo_root: Path,
    autogen_docs_dir: Path,
    destination_subdir: str,
    exclude_patterns: list[str],
    excluded_dir_basenames: set[str],
    excluded_dir_paths: list[str],
    excluded_filenames: set[str],
) -> list[dict]:
    """Walk a single root directory and collect all folder docs under it."""
    if not root_dir.exists():
        print(f'[readme_discovery] root path does not exist, skipping: {root_dir}')
        return []

    collected: list[dict] = []
    for dirpath, dirnames, filenames in os.walk(root_dir, followlinks=False):
        current_dir = Path(dirpath)
        _prune_excluded_dirs(
            current_dir, dirnames, repo_root, exclude_patterns, excluded_dir_basenames, excluded_dir_paths
        )

        eligible_filenames = _eligible_folder_doc_filenames(
            current_dir, filenames, repo_root, exclude_patterns, excluded_filenames
        )
        folder_has_readme = _README_FILENAME in eligible_filenames
        for filename in eligible_filenames:
            doc_path = current_dir / filename
            item = _collect_single_folder_doc(
                source_id=source_id,
                doc_path=doc_path,
                relative_doc_path=doc_path.relative_to(repo_root),
                autogen_docs_dir=autogen_docs_dir,
                destination_subdir=destination_subdir,
                stem_suffix=_output_stem_suffix(filename, folder_has_readme),
            )
            if item is not None:
                collected.append(item)

    return collected


def _eligible_folder_doc_filenames(
    current_dir: Path,
    filenames: list[str],
    repo_root: Path,
    exclude_patterns: list[str],
    excluded_filenames: set[str],
) -> list[str]:
    """Return the folder docs of current_dir to collect, in FOLDER_DOC_FILENAMES order.

    A folder doc is skipped when its name is in the shared
    ``exclude.filenames`` list, when its repo-relative path matches a source
    ``exclude`` glob, or when it is a symlinked AGENTS.md / CLAUDE.md.
    """
    present = set(filenames)
    eligible: list[str] = []
    for filename in FOLDER_DOC_FILENAMES:
        if filename not in present or filename in excluded_filenames:
            continue
        doc_path = current_dir / filename
        if _is_excluded(doc_path.relative_to(repo_root), exclude_patterns):
            continue
        if filename in _SYMLINK_SKIPPED_FILENAMES and doc_path.is_symlink():
            continue
        eligible.append(filename)
    return eligible


def _output_stem_suffix(filename: str, folder_has_readme: bool) -> str:
    """Return the suffix appended to ``<parent>`` to name a sub-folder folder doc's output."""
    if filename == _README_FILENAME:
        return ''
    if filename == _AGENTS_FILENAME:
        return _AGENTS_STEM_SUFFIX if folder_has_readme else ''
    if filename == _CLAUDE_FILENAME:
        return _CLAUDE_STEM_SUFFIX
    raise ValueError(f'not a folder doc filename: {filename}')


def _prune_excluded_dirs(
    current_dir: Path,
    dirnames: list[str],
    repo_root: Path,
    exclude_patterns: list[str],
    excluded_dir_basenames: set[str],
    excluded_dir_paths: list[str],
) -> None:
    """Remove excluded subdirectories from dirnames in-place so os.walk skips them."""
    kept_dirnames = []
    for dirname in dirnames:
        if dirname in excluded_dir_basenames:
            continue
        candidate_dir = current_dir / dirname
        relative_candidate_dir = candidate_dir.relative_to(repo_root)
        if _is_excluded(relative_candidate_dir, exclude_patterns):
            continue
        if _is_excluded_dir_path(candidate_dir, repo_root, excluded_dir_paths):
            continue
        kept_dirnames.append(dirname)
    dirnames[:] = kept_dirnames


def _is_excluded_dir_path(candidate_dir: Path, repo_root: Path, excluded_dir_paths: list[str]) -> bool:
    """Check whether candidate_dir (relative to repo_root) matches an excluded path prefix."""
    try:
        relative = candidate_dir.relative_to(repo_root).as_posix()
    except ValueError:
        return False
    return any(relative == excluded or relative.startswith(excluded + '/') for excluded in excluded_dir_paths)


def _is_excluded(relative_path: Path, exclude_patterns: list[str]) -> bool:
    """Check whether a repo-root-relative path matches any exclude glob pattern."""
    relative_path_str = str(relative_path)
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(relative_path_str, pattern):
            return True
    return False


def _collect_single_folder_doc(
    source_id: str,
    doc_path: Path,
    relative_doc_path: Path,
    autogen_docs_dir: Path,
    destination_subdir: str,
    stem_suffix: str,
) -> dict | None:
    """Copy a single folder doc to its derived destination and extract metadata."""
    destination_path = _derive_destination_path(relative_doc_path, autogen_docs_dir, destination_subdir, stem_suffix)

    try:
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(doc_path, destination_path)
        content = doc_path.read_text(encoding='utf-8')
    except OSError as exc:
        print(f'[readme_discovery] failed to copy {doc_path}: {exc}')
        return None

    _, body = _split_frontmatter(content)
    okf_type = _extract_okf_type(content)
    title = _extract_title(body) or _fallback_title(_fallback_title_segment(relative_doc_path, destination_path))

    output_path = destination_path.relative_to(autogen_docs_dir)
    return {
        'source_id': source_id,
        'source_path': str(doc_path),
        'output_path': str(output_path),
        'title': title,
        'okf_type': okf_type,
    }


def _fallback_title_segment(relative_doc_path: Path, destination_path: Path) -> str:
    """Pick the name a fallback title is derived from when a folder doc has no H1.

    A README.md keeps its parent directory segment (empty at the repo root).
    AGENTS.md and CLAUDE.md use their output stem (e.g. ``payment-agents``,
    ``agents``), so the fallback titles of one folder's docs stay distinct.
    """
    if relative_doc_path.name == _README_FILENAME:
        return relative_doc_path.parent.parts[-1] if relative_doc_path.parent.parts else ''
    return destination_path.stem


def _derive_destination_path(
    relative_doc_path: Path, autogen_docs_dir: Path, destination_subdir: str, stem_suffix: str
) -> Path:
    """Derive the destination path for a folder doc based on its parent directory path.

    All path segments of the parent directory except the last are preserved
    as nested subdirectories (with underscores hyphenated). The last segment
    plus ``stem_suffix`` becomes the new filename stem (with a .md
    extension), and the original folder-doc filename is discarded. A folder
    doc directly at the repo root maps to its ``_ROOT_OUTPUT_FILENAMES``
    entry instead.
    """
    relative_parent = relative_doc_path.parent
    parts = relative_parent.parts

    if not parts:
        # Folder doc directly at repo_root (no parent segments at all).
        return autogen_docs_dir / destination_subdir / _ROOT_OUTPUT_FILENAMES[relative_doc_path.name]

    dir_parts = [part.replace('_', '-') for part in parts[:-1]]
    filename_stem = f'{parts[-1]}{stem_suffix}'

    if not dir_parts:
        return autogen_docs_dir / destination_subdir / f'{filename_stem}.md'

    return autogen_docs_dir / destination_subdir / Path(*dir_parts) / f'{filename_stem}.md'


def _split_frontmatter(content: str) -> tuple[dict | None, str]:
    """Split leading YAML frontmatter (delimited by ---) from the Markdown body."""
    if not content.startswith(_FRONTMATTER_DELIMITER):
        return None, content

    lines = content.splitlines()
    closing_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == _FRONTMATTER_DELIMITER:
            closing_index = index
            break

    if closing_index is None:
        return None, content

    frontmatter_text = '\n'.join(lines[1:closing_index])
    body = '\n'.join(lines[closing_index + 1:])

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError:
        return None, body

    if not isinstance(frontmatter, dict):
        return None, body

    return frontmatter, body


def _extract_okf_type(content: str) -> str | None:
    """Extract the frontmatter 'type' key, or None if absent/unparseable."""
    frontmatter, _ = _split_frontmatter(content)
    if not frontmatter:
        return None
    okf_type = frontmatter.get('type')
    if not isinstance(okf_type, str):
        return None
    return okf_type


def _extract_title(body: str) -> str | None:
    """Extract the first Markdown ATX H1 heading from the document body."""
    match = _ATX_H1_PATTERN.search(body)
    if not match:
        return None
    return match.group(1).strip()


def _fallback_title(segment: str) -> str:
    """Derive a fallback title from a path segment name.

    Strips any leading numeric prefix (e.g. '01-', '02_'), replaces
    hyphens/underscores with spaces, and title-cases the result.
    """
    if not segment:
        return 'Readme'

    without_prefix = _NUMERIC_PREFIX_PATTERN.sub('', segment)
    spaced = without_prefix.replace('-', ' ').replace('_', ' ').strip()
    if not spaced:
        return 'Readme'

    return spaced.title()
