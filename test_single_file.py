#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from convert_html_to_markdown import process_markdown_file, load_url_mappings
from pathlib import Path

# Load URL mappings
base_dir = Path('.').resolve()
url_mappings = load_url_mappings(base_dir / 'docs.json')

# Test on a single file
test_file = base_dir / 'Ascend C 算子开发' / '1. Ascend C简介.md'
process_markdown_file(test_file, url_mappings, base_dir)

print("\n\n=== Preview of converted file ===")
with open(test_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[:50], 1):
        print(f"{i:3d}: {line}", end='')
