#!/usr/bin/env python3
"""
从华为文档中心的目录 JSON 文件生成 Markdown 目录和更新 docs.json，并下载文档
支持任意的文档目录 JSON 文件（如 optool.json, opdevg.json 等）
"""

import os
import json
import re
import subprocess
import time
from pathlib import Path
import argparse
from urllib.parse import urljoin, urlparse


# URL 前缀
URL_PREFIX = "https://www.hiascend.com/doc_center/source"


def build_tree_structure(data):
    """从 JSON 的 directory 构建树形结构"""
    # 获取 directory 数组
    directory = data.get('data', {}).get('directory', [])
    
    # 构建 id 到节点的映射
    node_map = {}
    for node in directory:
        node_map[node['nodeId']] = node
    
    return node_map, directory


def extract_node_order(node_id):
    """从 nodeId 中提取排序用的数字（如 2065abecb77b4ef187c4165c6ff35931-123 -> 123）"""
    parts = node_id.split('-')
    if len(parts) > 1:
        try:
            return int(parts[-1])
        except ValueError:
            return 0
    return 0


def node_to_markdown(node, node_map, indent_level=0, parent_numbers=None):
    """将节点转换为 Markdown 格式"""
    if parent_numbers is None:
        parent_numbers = []
    
    # 生成章节号
    section_number = '.'.join(parent_numbers)
    
    # 生成缩进
    indent = '  ' * indent_level
    
    # 获取节点信息
    node_name = node.get('nodeName', '')
    node_url = node.get('nodeUrl', '')
    children = node.get('children', [])
    
    # 构建完整 URL
    full_url = f"{URL_PREFIX}/{node_url}" if node_url else ""
    
    # 生成当前节点的 Markdown
    if full_url:
        # 有链接的节点
        md_line = f"{indent}* {section_number}. [{node_name}]({full_url})\n"
    else:
        # 没有链接的节点（章节标题）
        md_line = f"{indent}* {section_number}. {node_name}\n"
    
    # 处理子节点
    children_md = ""
    if children:
        # 按 nodeId 的数字后缀排序子节点
        sorted_children = sorted(children, key=lambda x: extract_node_order(x['nodeId']))
        for i, child in enumerate(sorted_children, 1):
            child_numbers = parent_numbers + [str(i)]
            children_md += node_to_markdown(child, node_map, indent_level + 1, child_numbers)
    
    return md_line + children_md


def generate_markdown(json_data, main_section, output_path):
    """生成 Markdown 目录文件"""
    node_map, directory = build_tree_structure(json_data)
    
    # 生成 Markdown 内容
    md_content = "# " + main_section + "\n"
    
    # 遍历顶层节点（parentId 指向根节点）
    root_id = json_data.get('data', {}).get('loadingNode')
    top_level_nodes = [n for n in directory if n.get('parentId') == root_id]
    
    # 按 nodeId 的数字后缀排序
    top_level_nodes.sort(key=lambda x: extract_node_order(x['nodeId']))
    
    for i, node in enumerate(top_level_nodes, 1):
        md_content += node_to_markdown(node, node_map, 0, [str(i)])
    
    # 保存文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✓ 已生成 Markdown 文件: {output_path}")
    return md_content


