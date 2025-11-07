#!/usr/bin/env python3
"""
Convert embedded HTML in markdown files to markdown syntax.
Replace URL links with relative paths based on docs.json mapping.
"""

import os
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup


def convert_html_to_markdown(html_content):
    """Convert HTML content to Markdown, keeping tables as HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Process tables - keep as HTML but remove unnecessary attributes
    for table in soup.find_all('table'):
        # Remove id, class, and other attributes from all tags in table
        for tag in table.find_all(True):
            # Keep only essential attributes
            attrs_to_keep = []
            if tag.name in ['td', 'th'] and 'colspan' in tag.attrs:
                attrs_to_keep.append('colspan')
            if tag.name in ['td', 'th'] and 'rowspan' in tag.attrs:
                attrs_to_keep.append('rowspan')
            
            # Remove all other attributes
            new_attrs = {}
            for attr in attrs_to_keep:
                if attr in tag.attrs:
                    new_attrs[attr] = tag.attrs[attr]
            tag.attrs = new_attrs
    
    # Convert headings
    for level in range(1, 7):
        for tag in soup.find_all(f'h{level}'):
            text = tag.get_text().strip()
            tag.replace_with(f'\n{"#" * level} {text}\n')
    
    # Convert strong/bold
    for tag in soup.find_all(['strong', 'b']):
        text = tag.get_text()
        tag.replace_with(f'**{text}**')
    
    # Convert em/italic
    for tag in soup.find_all(['em', 'i']):
        text = tag.get_text()
        tag.replace_with(f'*{text}*')
    
    # Convert code
    for tag in soup.find_all('code'):
        text = tag.get_text()
        tag.replace_with(f'`{text}`')
    
    # Convert pre/code blocks
    for tag in soup.find_all('pre'):
        text = tag.get_text()
        tag.replace_with(f'\n```\n{text}\n```\n')
    
    # Convert links
    for tag in soup.find_all('a'):
        href = tag.get('href', '')
        text = tag.get_text()
        if href:
            tag.replace_with(f'[{text}]({href})')
        else:
            tag.replace_with(text)
    
    # Convert images
    for tag in soup.find_all('img'):
        src = tag.get('src', '')
        alt = tag.get('alt', '')
        tag.replace_with(f'![{alt}]({src})')
    
    # Convert br
    for tag in soup.find_all('br'):
        tag.replace_with('\n')
    
    # Convert hr
    for tag in soup.find_all('hr'):
        tag.replace_with('\n---\n')
    
    # Convert lists
    for ul in soup.find_all('ul'):
        # Get all direct li children
        items = []
        for li in ul.find_all('li', recursive=False):
            text = li.get_text().strip()
            items.append(f'* {text}')
        ul.replace_with('\n' + '\n'.join(items) + '\n')
    
    for ol in soup.find_all('ol'):
        # Get all direct li children
        items = []
        for i, li in enumerate(ol.find_all('li', recursive=False), 1):
            text = li.get_text().strip()
            items.append(f'{i}. {text}')
        ol.replace_with('\n' + '\n'.join(items) + '\n')
    
    # Convert blockquotes
    for tag in soup.find_all('blockquote'):
        text = tag.get_text().strip()
        lines = text.split('\n')
        quoted = '\n'.join(f'> {line}' for line in lines)
        tag.replace_with(f'\n{quoted}\n')
    
    # Convert paragraphs
    for tag in soup.find_all('p'):
        text = tag.get_text().strip()
        if text:
            tag.replace_with(f'\n\n{text}\n')
        else:
            tag.decompose()
    
    # Remove empty div and span tags
    for tag in soup.find_all(['div', 'span']):
        tag.unwrap()
    
    # Get the final text
    result = str(soup)
    
    # Clean up excessive whitespace
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = re.sub(r' +', ' ', result)
    
    return result.strip()


def load_url_mappings(json_file):
    """Load URL to relative path mappings from docs.json."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    url_to_path = {}
    for item in data:
        url = item['url']
        main_section = item['main_section']
        parent_sections = item.get('parent_sections', [])
        filename = item['filename']
        
        # Build relative path
        path_parts = [main_section] + parent_sections
        file_path = os.path.join(*path_parts, f"{filename}.md")
        
        url_to_path[url] = file_path
    
    return url_to_path


