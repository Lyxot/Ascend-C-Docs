#!/usr/bin/env python3
"""
Manually process the first 11 files by carefully converting HTML to Markdown.
This script processes each file individually with explicit conversion logic.
"""

import re
from pathlib import Path

def manual_html_to_markdown(content):
    """
    Manually convert HTML to Markdown with careful, explicit rules.
    - Remove HTML boilerplate (doctype, html, head, body)
    - Convert headings (h1-h6) to Markdown
    - Convert paragraphs (p) to plain text
    - Convert lists (ul, li) to Markdown
    - Convert links (a) to Markdown
    - Keep img and map tags as HTML (complex)
    - Keep table tags as HTML but remove id/class attributes
    - Remove all id, class attributes from tags
    """
    
    # Extract metadata
    metadata_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    metadata = ''
    if metadata_match:
        metadata = metadata_match.group(0)
        content = content[len(metadata):]
    
    # Remove DOCTYPE, html, head tags
    content = re.sub(r'<!DOCTYPE[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<html[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</html>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<head[^>]*>.*?</head>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove body tags
    content = re.sub(r'<body[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</body>', '', content, flags=re.IGNORECASE)
    
    # Remove anchor tags without content
    content = re.sub(r'<a name="[^"]*"></a>', '', content)
    
    # Remove empty div tags and section wrappers
    content = re.sub(r'<div[^>]*>\s*</div>', '', content)
    content = re.sub(r'<div[^>]*>', '', content)
    content = re.sub(r'</div>', '', content)
    
    # Convert headings h1-h6 to Markdown
    content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\n# \1\n', content, flags=re.DOTALL)
    content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n## \1\n', content, flags=re.DOTALL)
    content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n### \1\n', content, flags=re.DOTALL)
    content = re.sub(r'<h4[^>]*>(.*?)</h4>', r'\n#### \1\n', content, flags=re.DOTALL)
    content = re.sub(r'<h5[^>]*>(.*?)</h5>', r'\n##### \1\n', content, flags=re.DOTALL)
    content = re.sub(r'<h6[^>]*>(.*?)</h6>', r'\n###### \1\n', content, flags=re.DOTALL)
    
    # Convert paragraphs - remove p tags but keep content
    content = re.sub(r'<p[^>]*>', '\n\n', content)
    content = re.sub(r'</p>', '\n', content)
    
    # Convert strong/b tags to Markdown
    content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', content, flags=re.DOTALL)
    content = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', content, flags=re.DOTALL)
    
    # Convert em/i tags to Markdown  
    content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', content, flags=re.DOTALL)
    content = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', content, flags=re.DOTALL)
    
    # Convert code tags
    content = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', content, flags=re.DOTALL)
    
    # Convert links - extract href and text
    def convert_link(match):
        full_tag = match.group(0)
        href_match = re.search(r'href="([^"]*)"', full_tag)
        href = href_match.group(1) if href_match else ''
        text_match = re.search(r'>(.*?)</a>', full_tag, re.DOTALL)
        text = text_match.group(1) if text_match else ''
        if href:
            return f'[{text}]({href})'
        return text
    
    content = re.sub(r'<a[^>]*>.*?</a>', convert_link, content, flags=re.DOTALL)
    
    # Convert lists - ul/ol/li to Markdown
    def convert_list_item(match):
        text = match.group(1)
        # Remove nested spans and other tags
        text = re.sub(r'<[^>]+>', '', text)
        return f'* {text.strip()}'
    
    # First, handle li tags
    content = re.sub(r'<li[^>]*>(.*?)</li>', convert_list_item, content, flags=re.DOTALL)
    
    # Remove ul/ol tags
    content = re.sub(r'<ul[^>]*>', '\n', content)
    content = re.sub(r'</ul>', '\n', content)
    content = re.sub(r'<ol[^>]*>', '\n', content)
    content = re.sub(r'</ol>', '\n', content)
    
    # Clean up span, term tags - just remove them
    content = re.sub(r'<span[^>]*>', '', content)
    content = re.sub(r'</span>', '', content)
    content = re.sub(r'<term[^>]*>', '', content)
    content = re.sub(r'</term>', '', content)
    
    # Remove id attributes from img and map tags
    content = re.sub(r'<img([^>]*)\sid="[^"]*"', r'<img\1', content)
    content = re.sub(r'<map([^>]*)\sid="[^"]*"', r'<map\1', content)
    content = re.sub(r'<area([^>]*)\sid="[^"]*"', r'<area\1', content)
    
    # For tables, remove id/class but keep structure
    content = re.sub(r'<table([^>]*)\sid="[^"]*"', r'<table\1', content)
    content = re.sub(r'<table([^>]*)\sclass="[^"]*"', r'<table\1', content)
    content = re.sub(r'<([a-z]+)([^>]*)\sid="[^"]*"', r'<\1\2', content)
    content = re.sub(r'<([a-z]+)([^>]*)\sclass="[^"]*"', r'<\1\2', content)
    content = re.sub(r'<([a-z]+)([^>]*)\scodetype="[^"]*"', r'<\1\2', content)
    
    # Clean up multiple newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Combine metadata and content
    result = metadata + '\n' + content.strip() + '\n'
    
    return result


def process_file(filepath):
    """Process a single file manually."""
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    converted = manual_html_to_markdown(content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(converted)
    
    print(f"Completed: {filepath}")


def main():
    """Process the first 11 files."""
    files_to_process = [
        "Ascend C 算子开发/1. Ascend C简介.md",
        "Ascend C 算子开发/2. 环境准备.md",
        "Ascend C 算子开发/3. 快速入门/3.1. HelloWorld.md",
        "Ascend C 算子开发/3. 快速入门/3.2. 基于Kernel直调工程的算子开发.md",
        "Ascend C 算子开发/3. 快速入门/3.3. 基于自定义算子工程的算子开发.md",
        "Ascend C 算子开发/4. 抽象硬件架构.md",
        "Ascend C 算子开发/5. 编程模型/5.1. SPMD模型.md",
        "Ascend C 算子开发/5. 编程模型/5.2. 核函数.md",
        "Ascend C 算子开发/5. 编程模型/5.3. 编程范式.md",
        "Ascend C 算子开发/5. 编程模型/5.4. 编程接口概述.md",
        "Ascend C 算子开发/6. 算子实现/6.1. 概述.md",
    ]
    
    for filepath in files_to_process:
        try:
            process_file(filepath)
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\nManual processing of 11 files completed!")


if __name__ == '__main__':
    main()