def node_to_docs_json_entry(node, node_map, main_section, parent_sections=None, parent_numbers=None):
    """将节点转换为 docs.json 格式的条目"""
    if parent_sections is None:
        parent_sections = []
    if parent_numbers is None:
        parent_numbers = []
    
    entries = []
    
    # 生成章节号
    section_number = '.'.join(parent_numbers)
    
    # 获取节点信息
    node_name = node.get('nodeName', '')
    node_url = node.get('nodeUrl', '')
    children = node.get('children', [])
    
    # 构建完整 URL
    full_url = f"{URL_PREFIX}/{node_url}" if node_url else ""
    
    # 构建完整标题
    full_title = f"{section_number}. {node_name}" if section_number else node_name
    
    # 如果有 URL，创建条目
    if full_url:
        entry = {
            "main_section": main_section,
            "full_title": full_title,
            "filename": f"{full_title.replace('/', '_')}.md",
            "url": full_url,
            "parent_sections": parent_sections.copy()
        }
        entries.append(entry)
    
    # 处理子节点
    if children:
        # 如果当前节点没有 URL，它只是一个章节标题
        new_parent_sections = parent_sections.copy()
        if not full_url:
            new_parent_sections.append(full_title)
        
        # 按 nodeId 的数字后缀排序子节点
        sorted_children = sorted(children, key=lambda x: extract_node_order(x['nodeId']))
        for i, child in enumerate(sorted_children, 1):
            child_numbers = parent_numbers + [str(i)]
            child_entries = node_to_docs_json_entry(child, node_map, main_section, new_parent_sections, child_numbers)
            entries.extend(child_entries)
    
    return entries


def generate_section_json(json_data, main_section, output_path):
    """生成独立的章节 JSON 文件（如 算子开发工具.json）"""
    # 生成新的条目
    node_map, directory = build_tree_structure(json_data)
    root_id = json_data.get('data', {}).get('loadingNode')
    top_level_nodes = [n for n in directory if n.get('parentId') == root_id]
    
    # 按 nodeId 的数字后缀排序
    top_level_nodes.sort(key=lambda x: extract_node_order(x['nodeId']))
    
    new_entries = []
    for i, node in enumerate(top_level_nodes, 1):
        entries = node_to_docs_json_entry(node, node_map, main_section, [], [str(i)])
        new_entries.extend(entries)
    
    # 保存为新的 JSON 文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_entries, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 已生成 JSON 文件: {output_path} (包含 {len(new_entries)} 个条目)")
    return new_entries


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


def remove_unnecessary_attributes(html_content):
    """去除HTML标签中不影响显示的属性"""
    if not html_content:
        return html_content
    
    # 定义需要保留的属性列表
    keep_attributes = {
        'href', 'src', 'alt', 'title', 'class', 'style', 
        'width', 'height', 'type', 'name', 'value', 'placeholder',
        'colspan', 'rowspan', 'target', 'rel', 'loading',
        'srcset', 'sizes', 'media', 'content', 'charset',
        'method', 'action', 'for', 'checked', 'selected', 'disabled',
        'required', 'readonly', 'multiple', 'accept', 'autocomplete',
        'min', 'max', 'step', 'pattern', 'maxlength', 'minlength',
        'align', 'valign', 'border', 'cellpadding', 'cellspacing'
    }
    
    # 定义需要删除的属性模式（前缀匹配）
    remove_prefixes = ['data-', 'aria-', 'ng-', 'v-', 'x-', '@', ':']
    
    # 定义需要删除的具体属性
    remove_attributes = {
        'id', 'role', 'tabindex', 'draggable', 'contenteditable',
        'spellcheck', 'translate', 'dir', 'lang', 'accesskey',
        'contextmenu', 'dropzone', 'hidden', 'itemprop', 'itemscope',
        'itemtype', 'itemid', 'itemref'
    }
    
    def clean_tag(match):
        tag_content = match.group(0)
        tag_name_match = re.match(r'<(\w+)', tag_content)
        if not tag_name_match:
            return tag_content
        
        tag_name = tag_name_match.group(1)
        
        # 构建新的标签
        new_tag = f'<{tag_name}'
        
        # 处理每个属性
        for attr_match in re.finditer(r'(\w+(?:-\w+)*)(?:=((?:"[^"]*"|\'[^\']*\'|[^\s>]+)))?', tag_content[len(tag_name)+1:]):
            attr_name = attr_match.group(1)
            attr_value = attr_match.group(2) if attr_match.group(2) else None
            
            # 判断是否保留该属性
            should_keep = False
            
            # 检查是否在保留列表中
            if attr_name.lower() in keep_attributes:
                should_keep = True
            else:
                # 检查是否需要删除
                if attr_name.lower() in remove_attributes:
                    should_keep = False
                else:
                    # 检查前缀
                    should_remove = any(attr_name.startswith(prefix) for prefix in remove_prefixes)
                    should_keep = not should_remove
            
            if should_keep:
                if attr_value:
                    new_tag += f' {attr_name}={attr_value}'
                else:
                    new_tag += f' {attr_name}'
        
        # 处理自闭合标签
        if tag_content.endswith('/>'):
            new_tag += '/>'
        else:
            new_tag += '>'
        
        return new_tag
    
    # 匹配所有开始标签（包括自闭合标签）
    html_content = re.sub(r'<\w+[^>]*/?>', clean_tag, html_content)
    
    return html_content