def replace_urls_with_relative_paths(content, url_mappings, current_file_path):
    """Replace URLs in content with relative paths - both in markdown and HTML."""
    
    def replace_markdown_url(match):
        full_url = match.group(1)
        
        # Split URL and fragment (anchor)
        if '#' in full_url:
            url, fragment = full_url.split('#', 1)
            fragment = '#' + fragment
        else:
            url = full_url
            fragment = ''
        
        # Skip if URL is not in our mappings
        if url not in url_mappings:
            return match.group(0)
        
        target_path = url_mappings[url]
        
        # Calculate relative path from current file to target file
        current_dir = os.path.dirname(current_file_path)
        
        try:
            rel_path = os.path.relpath(target_path, current_dir)
            # Normalize path separators for URLs
            rel_path = rel_path.replace('\\', '/')
            return f'({rel_path}{fragment})'
        except ValueError:
            # If paths are on different drives (Windows), return original
            return match.group(0)
    
    def replace_html_url(match):
        full_url = match.group(1)
        
        # Split URL and fragment (anchor)
        if '#' in full_url:
            url, fragment = full_url.split('#', 1)
            fragment = '#' + fragment
        else:
            url = full_url
            fragment = ''
        
        # Skip if URL is not in our mappings
        if url not in url_mappings:
            return match.group(0)
        
        target_path = url_mappings[url]
        
        # Calculate relative path from current file to target file
        current_dir = os.path.dirname(current_file_path)
        
        try:
            rel_path = os.path.relpath(target_path, current_dir)
            # Normalize path separators for URLs
            rel_path = rel_path.replace('\\', '/')
            return f'"{rel_path}{fragment}"'
        except ValueError:
            # If paths are on different drives (Windows), return original
            return match.group(0)
    
    # Build a regex pattern that matches all URLs from url_mappings
    url_patterns = []
    for url in url_mappings.keys():
        escaped_url = re.escape(url)
        url_patterns.append(escaped_url)
    
    # Pattern for URLs (with optional fragment)
    base_pattern = '(?:' + '|'.join(url_patterns) + ')'
    fragment_pattern = r'(?:#[^)"]*)?'
    
    # Match URLs in markdown links [text](url) and images ![alt](url)
    markdown_pattern = r'\((' + base_pattern + fragment_pattern + r')\)'
    content = re.sub(markdown_pattern, replace_markdown_url, content)
    
    # Match URLs in HTML attributes like href="url"
    html_pattern = r'"(' + base_pattern + fragment_pattern + r')"'
    content = re.sub(html_pattern, replace_html_url, content)
    
    return content


def extract_body_content(html_content):
    """Extract content from <body> tag if present."""
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
    if body_match:
        return body_match.group(1)
    return html_content


def process_markdown_file(file_path, url_mappings, base_dir):
    """Process a single markdown file."""
    print(f"Processing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract metadata (YAML front matter)
    metadata_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    metadata = ''
    if metadata_match:
        metadata = metadata_match.group(0)
        content = content[len(metadata):]
    
    # Calculate relative file path from base directory (for URL replacement)
    rel_file_path = os.path.relpath(file_path, base_dir)
    
    # Replace URLs with relative paths in HTML (before conversion)
    content = replace_urls_with_relative_paths(content, url_mappings, rel_file_path)
    
    # Remove DOCTYPE and html/head tags
    content = re.sub(r'<!DOCTYPE[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<html[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</html>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<head[^>]*>.*?</head>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Extract body content if present
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
    if body_match:
        content = body_match.group(1)
    
    # Remove anchor tags without content
    content = re.sub(r'<a name="[^"]*"></a>', '', content)
    
    # Convert HTML to Markdown
    markdown_content = convert_html_to_markdown(content)
    
    # Replace URLs with relative paths in markdown (after conversion)
    markdown_content = replace_urls_with_relative_paths(markdown_content, url_mappings, rel_file_path)
    
    # Combine metadata and content
    final_content = metadata + '\n' + markdown_content if metadata else markdown_content
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"Completed: {file_path}")


def main():
    """Main function to process all markdown files."""
    base_dir = Path(__file__).parent.resolve()
    
    # Load URL mappings
    docs_json_path = base_dir / 'docs.json'
    if not docs_json_path.exists():
        print(f"Error: {docs_json_path} not found")
        return
    
    print("Loading URL mappings from docs.json...")
    url_mappings = load_url_mappings(docs_json_path)
    print(f"Loaded {len(url_mappings)} URL mappings")
    
    # Target directories
    target_dirs = [
        'Ascend C 算子开发',
        'Ascend C API',
        'Ascend C 最佳实践',
        '算子开发工具'
    ]
    
    # Process all markdown files in target directories
    for dir_name in target_dirs:
        dir_path = base_dir / dir_name
        if not dir_path.exists():
            print(f"Warning: Directory not found: {dir_path}")
            continue
        
        print(f"\nProcessing directory: {dir_name}")
        
        # Find all markdown files
        md_files = list(dir_path.rglob('*.md'))
        print(f"Found {len(md_files)} markdown files")
        
        for md_file in md_files:
            try:
                process_markdown_file(md_file, url_mappings, base_dir)
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
                import traceback
                traceback.print_exc()
    
    print("\nConversion completed!")


if __name__ == '__main__':
    main()
