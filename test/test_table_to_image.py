#!/usr/bin/env python3
"""
Tests for table_to_image.py

Run from project root: python test/test_table_to_image.py
All tests must PASS. If any fail, table conversion is broken.
"""
import sys
import re
from pathlib import Path

sys.path.insert(0, 'G:/ai/_shared_tools/publishing')

# Will fail until table_to_image.py is created
from table_to_image import convert_tables_to_images, has_tables

TEST_OUTPUT_DIR = Path('G:/ai/content_upload_meister/test/table_images')

# --- Fixtures ---

SIMPLE_TABLE = """\
# Article With Table

Here is some content before the table.

| Team | Record | PPG |
|------|--------|-----|
| Michigan | 24-1 | 90.6 |
| Houston | 23-2 | 78.3 |
| Iowa State | 22-3 | 84.2 |

Content after the table.
"""

MULTI_TABLE = """\
# Two Tables

First table:

| Name | Value |
|------|-------|
| Alpha | 1 |
| Beta | 2 |

Between tables.

| Column A | Column B | Column C |
|----------|----------|----------|
| X | Y | Z |
| 1 | 2 | 3 |

End.
"""

NO_TABLE = """\
# No Tables Here

Just regular content with **bold** and *italic* text.

- List item 1
- List item 2
"""

SINGLE_ROW_TABLE = """\
| Header A | Header B |
|----------|----------|
| Only Row | Data |
"""


def run_test(name, fn):
    try:
        fn()
        print(f'  PASS  {name}')
        return True
    except AssertionError as e:
        print(f'  FAIL  {name}: {e}')
        return False
    except Exception as e:
        print(f'  ERROR {name}: {type(e).__name__}: {e}')
        return False


# --- Tests ---

def test_has_tables_detects_table():
    assert has_tables(SIMPLE_TABLE), 'Should detect markdown table'


def test_has_tables_no_false_positive():
    assert not has_tables(NO_TABLE), 'Should not detect table in plain content'


def test_no_table_content_unchanged():
    result, paths = convert_tables_to_images(NO_TABLE, TEST_OUTPUT_DIR)
    assert result == NO_TABLE, 'No-table content must be returned unchanged'
    assert paths == [], 'No images should be generated for content without tables'


def test_single_table_no_pipe_rows_remain():
    result, paths = convert_tables_to_images(SIMPLE_TABLE, TEST_OUTPUT_DIR, 'single')
    pipe_rows = [l for l in result.splitlines() if l.strip().startswith('|')]
    assert len(pipe_rows) == 0, f'Table rows still present in output: {pipe_rows}'


def test_single_table_one_png_created():
    result, paths = convert_tables_to_images(SIMPLE_TABLE, TEST_OUTPUT_DIR, 'single_png')
    assert len(paths) == 1, f'Expected 1 PNG path, got {len(paths)}'
    assert paths[0].exists(), f'PNG file not found at: {paths[0]}'
    assert paths[0].suffix == '.png', f'Expected .png extension, got: {paths[0].suffix}'


def test_single_table_png_not_empty():
    result, paths = convert_tables_to_images(SIMPLE_TABLE, TEST_OUTPUT_DIR, 'notempty')
    assert paths[0].stat().st_size > 1000, \
        f'PNG file suspiciously small ({paths[0].stat().st_size} bytes) — may be blank'


def test_single_table_valid_png_header():
    """Verify the PNG file starts with valid PNG magic bytes."""
    result, paths = convert_tables_to_images(SIMPLE_TABLE, TEST_OUTPUT_DIR, 'validpng')
    with open(paths[0], 'rb') as f:
        header = f.read(8)
    assert header == b'\x89PNG\r\n\x1a\n', f'Not a valid PNG — bad header: {header!r}'


