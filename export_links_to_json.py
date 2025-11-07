#!/usr/bin/env python3
"""
导出 docs.md 中的所有链接信息为 JSON 格式
包括：章节、子章节、原始链接等信息
"""

import os
import re
import json
import argparse
from typing import List, Dict


def sanitize_filename(name: str) -> str:
    """清理文件名，替换非法字符"""
    # 替换斜杠为下划线
    return name.replace('/', '_')


def parse_docs_md(file_path: str) -> List[Dict]:
    """解析 docs.md 文件，提取所有链接及其章节层级信息"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    links = []
    section_map = {}  # 章节号到标题的映射
    current_h2 = None  # 当前的二级标题
    current_path = []  # 用于跟踪当前的章节路径
    
    for line_num, line in enumerate(lines, 1):
        # 检查是否是二级标题
        if line.strip().startswith('##'):
            h2_title = line.strip()[2:].strip()
            current_h2 = h2_title
            section_map = {}  # 每个二级标题有自己的section_map
            current_path = []
            continue
        
        # 如果没有当前二级标题，跳过
        if not current_h2:
            continue
        
        # 跳过非列表项
        if not line.strip().startswith('*'):
            continue
        
        # 计算缩进级别（每4个空格为一级）
        indent = (len(line) - len(line.lstrip())) // 4
        
        # 提取链接 - 先检查是否有章节号
        # 格式可能是: "* 3.1. [HelloWorld](url)" 或 "    * 5.1. [SPMD模型](url)"
        section_match = re.search(r'\*\s+([\d.]+)\.\s+\[([^\]]+)\]\((https://[^\)]+)\)', line)
        if section_match:
            section_num = section_match.group(1).strip()
            link_title = section_match.group(2).strip()
            url = section_match.group(3).strip()
            
            # 完整标题包括章节号
            title = f"{section_num}. {link_title}"
            
            # 调整当前路径到正确的层级
            current_path = current_path[:indent]
            
            links.append({
                'main_section': current_h2,
                'full_title': title,
                'filename': sanitize_filename(title),
                'url': url,
                'parent_sections': current_path.copy()
            })
            continue
        
        # 如果没有章节号，尝试普通链接格式
        match = re.search(r'\[([^\]]+)\]\((https://[^\)]+)\)', line)
        if match:
            title = match.group(1).strip()
            url = match.group(2).strip()
            
            # 调整当前路径到正确的层级
            current_path = current_path[:indent]
            
            links.append({
                'main_section': current_h2,
                'full_title': title,
                'filename': sanitize_filename(title),
                'url': url,
                'parent_sections': current_path.copy()
            })
            continue
        
        # 如果是没有链接的章节标题（如 "3. 快速入门"）
        # 提取标题
        title_match = re.search(r'\*\s+([\d.]+)\.\s+(.+)', line)
        if title_match:
            number = title_match.group(1).strip()
            title = title_match.group(2).strip()
            full_title = f"{number}. {title}"
            current_path = current_path[:indent]
            current_path.append(full_title)
            # 记录到映射中
            section_map[number] = title
    
    return links


def export_to_json(links: List[Dict], output_file: str, pretty: bool = True):
    """导出链接信息到 JSON 文件"""
    
    # 直接导出链接列表
    with open(output_file, 'w', encoding='utf-8') as f:
        if pretty:
            json.dump(links, f, ensure_ascii=False, indent=2)
        else:
            json.dump(links, f, ensure_ascii=False)
    
    # 统计信息（用于显示）
    stats = {
        'total_links': len(links),
        'by_main_section': {}
    }
    
    # 统计各章节的链接数
    for link in links:
        main_section = link['main_section']
        stats['by_main_section'][main_section] = stats['by_main_section'].get(main_section, 0) + 1
    
    return stats


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='导出 docs.md 中的所有链接信息为 JSON 格式')
    parser.add_argument('-i', '--input', type=str, help='docs.md 文件路径（默认为当前目录下的 docs.md）')
    parser.add_argument('-o', '--output', type=str, help='输出 JSON 文件路径（默认为 links.json）')
    parser.add_argument('--compact', action='store_true', help='紧凑格式输出（不美化）')
    parser.add_argument('--filter-section', type=str, help='只导出指定章节的链接')
    args = parser.parse_args()
    
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置 docs.md 路径
    docs_md_path = args.input if args.input else os.path.join(script_dir, 'docs.md')
    docs_md_path = os.path.abspath(docs_md_path)
    
    # 设置输出路径
    output_file = args.output if args.output else os.path.join(script_dir, 'links.json')
    output_file = os.path.abspath(output_file)
    
    if not os.path.exists(docs_md_path):
        print(f"错误: 找不到文件 {docs_md_path}")
        return
    
    print(f"输入文件: {docs_md_path}")
    print(f"输出文件: {output_file}")
    
    # 解析 docs.md
    print("\n解析 docs.md...")
    links = parse_docs_md(docs_md_path)
    print(f"找到 {len(links)} 个链接")
    
    # 过滤章节（如果指定）
    if args.filter_section:
        original_count = len(links)
        links = [link for link in links if link['main_section'] == args.filter_section]
        print(f"过滤到章节 '{args.filter_section}': {len(links)} 个链接")
        if len(links) == 0:
            print(f"\n可用的章节:")
            sections = set(link['main_section'] for link in parse_docs_md(docs_md_path))
            for section in sorted(sections):
                print(f"  - {section}")
            return
    
    # 导出到 JSON
    print("\n导出到 JSON...")
    stats = export_to_json(links, output_file, pretty=not args.compact)
    
    # 显示统计信息
    print("\n" + "="*60)
    print("导出完成！")
    print(f"总链接数: {stats['total_links']}")
    print("\n各章节链接数:")
    for section, count in stats['by_main_section'].items():
        print(f"  {section}: {count}")
    print("="*60)
    
    # 显示示例数据
    if links:
        print("\n示例链接数据:")
        print(json.dumps(links[0], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
