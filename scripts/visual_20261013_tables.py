"""Prepare editable, information-preserving LaTeX table replacements.

This script never edits the manuscript or changes statistical contents. It reads
the four current tables, verifies every retained row, and writes replacement
blocks plus an audit manifest for the integrating agent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]  # repository root; override with --project-root
DEFAULT_SOURCE = PROJECT / "deliverables" / "latex" / "manuscript.tex"
DEFAULT_OUTPUT = PROJECT / "results" / "visual_20261013_table_blocks.json"
DEFAULT_REVIEW = PROJECT / "results" / "visual_20261013_tables_review.md"

PREAMBLE = r"""% Local, editable table styling: no global body or caption changes.
\usepackage{array,tabularx,siunitx}
\newcommand{\BMCVisualTableStyle}{%
  \fontsize{8.5}{11}\selectfont
  \setlength{\tabcolsep}{3pt}%
  \renewcommand{\arraystretch}{1.08}%
  \setlength{\heavyrulewidth}{0.6pt}%
  \setlength{\lightrulewidth}{0.35pt}%
  \setlength{\aboverulesep}{3pt}%
  \setlength{\belowrulesep}{3.5pt}%
  \sisetup{detect-all,group-digits=false,table-number-alignment=right}%
}
\newcommand{\BMCVisualTableNotes}{%
  \fontsize{7.5}{9.5}\selectfont\raggedright
}
\newcommand{\BMCVisualEffect}[3]{%
  \begin{tabular}[t]{@{}c@{}}%
    \tablenum[table-format=-1.3,table-number-alignment=center]{#1}\\[1pt]
    \ensuremath{[#2,\,#3]}%
  \end{tabular}%
}
"""


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def braced_argument(text: str, command: str) -> str:
    """Return an exact command and its balanced braced argument."""
    start = text.index(command + "{")
    index = start + len(command)
    depth = 0
    for end in range(index, len(text)):
        char = text[end]
        if char == "{" and (end == 0 or text[end - 1] != "\\"):
            depth += 1
        elif char == "}" and (end == 0 or text[end - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[start : end + 1]
    raise ValueError(f"Unbalanced argument of {command}")


def parse_table(block: str) -> dict:
    label_match = re.search(r"\\label\{(tab[1-4])\}", block)
    if not label_match:
        raise ValueError("Missing expected table label")
    body = block.split(r"\midrule", 1)[1].split(r"\botrule", 1)[0]
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        if not line.endswith(r"\\"):
            raise ValueError(f"Unexpected original data row: {line}")
        rows.append([cell.strip() for cell in line[:-2].split("&")])
    return {
        "label": label_match.group(1),
        "caption": braced_argument(block, r"\caption"),
        "footnotetext": braced_argument(block, r"\footnotetext"),
        "rows": rows,
        "original": block,
    }


def wrap(table: dict, alignment: str, header: str, rows: list[str], *, sep=3) -> str:
    body = "\n".join(rows)
    return (
        "\\begin{table}[tbp]\n"
        + table["caption"]
        + "\\label{"
        + table["label"]
        + "}\n"
        + "\\BMCVisualTableStyle\n"
        + f"\\setlength{{\\tabcolsep}}{{{sep}pt}}\n"
        + "\\begin{tabularx}{\\textwidth}{"
        + alignment
        + "}\n\\toprule\n"
        + header
        + "\n\\midrule\n"
        + body
        + "\n\\bottomrule\n\\end{tabularx}\n"
        + "{\\BMCVisualTableNotes\n"
        + table["footnotetext"]
        + "\n}\n\\end{table}"
    )


def table1(table: dict) -> tuple[str, list[dict]]:
    rows, manifest = [], []
    for index, cells in enumerate(table["rows"]):
        assert len(cells) == 6
        if index in (2, 5):
            rows.append(r"\addlinespace[6pt]")
        rows.append(" & ".join(cells) + r"\\")
        manifest.append({"row": index + 1, "labels": [cells[0], cells[1], cells[5]], "values": cells[2:5]})
    alignment = (
        r"@{}>{\raggedright\arraybackslash}X"
        r" >{\raggedright\arraybackslash}X"
        r" S[table-format=5.0] S[table-format=3.0] S[table-format=3.0]"
        r" >{\raggedright\arraybackslash}X@{}"
    )
    header = (
        r"\textbf{Source} & \textbf{Outcome} & {\textbf{Students}} & {\textbf{Classes}} & {\textbf{Schools}} & \textbf{95\% interval method}\\"
    )
    return wrap(table, alignment, header, rows, sep=3), manifest


def domain_estimand(cell: str) -> tuple[str, str]:
    match = re.fullmatch(r"\\shortstack\[l\]\{(.*?)\\\\\s+(.*?)\}", cell)
    if not match:
        raise ValueError(f"Cannot read domain and estimand: {cell}")
    return match.group(1), match.group(2)


def table2(table: dict) -> tuple[str, list[dict]]:
    rows, manifest = [], []
    previous = None
    for index, cells in enumerate(table["rows"]):
        assert len(cells) == 4
        domain, estimand = domain_estimand(cells[0])
        if domain != previous:
            if previous is not None:
                rows.append(r"\addlinespace[7pt]")
            rows.append(r"\multicolumn{4}{@{}l@{}}{\textbf{" + domain + r"}}\\[2pt]")
            previous = domain
        rows.append(r"\hspace{0.65em}" + estimand + " & " + " & ".join(cells[1:]) + r"\\")
        manifest.append({"row": index + 1, "domain_group": domain, "estimand": estimand, "values": cells[1:]})
    alignment = (
        r"@{}>{\raggedright\arraybackslash}X"
        r" S[table-format=-1.3] S[table-format=-1.3] S[table-format=-1.3]@{}"
    )
    header = (
        r"\textbf{Domain and estimand} & {\textbf{Estimate}} & {\textbf{95\% lower}} & {\textbf{95\% upper}}\\"
    )
    return wrap(table, alignment, header, rows, sep=5), manifest


def ci_limits(cell: str) -> tuple[str, str]:
    match = re.fullmatch(r"(-?\d+\.\d{3}) to (-?\d+\.\d{3})", cell)
    if not match:
        raise ValueError(f"Cannot read interval: {cell}")
    return match.group(1), match.group(2)


def table3(table: dict) -> tuple[str, list[dict]]:
    rows, manifest = [], []
    for index, cells in enumerate(table["rows"]):
        assert len(cells) == 5
        if index in (5, 8, 10, 13):
            rows.append(r"\addlinespace[6pt]")
        low, high = ci_limits(cells[4])
        rows.append(" & ".join(cells[:4] + [low, high]) + r"\\")
        manifest.append({"row": index + 1, "specification": cells[0], "values": cells[1:4] + [low, high]})
    alignment = (
        r"@{}>{\raggedright\arraybackslash}X"
        r" S[table-format=5.0] S[table-format=3.0]"
        r" S[table-format=-1.3] S[table-format=-1.3] @{\hspace{0.2em}to\hspace{0.2em}} S[table-format=-1.3]@{}"
    )
    header = (
        r"\textbf{Specification} & {\textbf{Students}} & {\textbf{Classes}} & {\boldmath$\beta_{\mathrm{B}} - \beta_{\mathrm{W}}$} & \multicolumn{2}{c@{}}{\textbf{95\% CI}}\\"
    )
    return wrap(table, alignment, header, rows, sep=3), manifest


def effect_triplet(cell: str) -> tuple[str, str, str]:
    match = re.fullmatch(r"\\shortstack\[l\]\{(-?\d+\.\d{3})\\\\\s+\((-?\d+\.\d{3}) to (-?\d+\.\d{3})\)\}", cell)
    if not match:
        raise ValueError(f"Cannot read effect and interval: {cell}")
    return tuple(match.groups())


def table4(table: dict) -> tuple[str, list[dict]]:
    rows, manifest = [], []
    for index, cells in enumerate(table["rows"]):
        assert len(cells) == 5
        if index in (1, 2):
            rows.append(r"\addlinespace[7pt]")
        elif index > 2:
            rows.append(r"\addlinespace[5pt]")
        triplets = [effect_triplet(cell) for cell in cells[2:]]
        formatted = [r"\BMCVisualEffect{" + "}{".join(triplet) + "}" for triplet in triplets]
        rows.append(" & ".join(cells[:2] + formatted) + r"\\")
        manifest.append({"row": index + 1, "source_and_domain": cells[0], "students": cells[1], "effects_in_original_order": triplets})
    alignment = (
        r"@{}>{\raggedright\arraybackslash}p{26mm} S[table-format=4.0]"
        r" *{3}{>{\centering\arraybackslash}X}@{}"
    )
    header = (
        r"\textbf{Source and domain} & {\textbf{Students}} & \shortstack[c]{\textbf{Within}\\\boldmath$\beta_{\mathrm{W}}$} & \shortstack[c]{\textbf{Between}\\\boldmath$\beta_{\mathrm{B}}$} & \shortstack[c]{\boldmath$\beta_{\mathrm{B}} - \beta_{\mathrm{W}}$}\\"
    )
    return wrap(table, alignment, header, rows, sep=2), manifest


def verify_preservation(original: dict, replacement: str, manifest: list[dict]) -> dict:
    # Exact caption/note equality includes wording, punctuation and TeX formulas.
    assert braced_argument(replacement, r"\caption") == original["caption"]
    assert braced_argument(replacement, r"\footnotetext") == original["footnotetext"]
    assert replacement.count(r"\label{" + original["label"] + "}") == 1
    assert len(manifest) == len(original["rows"])
    assert r"\resizebox" not in replacement and r"\includegraphics" not in replacement
    assert r"\hline" not in replacement and "|" not in replacement

    # Every row's original labels/values is accounted for by a structural parse;
    # aggregate token checks additionally catch accidental omission/duplication.
    source_tokens = []
    rebuilt_tokens = []
    for row, entry in zip(original["rows"], manifest, strict=True):
        label = original["label"]
        if label == "tab1":
            assert entry["labels"] == [row[0], row[1], row[5]]
            assert entry["values"] == row[2:5]
            source_tokens.extend(row[2:5])
            rebuilt_tokens.extend(entry["values"])
        elif label == "tab2":
            domain, estimand = domain_estimand(row[0])
            assert (entry["domain_group"], entry["estimand"]) == (domain, estimand)
            assert entry["values"] == row[1:]
            source_tokens.extend(row[1:])
            rebuilt_tokens.extend(entry["values"])
        elif label == "tab3":
            low, high = ci_limits(row[4])
            assert entry["specification"] == row[0]
            assert entry["values"] == row[1:4] + [low, high]
            source_tokens.extend(row[1:4] + [low, high])
            rebuilt_tokens.extend(entry["values"])
        elif label == "tab4":
            assert entry["source_and_domain"] == row[0]
            assert entry["students"] == row[1]
            triplets = [effect_triplet(cell) for cell in row[2:]]
            assert entry["effects_in_original_order"] == triplets
            source_tokens.append(row[1])
            rebuilt_tokens.append(entry["students"])
            source_tokens.extend(value for triplet in triplets for value in triplet)
            rebuilt_tokens.extend(value for triplet in entry["effects_in_original_order"] for value in triplet)
    assert source_tokens == rebuilt_tokens
    # Ensure each numeric token is emitted exactly as supplied, including signs,
    # three-decimal trailing zeroes, and the original row/column ordering.
    content = replacement.split(r"\midrule", 1)[1].split(r"\bottomrule", 1)[0]
    rendered_numbers = []
    emitted_rows = [line.strip()[:-2] for line in content.splitlines()
                    if line.strip().endswith(r"\\") and " & " in line]
    assert len(emitted_rows) == len(original["rows"])
    for source_row, line in zip(original["rows"], emitted_rows, strict=True):
        cells = [cell.strip() for cell in line.split("&")]
        if original["label"] == "tab1":
            assert cells == source_row
            rendered_numbers.extend(cells[2:5])
        elif original["label"] == "tab2":
            domain, estimand = domain_estimand(source_row[0])
            assert cells[0] == r"\hspace{0.65em}" + estimand
            assert r"\textbf{" + domain + "}" in replacement
            rendered_numbers.extend(cells[1:])
        elif original["label"] == "tab3":
            assert cells[0] == source_row[0]
            rendered_numbers.extend(cells[1:])
        else:
            assert cells[:2] == source_row[:2]
            rendered_numbers.append(cells[1])
            for cell in cells[2:]:
                match = re.fullmatch(r"\\BMCVisualEffect\{(-?\d+\.\d{3})\}\{(-?\d+\.\d{3})\}\{(-?\d+\.\d{3})\}", cell)
                assert match, cell
                rendered_numbers.extend(match.groups())
    assert rendered_numbers == source_tokens, (original["label"], rendered_numbers, source_tokens)
    return {
        "data_rows": len(manifest),
        "numeric_values_exactly_retained": len(source_tokens),
        "caption_exact": True,
        "footnotetext_exact": True,
        "row_labels_and_meanings_retained": True,
        "row_order_retained": True,
        "editable_vector_latex": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    args = parser.parse_args()
    source_bytes = args.source.read_bytes()
    source = source_bytes.decode("utf-8-sig")
    blocks = re.findall(r"\\begin\{table\}(?:\[[^\]]*\])?.*?\\end\{table\}", source, re.DOTALL)
    tables = [parse_table(block) for block in blocks]
    assert [table["label"] for table in tables] == ["tab1", "tab2", "tab3", "tab4"]
    builders = [table1, table2, table3, table4]
    replacements = []
    for table, builder in zip(tables, builders, strict=True):
        replacement, manifest = builder(table)
        audit = verify_preservation(table, replacement, manifest)
        replacements.append({"label": table["label"], "original": table["original"], "original_sha256": sha(table["original"]), "replacement": replacement, "audit": audit, "row_manifest": manifest})
    report = {
        "source": str(args.source),
        "source_file_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "preamble": PREAMBLE,
        "body_font_pt": 8.5,
        "note_font_pt": 7.5,
        "width": r"\textwidth (31pc)",
        "replacements": replacements,
        "validation": "source/row invariants passed; integrated PDF compilation and visual inspection required",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # No source-file mutation, even when the integrating agent reruns the script.
    assert args.source.read_bytes() == source_bytes
    total = sum(item["audit"]["numeric_values_exactly_retained"] for item in replacements)
    lines = [
        "# 2026-10-13 四张正文表格排版审查",
        "",
        f"来源：`{args.source}`。本脚本仅生成替换块，未修改 manuscript.tex、正文、统计结果或结论。",
        "",
        "## 已完成的表格设计",
        "",
        "- 四表保持可编辑 LaTeX，使用 booktabs 三条主线、无竖线、无逐行网格。",
        "- 表内文字和数值为 8.5 pt／11 pt 行距，表注为 7.5 pt／9.5 pt；不缩放整表，不栅格化。",
        "- 所有表使用现有 31pc 的 textwidth；表格样式宏只在各 table 的局部分组中生效，不改变全局正文或 caption 格式。",
        "- 表 1 用调查间留白与可换行文字列组织来源、结局和区间方法，人数列右对齐。",
        "- 表 2 将重复 domain 标签提升为三个组标题，保留三个组内的 Within／Between／Contextual 行及原顺序；三个数值列按小数对齐。",
        "- 表 3 保留所有 specification 原文与顺序，以留白区分既有连续块；区间拆为对齐的下、上界，中间仍显示 to。",
        "- 表 4 保留八个来源原行名与原列顺序；每个估计及区间两行展示，点估计按固定小数位对齐；CI 用紧凑的数学 [下界, 上界]，不为正数补入固定符号占位。调查间及 ICCS 行间留白。",
        "- 浮动位置由原 [h] 放宽为 [tbp]，允许正文顶／底或单独浮动页；不强制改变正文分页。",
        "",
        "## 信息守恒核验",
        "",
        "| 表 | 原数据行数 | 完全保留的数值 | Caption／footnotetext | 行名／行义与原顺序 |",
        "|---|---:|---:|---|---|",
    ]
    for item in replacements:
        audit = item["audit"]
        lines.append(f"| {item['label']} | {audit['data_rows']} | {audit['numeric_values_exactly_retained']} | 逐字一致 | 已通过结构化逐行断言 |")
    lines += [
        "",
        f"合计 {total} 个数据数值逐 token、逐顺序核验，包含正负号和三位小数末尾零。表注中的数字与数学表达由原 footnotetext 完整复制并核验。原表的非数值标签也逐行解析并核验，表 2 的 domain 原文完整保存在对应组标题中。",
        "",
        "## 集成与余下版面 QA",
        "",
        f"读取 `{args.output}`，把 `preamble` 加在 begin document 前；依次以 original 精确定位四表并替换为 replacement。每个 original 必须在当时的 manuscript.tex 中唯一匹配，不能按旧 Word 重建内容。",
        "",
        "依赖 array、tabularx、siunitx 均已用本机 kpsewhich 确认存在。集成后需检查 LaTeX 日志的 table overfull／Float too large 报告，以及 PDF 中四表的列宽、数值对齐、表注归属和分页。该报告只声称源码与信息守恒核验已通过；尚不把未编译的布局说成已经视觉验证。",
        "",
        f"当前来源文件 SHA-256：`{report['source_file_sha256']}`。",
    ]
    args.review.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"tables": len(replacements), "data_values_verified": total, "output": str(args.output), "review": str(args.review), "source_unchanged": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