def test_single_table_image_ref_in_output():
    result, paths = convert_tables_to_images(SIMPLE_TABLE, TEST_OUTPUT_DIR, 'imgref')
    assert '![' in result, 'No image reference inserted into content'
    assert paths[0].as_posix() in result, \
        f'PNG path not found in output content.\nPath: {paths[0]}\nContent: {result}'


def test_surrounding_content_preserved():
    result, paths = convert_tables_to_images(SIMPLE_TABLE, TEST_OUTPUT_DIR, 'surround')
    assert 'Here is some content before the table.' in result, 'Pre-table content lost'
    assert 'Content after the table.' in result, 'Post-table content lost'
    assert '# Article With Table' in result, 'Heading lost'


def test_multi_table_both_removed():
    result, paths = convert_tables_to_images(MULTI_TABLE, TEST_OUTPUT_DIR, 'multi')
    pipe_rows = [l for l in result.splitlines() if l.strip().startswith('|')]
    assert len(pipe_rows) == 0, f'Table rows still present: {pipe_rows}'


def test_multi_table_two_pngs_created():
    result, paths = convert_tables_to_images(MULTI_TABLE, TEST_OUTPUT_DIR, 'multi_png')
    assert len(paths) == 2, f'Expected 2 PNGs, got {len(paths)}'
    for p in paths:
        assert p.exists(), f'PNG missing: {p}'
        assert p.stat().st_size > 1000, f'PNG too small: {p}'


def test_multi_table_two_refs_in_content():
    result, paths = convert_tables_to_images(MULTI_TABLE, TEST_OUTPUT_DIR, 'multi_ref')
    ref_count = result.count('![')
    assert ref_count == 2, f'Expected 2 image refs, found {ref_count}'


def test_multi_table_surrounding_content_preserved():
    result, paths = convert_tables_to_images(MULTI_TABLE, TEST_OUTPUT_DIR, 'multi_surr')
    assert 'Between tables.' in result, 'Content between tables lost'
    assert 'First table:' in result, 'Pre-first-table content lost'
    assert 'End.' in result, 'Post-last-table content lost'


def test_single_row_table_works():
    result, paths = convert_tables_to_images(SINGLE_ROW_TABLE, TEST_OUTPUT_DIR, 'onerow')
    assert len(paths) == 1, 'Should handle single-data-row table'
    assert paths[0].exists(), 'PNG not created for single-row table'
    pipe_rows = [l for l in result.splitlines() if l.strip().startswith('|')]
    assert len(pipe_rows) == 0, 'Single-row table not removed'


if __name__ == '__main__':
    print('=' * 55)
    print('  Table-to-Image Conversion Tests')
    print('=' * 55)

    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tests = [
        ('has_tables() detects table', test_has_tables_detects_table),
        ('has_tables() no false positive', test_has_tables_no_false_positive),
        ('no-table content unchanged', test_no_table_content_unchanged),
        ('single table: pipe rows removed', test_single_table_no_pipe_rows_remain),
        ('single table: one PNG created', test_single_table_one_png_created),
        ('single table: PNG not empty', test_single_table_png_not_empty),
        ('single table: valid PNG bytes', test_single_table_valid_png_header),
        ('single table: image ref inserted', test_single_table_image_ref_in_output),
        ('surrounding content preserved', test_surrounding_content_preserved),
        ('multi-table: both removed', test_multi_table_both_removed),
        ('multi-table: two PNGs created', test_multi_table_two_pngs_created),
        ('multi-table: two refs in content', test_multi_table_two_refs_in_content),
        ('multi-table: between-table content kept', test_multi_table_surrounding_content_preserved),
        ('single-row table works', test_single_row_table_works),
    ]

    results = [run_test(name, fn) for name, fn in tests]

    print('=' * 55)
    passed = sum(results)
    total = len(results)
    print(f'  {passed}/{total} passed')
    if passed == total:
        print('  ALL TESTS PASS')
        sys.exit(0)
    else:
        print('  TESTS FAILED')
        sys.exit(1)
