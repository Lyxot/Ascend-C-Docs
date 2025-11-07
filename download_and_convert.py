#!/usr/bin/env python3
"""
下载 docs.md 中的所有链接，将HTML源码保存为Markdown文件（不做转换）
"""

import os
import re
import subprocess
from urllib.parse import urljoin, urlparse
import time
from pathlib import Path
import argparse


def parse_docs_md(file_path):
    """解析 docs.md 文件，提取所有链接及其章节层级和标题"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    links = []
    section_map = {}  # 章节号到标题的映射，如 {'6': '算子实现', '6.2': '矢量编程'}
    current_h2 = None  # 当前的二级标题（如 "Ascend C 算子开发"）
    current_path = []  # 用于跟踪当前的章节路径
    
    for line in lines:
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
                'title': title,
                'url': url,
                'path': current_path.copy(),
                'h2_section': current_h2,
                'level': indent,
                'section_map': section_map.copy()  # 保存当前章节的section_map
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
                'title': title,
                'url': url,
                'path': current_path.copy(),
                'h2_section': current_h2,
                'level': indent,
                'section_map': section_map.copy()  # 保存当前章节的section_map
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


def build_file_path(link_info, base_dir):
    """根据链接信息构建文件路径"""
    title = link_info['title']
    h2_section = link_info.get('h2_section', 'Ascend C 算子开发')  # 二级标题作为根目录
    section_map = link_info.get('section_map', {})  # 获取该链接所属章节的section_map
    
    # 基础目录使用二级标题，替换斜杠为下划线
    dir_parts = [h2_section.replace('/', '_')]
    
    # 从标题中提取章节号（如 "3.1. HelloWorld" -> "3.1"）
    title_match = re.match(r'^([\d.]+)\.\s+(.+)$', title)
    if title_match:
        section_num = title_match.group(1)
        clean_title = title_match.group(2)
        
        # 分解章节号 "3.1" -> ['3', '1']
        parts = section_num.split('.')
        
        # 构建完整的目录结构（不包括最后一级，最后一级是文件本身）
        for i in range(len(parts) - 1):
            # 构建当前层级的章节号，如 "3"
            current_num = '.'.join(parts[:i+1])
            
            # 从 section_map 中查找对应的标题
            if current_num in section_map:
                section_title = section_map[current_num].replace('/', '_')
                dir_parts.append(f"{current_num}. {section_title}")
            else:
                # 如果找不到，只使用章节号
                dir_parts.append(current_num)
        
        # 文件名使用完整的章节号和标题，替换斜杠为下划线
        clean_title_escaped = clean_title.replace('/', '_')
        file_name = f"{section_num}. {clean_title_escaped}.md"
    else:
        # 没有章节号，直接使用标题作为文件名，替换斜杠为下划线
        title_escaped = title.replace('/', '_')
        file_name = f"{title_escaped}.md"
    
    # 创建目录
    dir_path = os.path.join(base_dir, *dir_parts)
    os.makedirs(dir_path, exist_ok=True)
    
    # 构建完整文件路径
    file_path = os.path.join(dir_path, file_name)
    
    return file_path


def download_html(url):
    """使用curl下载HTML内容"""
    try:
        result = subprocess.run(
            ['curl', '-s', '-L', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
        else:
            print(f"下载失败 {url}: {result.stderr}")
            return None
    except Exception as e:
        print(f"下载异常 {url}: {e}")
        return None


def convert_relative_urls(html_content, base_url):
    """将HTML中的相对URL转换为完整URL（使用正则表达式）"""
    if not html_content:
        return html_content
    
    # 解析base URL
    parsed = urlparse(base_url)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"
    base_path = '/'.join(parsed.path.split('/')[:-1])
    
    # 转换href属性
    def replace_href(match):
        url = match.group(1)
        if url.startswith(('http://', 'https://', 'javascript:', 'mailto:')):
            return match.group(0)
        elif url.startswith('#'):
            return match.group(0)
        elif url.startswith('/'):
            return f'href="{base_domain}{url}"'
        else:
            return f'href="{base_domain}{base_path}/{url}"'
    
    # 转换src属性
    def replace_src(match):
        url = match.group(1)
        if url.startswith(('http://', 'https://', 'data:')):
            return match.group(0)
        elif url.startswith('#'):
            return match.group(0)
        elif url.startswith('/'):
            return f'src="{base_domain}{url}"'
        else:
            return f'src="{base_domain}{base_path}/{url}"'
    
    html_content = re.sub(r'href="([^"]+)"', replace_href, html_content)
    html_content = re.sub(r'src="([^"]+)"', replace_src, html_content)
    
    return html_content


def create_markdown_with_html(html_content, original_url):
    """创建包含HTML源码的Markdown文件，添加metadata"""
    # 添加metadata
    metadata = f"""---
