# Ascend C 文档下载和导出工具

本目录包含两个脚本，用于处理 `docs.md` 中的文档链接。

## 脚本说明

### 1. download_and_convert.py - 下载HTML文档

下载 `docs.md` 中的所有链接，将HTML源码保存为Markdown文件。

**功能特点：**
- 支持所有4个章节（Ascend C 算子开发、API、最佳实践、开发工具）
- 自动创建层级目录结构
- 转换相对URL为绝对URL
- 添加元数据（源链接）
- 保持原始HTML内容不变

**使用示例：**

```bash
# 1. 测试模式 - 只显示将要创建的文件路径
python download_and_convert.py --dry-run -o test

# 2. 下载前100个文件（测试）
python download_and_convert.py -n 100 -o test

# 3. 下载所有1265个文件到当前目录
python download_and_convert.py

# 4. 下载到指定目录
python download_and_convert.py -o /path/to/output

# 5. 使用自定义的docs.md文件
python download_and_convert.py -i custom_docs.md -o output
```

**参数说明：**
- `-o, --output`: 输出目录路径
- `-i, --input`: docs.md 文件路径
- `-n, --limit`: 只下载前N个链接（用于测试）
- `--dry-run`: 只显示路径，不实际下载

**输出结构示例：**

```
output/
├── Ascend C 算子开发/
│   ├── 1. Ascend C简介.md
│   ├── 3. 快速入门/
│   │   ├── 3.1. HelloWorld.md
│   │   └── 3.2. 基于Kernel直调工程的算子开发.md
│   └── 6. 算子实现/
│       └── 6.2. 矢量编程/
│           └── 6.2.4. 多核&Tiling切分/
│               └── 6.2.4.1. 概述.md
├── Ascend C API/
│   ├── 1. Ascend C API列表.md
│   └── 3. 数据类型定义/
│       └── 3.1. LocalTensor/
│           └── 3.1.1. 简介.md
├── Ascend C 最佳实践/
│   └── 3. 功能调试/
│       └── 3.1. 运行正常.md
└── 算子开发工具/
    └── 3. 算子设计（msKPP）/
        └── 3.3. 性能建模/
            └── 3.3.1. 原理概述.md
```

**文件格式：**

每个Markdown文件包含：

```markdown
---
source: https://www.hiascend.com/doc_center/source/...
---

<!doctype html>
<html>
...原始HTML内容（相对URL已转为绝对URL）...
</html>
```

---

### 2. export_links_to_json.py - 导出链接信息

将 `docs.md` 中的所有链接信息导出为JSON格式，便于分析和处理。

**功能特点：**
- 导出所有链接的详细信息
- 包含章节、子章节、面包屑导航
- 支持过滤特定章节
- 提供统计信息

**使用示例：**

```bash
# 1. 导出所有链接到 links.json
python export_links_to_json.py -o links.json

# 2. 只导出"Ascend C API"章节
python export_links_to_json.py --filter-section "Ascend C API" -o api_links.json

# 3. 紧凑格式输出（不美化）
python export_links_to_json.py --compact -o links.json

# 4. 使用自定义的docs.md文件
python export_links_to_json.py -i custom_docs.md -o links.json
```

**参数说明：**
- `-o, --output`: 输出JSON文件路径（默认: links.json）
- `-i, --input`: docs.md 文件路径
- `--compact`: 紧凑格式输出（不美化）
- `--filter-section`: 只导出指定章节的链接

**JSON格式说明：**

```json
[
  {
    "main_section": "Ascend C 算子开发",
    "full_title": "1. Ascend C简介",
    "url": "https://www.hiascend.com/doc_center/source/zh/CANNCommunityEdition/82RC1/opdevg/Ascendcopdevg/atlas_ascendc_10_0001.html",
    "parent_sections": []
  },
  {
    "main_section": "Ascend C 算子开发",
    "full_title": "6.2.4.1. 概述",
    "url": "https://www.hiascend.com/doc_center/source/zh/CANNCommunityEdition/82RC1/opdevg/Ascendcopdevg/atlas_ascendc_10_10005.html",
    "parent_sections": [
      "6. 算子实现",
      "6.2. 矢量编程",
      "6.2.4. 多核&Tiling切分"
    ]
  }
]
```

**字段说明：**
- `main_section`: 主章节（二级标题）
- `full_title`: 完整标题（含章节编号）
- `url`: 原始链接
- `parent_sections`: 父章节列表（从根到当前的完整路径）

---

## 统计信息

基于 `docs.md`（CANN 社区版 8.2.RC1）：

| 章节 | 链接数 |
|------|--------|
| Ascend C 算子开发 | 97 |
| Ascend C API | 944 |
| Ascend C 最佳实践 | 35 |
| 算子开发工具 | 189 |
| **总计** | **1265** |

---

## 环境要求

- Python 3.6+
- 虚拟环境（可选，建议使用）

**安装依赖：**

```bash
# 如果没有虚拟环境，创建一个
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 两个脚本都只使用Python标准库，无需安装额外依赖
```

---

## 常见问题

### 1. 下载失败或超时

部分链接可能因为网络问题下载失败，脚本会跳过并在最后显示统计信息。可以重新运行脚本，已下载的文件会被跳过。

### 2. 文件名过长

某些文件系统（如Windows）可能对路径长度有限制。可以使用较短的输出目录名。

### 3. 查看可用章节

如果使用 `--filter-section` 但不确定章节名，运行时不指定章节名会列出所有可用章节：

```bash
python export_links_to_json.py --filter-section ""
```

---

## 示例工作流

### 完整下载流程

```bash
# 1. 先导出JSON查看结构
python export_links_to_json.py -o links.json

# 2. 测试下载前10个文件
python download_and_convert.py --dry-run -n 10 -o test

# 3. 确认无误后，下载所有文件
python download_and_convert.py -o docs_html

# 4. 检查下载结果
find docs_html -name "*.md" | wc -l
```

### 只处理特定章节

```bash
# 1. 导出API章节的链接信息
python export_links_to_json.py --filter-section "Ascend C API" -o api_links.json

# 2. 手动编辑 docs.md，只保留API章节
# 或者创建一个只包含API章节的新文件

# 3. 下载该章节的文档
python download_and_convert.py -i api_docs.md -o api_output
```

---

## 许可和版权

这些脚本用于个人学习和研究目的。下载的文档内容版权归华为技术有限公司所有。
