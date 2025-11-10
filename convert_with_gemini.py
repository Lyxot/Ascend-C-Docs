#!/usr/bin/env python3
"""
使用 Google Gemini CLI 将 HTML 转换为 Markdown
"""

import argparse
import subprocess
import sys
import os
import re
import json
from pathlib import Path


def convert_html_to_markdown(content, model="gemini-2.5-flash", verbose=True, output_file=None, debug=False, project=None):
    """
    使用 Gemini CLI 将 HTML 内容转换为 Markdown
    
    Args:
        content: 要转换的 HTML 内容（字符串）
        model: Gemini 模型名称，默认 "gemini-2.5-flash"
        verbose: 是否显示详细进度信息，默认 True
        output_file: 输出文件路径，如果指定则实时写入文件
        debug: 调试模式，显示原始输出
        project: Google Cloud Project ID，如果未指定则从环境变量获取
    
    Returns:
        str: 转换后的 Markdown 内容，失败时返回 None
    """
    # 构建系统提示词
    system_prompt = """用户会给出一个内嵌HTML标签的Markdown文档，严格遵守以下规则对它做出修改:
1. 保留原metadata,添加新metadata: `converted: true`,不要遗漏metadata后的`---`
2. 不要修改文档的结构,不要对内容做任何改动
3. 对于源码中的HTML table,直接在Markdown中嵌入整个table部分的原始HTML源码即可,但是需要移除标签中的id等无关的属性并适当压缩行数(表格的一行写在源码的同一行里),不需要引用在代码块中;代码块可能以<table class="highlighttable">的形式存储,这种方式存储的代码块的外层div会标明编程语言(如<div codetype="Cpp">),需要转换为Markdown代码块
4. 将其它内嵌的HTML语法转换为对应的Markdown语法
5. 在Markdown中嵌入HTML时,HTML本身不能包含Markdown语法(比如不能有`**`在HTML里);不要在Markdown代码块中使用粗体、斜体等语法(比如不能有`**`在代码块里)
6. 对于多层的Markdown嵌套结构,确保正确处理缩进和层级关系,缩进使用2个空格表示一个层级
7. 原文中可能用abcde等字母表示列表项,将它们转为对应的数字列表项(1., 2., 3., ...)
8. 如果文章以`父主题：...`结尾,将其提取到metadata中的`parent_topic`字段中,并删除正文中的该行

回复时,只需要回复Markdown源码即可,不需要引用在代码块里。

以下为Markdown文档:

"""
    
    # 构建完整的 prompt
    full_prompt = system_prompt + content
    
    # 转义单引号以避免 shell 问题
    escaped_prompt = full_prompt.replace("'", "'\\''")
    
    # 获取 Google Cloud Project ID
    gcp_project = project if project else os.environ.get('GOOGLE_CLOUD_PROJECT', '')
    
    # 构建命令
    if gcp_project:
        cmd = f"GOOGLE_CLOUD_PROJECT={gcp_project} gemini --model {model} --prompt '{escaped_prompt}'"
    else:
        cmd = f"gemini --model {model} --prompt '{escaped_prompt}'"
    
    if verbose and not debug:
        print(f"正在调用 Gemini CLI (模型: {model})...")
    
    if debug:
        print(f"[DEBUG] 命令: {cmd[:200]}...")
        print(f"[DEBUG] Prompt 长度: {len(full_prompt)} 字符")
    
    try:
        # 执行命令
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if debug:
            print(f"[DEBUG] 返回码: {result.returncode}")
            print(f"[DEBUG] 原始输出长度: {len(result.stdout)} 字符")
            print(f"[DEBUG] 原始输出前200字符: {result.stdout[:200]}")
        
        if result.returncode != 0:
            print(f"错误: Gemini CLI 执行失败")
            if debug or verbose:
                print(f"stderr: {result.stderr}")
            return None
        
        # 获取输出
        output = result.stdout
        
        # 去除 "Loaded cached credentials." 前缀
        # Gemini CLI 的输出格式为：
        # Loaded cached credentials.
        # <实际内容>
        if output.startswith("Loaded cached credentials."):
            # 移除第一行
            lines = output.split('\n', 1)
            if len(lines) > 1:
                converted_content = lines[1].lstrip('\n')
            else:
                converted_content = ""
        else:
            converted_content = output
        
        # 去除 Markdown 代码块标记（如果存在）
        # 有些模型可能会将输出包裹在 ```markdown ... ``` 或 ``` ... ``` 中
        # 先去除末尾的空行，再检查代码块标记
        converted_content = converted_content.rstrip('\n')
        
        if converted_content.startswith('```markdown'):
            # 移除开头的 ```markdown 和换行
            converted_content = converted_content[len('```markdown'):].lstrip('\n')
            
            # 移除结尾的 ```
            if converted_content.endswith('```'):
                converted_content = converted_content[:-3].rstrip('\n')
            
            if debug:
                print(f"[DEBUG] 检测到并移除了 ```markdown 代码块标记")
        elif converted_content.startswith('```'):
            # 移除开头的 ``` 和换行
            converted_content = converted_content[len('```'):].lstrip('\n')
            
            # 移除结尾的 ```
            if converted_content.endswith('```'):
                converted_content = converted_content[:-3].rstrip('\n')
            
            if debug:
                print(f"[DEBUG] 检测到并移除了 ``` 代码块标记")
        
        if debug:
            print(f"[DEBUG] 转换后内容长度: {len(converted_content)} 字符")
            print(f"[DEBUG] 转换后内容前200字符: {converted_content[:200]}")
        
        # 如果指定了输出文件，写入文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(converted_content)
            if verbose and not debug:
                print(f"✓ 已保存到: {output_file}")
        
        if verbose and not debug:
            line_count = converted_content.count('\n') + 1
            print(f"转换完成! 输出 {line_count} 行 {len(converted_content)} 字符")
        
        return converted_content
        
    except Exception as e:
        print(f"错误: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return None


def check_already_converted(content):
    """
    检查文件的 metadata 中是否已标记为 converted: true
    
    Args:
        content: 文件内容（字符串）
    
    Returns:
        bool: 如果 converted 为 true 返回 True，否则返回 False
    """
    # 匹配 YAML front matter
    pattern = r'^---\s*\n(.*?)\n---'
    match = re.match(pattern, content, re.DOTALL)
    
    if match:
        metadata = match.group(1)
        # 检查是否有 converted: true
        if re.search(r'^\s*converted\s*:\s*true\s*$', metadata, re.MULTILINE | re.IGNORECASE):
            return True
    
    return False


def convert_file_with_gemini(file_path, model="gemini-2.5-flash", output_path=None, force=False, debug=False, project=None):
    """
    使用 Gemini CLI 将文件转换为 Markdown
    
    Args:
        file_path: 要转换的文件路径
        model: Gemini 模型名称
        output_path: 输出文件路径
        force: 强制转换，即使已标记为已转换
        debug: 调试模式
        project: Google Cloud Project ID
    
    Returns:
        str: 转换后的 Markdown 内容，失败时返回 None
        'skipped': 如果文件已转换且未强制转换
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 {file_path}")
        return None
    
    # 读取文件内容
    print(f"读取文件: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"错误: 读取文件失败 {e}")
        return None
    
    # 检查是否已转换（除非强制转换）
    if not force and check_already_converted(content):
        print(f"⊘ 文件已转换过，跳过: {file_path}")
        return 'skipped'
    
    # 调用核心转换函数
    if not debug:
        print(f"调用模型: {model}")
        print(f"文件大小: {len(content)} 字符")
    else:
        print(f"[DEBUG] 调用模型: {model}")
        print(f"[DEBUG] 文件大小: {len(content)} 字符")
    
    try:
        converted_content = convert_html_to_markdown(content, model, verbose=True, output_file=output_path, debug=debug, project=project)
        
        if not converted_content:
            print("警告: 模型返回空内容")
            return None
        
        return converted_content
        
    except Exception as e:
        print(f"错误: {e}")
        return None


def collect_files_from_json(json_path, limit=None):
    """
    从 docs.json 文件中读取并构建文件路径列表
    
    Args:
        json_path: docs.json 文件路径
        limit: 限制处理的文件数量，None 表示处理全部
    
    Returns:
        list: 文件路径列表
    """
    if not os.path.exists(json_path):
        print(f"错误: JSON 文件不存在: {json_path}")
        return []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            docs = json.load(f)
    except Exception as e:
        print(f"错误: 读取 JSON 文件失败: {e}")
        return []
    
    file_paths = []
    base_dir = os.path.dirname(json_path)
    
    # 处理每个文档条目
    count = 0
    for doc in docs:
        if limit and count >= limit:
            break
            
        # 构建文件路径：main_section/parent_sections/filename.md
        main_section = doc.get('main_section', '')
        parent_sections = doc.get('parent_sections', [])
        filename = doc.get('filename', '')
        
        if not main_section or not filename:
            continue
        
        # 构建完整路径
        path_parts = [base_dir, main_section] + parent_sections + [filename]
        file_path = os.path.join(*path_parts)
        
        # 检查文件是否存在
        if os.path.exists(file_path):
            file_paths.append(file_path)
            count += 1
        else:
            print(f"警告: 文件不存在，跳过: {file_path}")
    
    return file_paths


def process_files(file_paths, model="gemini-2.5-flash", output_dir=None, overwrite=False, force=False, debug=False, project=None):
    """
    批量处理多个文件
    
    Args:
        file_paths: 文件路径列表
        model: Gemini 模型名称
        output_dir: 输出目录（None表示原地覆盖）
        overwrite: 是否覆盖原文件
        force: 强制转换，即使文件已标记为已转换
        debug: 调试模式
        project: Google Cloud Project ID
    
    Returns:
        tuple: (成功数, 失败数, 跳过数)
    """
    total = len(file_paths)
    success = 0
    failed = 0
    skipped = 0
    
    print(f"\n找到 {total} 个文件待处理")
    print("=" * 60)
    
    for i, file_path in enumerate(file_paths, 1):
        print(f"\n[{i}/{total}] 处理: {file_path}")
        
        # 确定输出路径
        if output_dir:
            # 保持相对目录结构
            rel_path = os.path.relpath(file_path, os.path.dirname(file_paths[0]))
            output_path = os.path.join(output_dir, rel_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        elif overwrite:
            output_path = file_path
        else:
            # 默认添加 .converted.md 后缀
            base_path = os.path.splitext(file_path)[0]
            output_path = f"{base_path}.converted.md"
        
        # 检查是否需要跳过（文件已存在且不是覆盖模式）
        if not overwrite and os.path.exists(output_path) and output_path != file_path:
            print(f"⊘ 已存在，跳过: {output_path}")
            skipped += 1
            continue
        
        # 转换文件
        try:
            converted_content = convert_file_with_gemini(file_path, model, output_path=output_path, force=force, debug=debug, project=project)
            
            if converted_content == 'skipped':
                skipped += 1
            elif converted_content:
                success += 1
                print(f"✓ 成功")
            else:
                failed += 1
                print(f"✗ 失败")
        except Exception as e:
            failed += 1
            print(f"✗ 失败: {e}")
    
    # 打印汇总
    print("\n" + "=" * 60)
    print(f"处理完成!")
    print(f"总计: {total} 个文件")
    print(f"成功: {success} 个")
    print(f"失败: {failed} 个")
    print(f"跳过: {skipped} 个")
    
    return (success, failed, skipped)


def main():
    parser = argparse.ArgumentParser(
        description='使用 Google Gemini CLI 将 HTML 转换为 Markdown'
    )
    parser.add_argument(
        '-o', '--output',
        help='输出文件或目录路径（默认：原地覆盖或添加 .converted.md 后缀）'
    )
    parser.add_argument(
        '-m', '--model',
        default='gemini-2.5-flash',
        help='Gemini 模型名称（默认: gemini-2.5-flash）'
    )
    parser.add_argument(
        '-p', '--project',
        help='Google Cloud Project ID（如果未指定，则从环境变量 GOOGLE_CLOUD_PROJECT 获取）'
    )
    parser.add_argument(
        '--from-json',
        dest='json_file',
        help='从 JSON 文件读取文件列表（如 docs.json）'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='限制处理前 N 个文件（仅在使用 --from-json 时有效）'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='覆盖原文件（危险操作，请谨慎使用）'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制转换，即使文件 metadata 中标记为已转换'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='只显示将要转换的文件，不实际执行'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='调试模式，显示详细的调试信息'
    )
    
    args = parser.parse_args()
    
    # 收集文件
    file_paths = []
    
    if args.json_file:
        # 从 JSON 文件读取
        json_path = os.path.abspath(args.json_file)
        print(f"从 JSON 文件读取: {json_path}")
        if args.limit:
            print(f"限制处理前 {args.limit} 个文件")
        file_paths = collect_files_from_json(json_path, args.limit)
    else:
        print("错误: 必须使用 --from-json 指定 JSON 文件")
        sys.exit(1)
    
    if not file_paths:
        print(f"错误: 没有找到匹配的文件")
        sys.exit(1)
    
    if args.dry_run:
        print(f"[DRY RUN] 找到 {len(file_paths)} 个文件:")
        for i, fp in enumerate(file_paths, 1):
            print(f"  [{i}] {fp}")
        print(f"\n模型: {args.model}")
        print(f"覆盖模式: {'是' if args.overwrite else '否'}")
        print(f"强制转换: {'是' if args.force else '否'}")
        if args.limit:
            print(f"限制数量: {args.limit}")
        sys.exit(0)
    
    # 批量处理文件
    output_dir = args.output if args.output else None
    process_files(file_paths, args.model, output_dir, args.overwrite, args.force, args.debug, args.project)


if __name__ == '__main__':
    main()