source: {original_url}
---

"""
    
    return metadata + html_content


def process_links(links, base_dir):
    """处理所有链接"""
    total = len(links)
    success = 0
    failed = 0
    skipped = 0
    
    for i, link_info in enumerate(links, 1):
        title = link_info['title']
        url = link_info['url']
        
        print(f"\n[{i}/{total}] 处理: {title}")
        print(f"URL: {url}")
        
        # 构建文件路径
        file_path = build_file_path(link_info, base_dir)
        
        # 检查文件是否已存在
        if os.path.exists(file_path):
            print(f"⊘ 已存在，跳过: {file_path}")
            skipped += 1
            continue
        
        # 下载HTML
        html_content = download_html(url)
        if not html_content:
            print(f"✗ 下载失败，跳过: {title}")
            failed += 1
            continue
        
        # 转换相对URL为完整URL
        html_content = convert_relative_urls(html_content, url)
        
        # 创建包含HTML的Markdown文件
        markdown_content = create_markdown_with_html(html_content, url)
        
        # 保存文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"✓ 已保存: {file_path}")
            success += 1
        except Exception as e:
            print(f"✗ 保存失败: {e}")
            failed += 1
        
        # 避免请求过快
        time.sleep(0.5)
    
    # 输出统计信息
    print("\n" + "="*60)
    print("处理完成统计:")
    print(f"  总计: {total}")
    print(f"  成功: {success}")
    print(f"  失败: {failed}")
    print(f"  跳过: {skipped}")
    print("="*60)


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='下载并转换 docs.md 中的所有链接为 Markdown 文件')
    parser.add_argument('-o', '--output', type=str, help='输出目录路径（默认为当前目录）')
    parser.add_argument('-i', '--input', type=str, help='docs.md 文件路径（默认为当前目录下的 docs.md）')
    parser.add_argument('-n', '--limit', type=int, help='只下载前 N 个链接（用于测试）')
    parser.add_argument('--dry-run', action='store_true', help='只显示将要创建的文件路径，不实际下载')
    args = parser.parse_args()
    
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置输出目录
    output_dir = args.output if args.output else script_dir
    output_dir = os.path.abspath(output_dir)
    
    # 设置 docs.md 路径
    docs_md_path = args.input if args.input else os.path.join(script_dir, 'docs.md')
    docs_md_path = os.path.abspath(docs_md_path)
    
    if not os.path.exists(docs_md_path):
        print(f"错误: 找不到文件 {docs_md_path}")
        return
    
    print(f"输入文件: {docs_md_path}")
    print(f"输出目录: {output_dir}")
    
    # 解析 docs.md
    print("\n解析 docs.md...")
    links = parse_docs_md(docs_md_path)
    print(f"找到 {len(links)} 个链接")
    
    # 统计各章节的链接数
    section_counts = {}
    for link in links:
        h2 = link.get('h2_section', 'Unknown')
        section_counts[h2] = section_counts.get(h2, 0) + 1
    print("各章节链接数:")
    for section, count in section_counts.items():
        print(f"  {section}: {count}")
    
    # 限制链接数量（如果指定了）
    if args.limit:
        links = links[:args.limit]
        print(f"限制处理前 {args.limit} 个链接")
    
    # 如果是 dry-run 模式，只显示路径
    if args.dry_run:
        print("\n[DRY RUN] 将要创建的文件路径：")
        for i, link_info in enumerate(links, 1):
            file_path = build_file_path(link_info, output_dir)
            print(f"[{i}] {file_path}")
        print("\n完成!")
        return
    
    # 处理所有链接
    print("\n开始下载和转换...")
    process_links(links, output_dir)
    
    print("\n完成!")


if __name__ == '__main__':
    main()
