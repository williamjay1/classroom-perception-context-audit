# 2026-10-13 四张正文表格排版审查

来源：`D:\MLWork\BMC_Classroom_Revision_20261005\deliverables\latex\manuscript.tex`。本脚本仅生成替换块，未修改 manuscript.tex、正文、统计结果或结论。

## 已完成的表格设计

- 四表保持可编辑 LaTeX，使用 booktabs 三条主线、无竖线、无逐行网格。
- 表内文字和数值为 8.5 pt／11 pt 行距，表注为 7.5 pt／9.5 pt；不缩放整表，不栅格化。
- 所有表使用现有 31pc 的 textwidth；表格样式宏只在各 table 的局部分组中生效，不改变全局正文或 caption 格式。
- 表 1 用调查间留白与可换行文字列组织来源、结局和区间方法，人数列右对齐。
- 表 2 将重复 domain 标签提升为三个组标题，保留三个组内的 Within／Between／Contextual 行及原顺序；三个数值列按小数对齐。
- 表 3 保留所有 specification 原文与顺序，以留白区分既有连续块；区间拆为对齐的下、上界，中间仍显示 to。
- 表 4 保留八个来源原行名与原列顺序；每个估计及区间两行展示，点估计按固定小数位对齐；CI 用紧凑的数学 [下界, 上界]，不为正数补入固定符号占位。调查间及 ICCS 行间留白。
- 浮动位置由原 [h] 放宽为 [tbp]，允许正文顶／底或单独浮动页；不强制改变正文分页。

## 信息守恒核验

| 表 | 原数据行数 | 完全保留的数值 | Caption／footnotetext | 行名／行义与原顺序 |
|---|---:|---:|---|---|
| tab1 | 11 | 33 | 逐字一致 | 已通过结构化逐行断言 |
| tab2 | 9 | 27 | 逐字一致 | 已通过结构化逐行断言 |
| tab3 | 16 | 80 | 逐字一致 | 已通过结构化逐行断言 |
| tab4 | 8 | 80 | 逐字一致 | 已通过结构化逐行断言 |

合计 220 个数据数值逐 token、逐顺序核验，包含正负号和三位小数末尾零。表注中的数字与数学表达由原 footnotetext 完整复制并核验。原表的非数值标签也逐行解析并核验，表 2 的 domain 原文完整保存在对应组标题中。

## 集成与余下版面 QA

读取 `D:\MLWork\BMC_Classroom_Revision_20261005\results\visual_20261013_table_blocks.json`，把 `preamble` 加在 begin document 前；依次以 original 精确定位四表并替换为 replacement。每个 original 必须在当时的 manuscript.tex 中唯一匹配，不能按旧 Word 重建内容。

依赖 array、tabularx、siunitx 均已用本机 kpsewhich 确认存在。集成后需检查 LaTeX 日志的 table overfull／Float too large 报告，以及 PDF 中四表的列宽、数值对齐、表注归属和分页。源码与信息守恒核验已通过；候选 PDF 的编译和视觉核验记录见下节。

当前来源文件 SHA-256：`ec0969f47284b8a27e6e34a117b855d478360fbd2577a2a4665387439c6dfffe`。

## 已完成的候选 PDF 视觉核验

已只读检查候选主文 PDF 的第 6、11、12、14 页，及 CI 宏更新后的 `page_14_final.png`。四表均完整落在当前文本宽度内；没有列或数字裁切、重叠、竖线或密网格；表题与对应表注同页，表注完整。表 2 的组标题与九个 estimand 行归属清楚，表 3 的留白保留所有原行顺序，表 4 的更新后区间以数学方括号整齐显示，原来的 to 紧贴数字及正数符号占位已消除。没有进一步阻止交付的表格缺陷。

根代理最终重新编译成功：21 页，0 overfull、0 undefined；这里只记录与四表有关的排版检查，不扩展正文或统计审查。