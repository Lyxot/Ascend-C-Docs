# Directory Overview

This directory  contains documentation for Ascend C operator development, based on the CANN Community Edition 8.2.RC1.

# Key Files

*   `docs.md`: The main entry point for the documentation, with links to different sections like "Ascend C 算子开发" (Ascend C Operator Development), "Ascend C API", and "Ascend C 最佳实践" (Ascend C Best Practices).

# TASK

打开 @docs.md 中所有的链接，对每一个链接按照以下步骤执行：
  1. 使用命令行工具，执行curl下载网页源码到临时文件 source.html 中
  2. 将网页源码中的使用相对路径的链接补全为完整链接
  3. 根据网页源码生成对应的markdown文档，要求为：完全按照文档的结构，将它转换为一个Markdown文档，并且不要对其中的内容做任何改动。对于源码中的表格元素(<table>)，直接在markdown中嵌入html源码即可
  4. 在生成的markdown文档顶部添加metadata用以记录原始文档的链接
  5. 按照 @docs.md 链接对应的章节名，来保存转换好的markdown文件，如： `1. [Ascend C简介](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/Ascendcopdevg/atlas_ascendc_10_0001.html)`保存为 `Ascend C 算子开发/1. AscendC简介.md`，`6.2.4.1. [概述](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/Ascendcopdevg/atlas_ascendc_10_10005.html)` 保存为 `Ascend C 算子开发/6. 算子实现/6.2. 矢量编程/6.2.4. 多核&Tiling切分/6.2.4.1. 概述.md`
  6. 继续处理下一个链接

要求**手动**处理所有链接，不要使用脚本及外部文档转换工具来完成这个任务，因为它们可能会引入格式错误。不计时间与token成本

# TASK

完全按照文档的结构，将嵌入markdown的html语法转换为Markdown语法，并且不要对其中的内容做任何改动。文档顶部有用以记录原始文档的链接的metadata，根据原始文档的链接，将文档中使用相对路径的链接/图片补全为完整url。对于源码中的表格元素(<table>)，直接在markdown中嵌入html源码即可，但是需要移除标签中的id