def remove_useless_tags(html_content):
    """移除无用的HTML标签"""
    if not html_content:
        return html_content
    
    # 移除script标签
    html_content = re.sub(r'<script(?![^>]*type=["\']application/ld\+json["\'])[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # 移除style标签
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # 移除noscript标签
    html_content = re.sub(r'<noscript[^>]*>.*?</noscript>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # 移除注释
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    # 移除iframe
    html_content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # 移除空的span标签
    html_content = re.sub(r'<span\s*>(.*?)</span>', r'\1', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # 移除空的div标签
    html_content = re.sub(r'<div\s*>\s*</div>', '', html_content, flags=re.IGNORECASE)
    
    # 清理多余的空白行
    html_content = re.sub(r'\n\s*\n\s*\n', '\n\n', html_content)

    # 移除doctype声明
    html_content = re.sub(r'<!DOCTYPE[^>]*>', '', html_content, flags=re.IGNORECASE)
    
    return html_content


def convert_relative_urls(html_content, base_url):
    """将HTML中的相对URL转换为完整URL"""
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
    metadata = f"""---
source: {original_url}
---

"""
    return metadata + html_content


def build_file_path(entry, base_dir):
    """根据 docs.json 条目构建文件路径"""
    main_section = entry.get('main_section', '')
    filename = entry.get('filename', '')
    parent_sections = entry.get('parent_sections', [])
    
    # 构建目录路径
    dir_parts = [main_section.replace('/', '_')]
    
    # 添加父章节
    for section in parent_sections:
        dir_parts.append(section.replace('/', '_'))
    
    # 创建目录
    dir_path = os.path.join(base_dir, *dir_parts)
    os.makedirs(dir_path, exist_ok=True)
    
    # 构建文件路径
    file_path = os.path.join(dir_path, filename)
    
    return file_path


def download_documents(entries, base_dir, skip_existing=True):
    """下载所有文档"""
    total = len(entries)
    success = 0
    failed = 0
    skipped = 0
    
    for i, entry in enumerate(entries, 1):
        title = entry.get('full_title', '')
        url = entry.get('url', '')
        
        print(f"\n[{i}/{total}] 处理: {title}")
        print(f"URL: {url}")
        
        # 构建文件路径
        file_path = build_file_path(entry, base_dir)
        
        # 检查文件是否已存在
        if skip_existing and os.path.exists(file_path):
            print(f"⊘ 已存在，跳过: {file_path}")
            skipped += 1
            continue
        
        # 下载HTML
        html_content = download_html(url)
        if not html_content:
            print(f"✗ 下载失败，跳过: {title}")
            failed += 1
            continue
        
        # 移除无用的HTML标签
        html_content = remove_useless_tags(html_content)
        
        # 去除不必要的HTML属性
        html_content = remove_unnecessary_attributes(html_content)
        
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
        time.sleep(0.1)
    
    # 输出统计信息
    print("\n" + "="*60)
    print("下载完成统计:")
    print(f"  总计: {total}")
    print(f"  成功: {success}")
    print(f"  失败: {failed}")
    print(f"  跳过: {skipped}")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description='从华为文档中心的目录 JSON 文件生成 Markdown 目录和更新 docs.json，并下载文档',
        epilog='示例: python3 %(prog)s -i optool.json'
    )
    parser.add_argument('-i', '--input', type=str, required=True, help='输入的 JSON 文件路径（如 optool.json）')
    parser.add_argument('-o', '--output', type=str, help='输出目录路径（默认为当前目录）')
    parser.add_argument('--skip-md', action='store_true', help='跳过生成 Markdown 文件')
    parser.add_argument('--skip-json', action='store_true', help='跳过生成章节 JSON 文件')
    parser.add_argument('--skip-download', action='store_true', help='跳过下载文档')
    parser.add_argument('--force', action='store_true', help='强制重新下载已存在的文件')
    parser.add_argument('-n', '--limit', type=int, help='只下载前 N 个文档（用于测试）')
    parser.add_argument('--dry-run', action='store_true', help='只显示将要创建的文件路径，不实际下载')
    args = parser.parse_args()
    
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置输出目录
    output_dir = args.output if args.output else script_dir
    output_dir = os.path.abspath(output_dir)
    
    # 设置输入 JSON 路径
    input_json_path = args.input if os.path.isabs(args.input) else os.path.join(script_dir, args.input)
    
    if not os.path.exists(input_json_path):
        print(f"错误: 找不到文件 {input_json_path}")
        return
    
    print(f"输入文件: {input_json_path}")
    
    # 读取 JSON 文件
    with open(input_json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # 从 JSON 中提取主章节名称（data.nodeName）
    main_section = json_data.get('data', {}).get('nodeName', '')
    if not main_section:
        print("错误: 无法从 JSON 中提取主章节名称（data.nodeName）")
        return
    
    # 从输入文件名提取基础名（如 optool.json -> optool）
    base_name = os.path.splitext(os.path.basename(input_json_path))[0]
    
    # 生成 Markdown 文件名（将 / 替换为 _）
    markdown_filename = f"{main_section.replace('/', '_')}.md"
    
    print(f"主章节: {main_section}")
    print(f"输出目录: {output_dir}")
    
    # 生成 Markdown 文件
    if not args.skip_md:
        print(f"\n生成 Markdown 文件 ({markdown_filename})...")
        markdown_path = os.path.join(output_dir, markdown_filename)
        generate_markdown(json_data, main_section, markdown_path)
    
    # 生成章节 JSON 文件
    entries = []
    if not args.skip_json:
        # 将文件名中的 / 替换为 _
        json_filename = f"{main_section.replace('/', '_')}.json"
        print(f"\n生成章节 JSON 文件 ({json_filename})...")
        section_json_path = os.path.join(output_dir, json_filename)
        entries = generate_section_json(json_data, main_section, section_json_path)
    else:
        # 如果不生成 JSON，仍需要生成 entries 用于下载
        node_map, directory = build_tree_structure(json_data)
        root_id = json_data.get('data', {}).get('loadingNode')
        top_level_nodes = [n for n in directory if n.get('parentId') == root_id]
        
        # 按 nodeId 的数字后缀排序
        top_level_nodes.sort(key=lambda x: extract_node_order(x['nodeId']))
        
        for i, node in enumerate(top_level_nodes, 1):
            node_entries = node_to_docs_json_entry(node, node_map, main_section, [], [str(i)])
            entries.extend(node_entries)
    
    # 下载文档
    if not args.skip_download and entries:
        # 限制数量（如果指定了）
        if args.limit:
            entries = entries[:args.limit]
            print(f"\n限制处理前 {args.limit} 个文档")
        
        # 如果是 dry-run 模式，只显示路径
        if args.dry_run:
            print("\n[DRY RUN] 将要创建的文件路径：")
            for i, entry in enumerate(entries, 1):
                file_path = build_file_path(entry, output_dir)
                print(f"[{i}] {file_path}")
        else:
            print("\n开始下载文档...")
            download_documents(entries, output_dir, skip_existing=not args.force)
    
    print("\n完成!")


if __name__ == '__main__':
    main()
