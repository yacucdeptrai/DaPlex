#!/usr/bin/env python3
"""
convert.py — Convert a single Markdown thesis file to Typst.

Usage:
    python convert.py --input <path.md> --output <path.typ>

Requires: typst --root bao-cao-do-an/ (absolute paths /figures/... and /typst/template.typ)
"""

import re
import sys
import argparse
from pathlib import Path
import unicodedata


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """'Hình 1.1' → 'hinh-1-1'"""
    nfd = unicodedata.normalize('NFD', text.lower())
    ascii_str = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '-', ascii_str).strip('-')


XREF_RE = re.compile(r'(Hình|Bảng)\s+(\d+)\.(\d+)')

def apply_cross_refs(text: str) -> str:
    """Replace 'Hình 1.1' → '@hinh-1-1', 'Bảng 2.3' → '@bang-2-3'."""
    def _replace(m: re.Match) -> str:
        kind  = m.group(1)
        n1, n2 = m.group(2), m.group(3)
        prefix = 'hinh' if kind == 'Hình' else 'bang'
        return f'@{prefix}-{n1}-{n2}'
    return XREF_RE.sub(_replace, text)


def escape_outside_code(text: str, char: str, replacement: str) -> str:
    """Escape `char` in `text` only outside backtick code spans."""
    parts = re.split(r'(`[^`]*`)', text)
    result = []
    for part in parts:
        if part.startswith('`') and part.endswith('`') and len(part) >= 2:
            result.append(part)  # inside code span — leave unchanged
        else:
            result.append(part.replace(char, replacement))
    return ''.join(result)


def escape_dollar(text: str) -> str:
    """Escape '$' outside code spans (e.g. MongoDB $inc, $set operators)."""
    return escape_outside_code(text, '$', r'\$')


def escape_hash(text: str) -> str:
    """Escape '#' in prose that would start a Typst function call."""
    # Only escape '#' that is NOT at the very start of the string
    # (headings start with '#' but those are handled before this function runs)
    return re.sub(r'(?<!\A)(?<!\n)#', r'\\#', text)


def convert_inline(text: str) -> str:
    """Convert inline Markdown to Typst inline syntax."""
    # Bold **text** / __text__ → #strong[text]  (avoids bare * in Typst output)
    text = re.sub(r'\*\*(.+?)\*\*', r'#strong[\1]', text)
    text = re.sub(r'__(.+?)__',     r'#strong[\1]', text)

    # Links [label](url) — keep label, drop url
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Italic *text* → _text_
    # Exclude: already-converted bold, figure caption markers (*Hình /*Bảng),
    # and list bullet lines (handled separately)
    text = re.sub(
        r'(?<!\*)\*(?!\*|Hình\s+\d|Bảng\s+\d)([^*\n]+?)(?<!\*)\*(?!\*)',
        r'_\1_',
        text,
    )

    # Escape stray * that didn't form a pair (would start unclosed bold in Typst)
    text = escape_outside_code(text, '*', r'\*')
    return text


def heading_line(line: str, shift: int = 1) -> str:
    """'# 1.1 Title' → '== 1.1 Title'  (shift controls how many = to add)"""
    m = re.match(r'^(#{1,6})\s+(.*)', line)
    if not m:
        return line
    level = min(len(m.group(1)) + shift, 6)
    return '=' * level + ' ' + m.group(2).strip()


# ─────────────────────────────────────────────────────────────
# Table parser
# ─────────────────────────────────────────────────────────────

def split_table_cells(row_str: str) -> list[str]:
    """Split a GFM table row on '|', respecting backtick code spans."""
    cells = []
    current = []
    in_code = False
    i = 0
    while i < len(row_str):
        ch = row_str[i]
        if ch == '`':
            in_code = not in_code
            current.append(ch)
        elif ch == '|' and not in_code:
            cells.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)
        i += 1
    last = ''.join(current).strip()
    if last:
        cells.append(last)
    return cells


def pre_escape_cell(text: str) -> str:
    """Escape special Typst chars in raw markdown cell text (before convert_inline)."""
    parts = re.split(r'(`[^`]+`)', text)
    result = []
    for part in parts:
        if part.startswith('`') and part.endswith('`') and len(part) > 2:
            result.append(part)  # keep code spans unchanged; handled later
        else:
            result.append(part.replace('#', r'\#').replace('<', r'\<').replace('$', r'\$'))
    return ''.join(result)


def escape_cell(text: str) -> str:
    """Convert backtick code spans in already-converted cell content."""
    parts = re.split(r'(`[^`]+`)', text)
    result = []
    for part in parts:
        if part.startswith('`') and part.endswith('`') and len(part) > 2:
            inner = part[1:-1].replace('"', r'\"')
            result.append(f'#raw("{inner}")')
        else:
            result.append(part)
    return ''.join(result)


def parse_table(table_lines: list[str]) -> str:
    """Convert GFM pipe table -> Typst #table(...)."""
    rows = []
    for ln in table_lines:
        s = ln.strip()
        if not s:
            continue
        # Skip separator rows (|---|---|)
        if re.match(r'^\|[-| :]+\|$', s):
            continue
        # Strip leading/trailing pipes then split respecting code spans
        if s.startswith('|'):
            s = s[1:]
        if s.endswith('|'):
            s = s[:-1]
        cells = split_table_cells(s)
        rows.append(cells)

    if not rows:
        return ''

    ncols = len(rows[0])
    header = rows[0]
    data   = rows[1:]

    col_spec = ', '.join(['1fr'] * ncols)

    def fmt_cells(row: list[str], bold: bool = False) -> str:
        row = (row + [''] * ncols)[:ncols]
        cells = []
        for c in row:
            # Pre-escape special chars in raw text, then convert inline markdown,
            # then convert remaining code spans to #raw(...)
            content = escape_cell(convert_inline(pre_escape_cell(c)))
            if bold:
                cells.append(f'[#strong[{content}]]')
            else:
                cells.append(f'[{content}]')
        return ', '.join(cells)

    header_str = fmt_cells(header, bold=True)
    data_lines = ',\n    '.join(fmt_cells(r) for r in data)

    return (
        f'table(\n'
        f'  columns: ({col_spec}),\n'
        f'  table.header({header_str}),\n'
        f'  {data_lines},\n'
        f')'
    )


# ─────────────────────────────────────────────────────────────
# FIGURE block extractor
# ─────────────────────────────────────────────────────────────

def extract_figure(comment_text: str) -> dict | None:
    """Parse a <!-- FIGURE ... --> block into a dict."""
    drawio_m = re.search(r'drawio:\s*(figures/[\w\-\.]+\.drawio)', comment_text)
    id_m     = re.search(r'id:\s*(Hình|Bảng)\s+(\d+)\.(\d+)',     comment_text)
    if not drawio_m or not id_m:
        return None
    fig_type = id_m.group(1)
    n1, n2   = id_m.group(2), id_m.group(3)
    prefix   = 'hinh' if fig_type == 'Hình' else 'bang'
    svg_name = Path(drawio_m.group(1)).stem + '.svg'
    return {
        'label':    f'{prefix}-{n1}-{n2}',
        'svg_name': svg_name,
        'kind':     fig_type,
        'n1': n1, 'n2': n2,
    }


# ─────────────────────────────────────────────────────────────
# Main converter
# ─────────────────────────────────────────────────────────────

def convert_file(md_path: Path, level_shift: int = 1) -> str:
    lines  = md_path.read_text(encoding='utf-8').splitlines()
    output: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # ── Skip non-FIGURE HTML comments ────────────────────────────────
        if re.match(r'^\s*<!--(?! FIGURE)', line):
            while i < len(lines) and '-->' not in lines[i]:
                i += 1
            i += 1   # skip closing -->
            continue

        # ── FIGURE comment block ─────────────────────────────────────────
        if re.match(r'^\s*<!-- FIGURE', line):
            comment_parts = []
            while i < len(lines):
                comment_parts.append(lines[i])
                done = '-->' in lines[i]
                i += 1
                if done:
                    break

            fig = extract_figure('\n'.join(comment_parts))
            if not fig:
                continue

            # Skip ![...](pending)
            if i < len(lines) and re.match(r'^!\[', lines[i]):
                i += 1

            # Extract caption from *Hình/Bảng N.M: caption* line
            caption = ''
            if i < len(lines):
                cm = re.match(
                    r'^\*(?:Hình|Bảng)\s+\d+\.\d+:\s*(.+?)\*\s*$',
                    lines[i]
                )
                if cm:
                    caption = cm.group(1).strip()
                    i += 1

            svg_path = f'/figures/{fig["svg_name"]}'
            output.append(
                f'\n#figure(\n'
                f'  safe-image("{svg_path}"),\n'
                f'  caption: [{caption}],\n'
                f') <{fig["label"]}>\n'
            )
            continue

        # ── Fenced code block ─────────────────────────────────────────────
        if re.match(r'^```', line):
            lang = line[3:].strip() or 'text'
            code_lines = []
            i += 1
            while i < len(lines) and not re.match(r'^```\s*$', lines[i]):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            body = '\n'.join(code_lines)
            output.append(f'\n```{lang}\n{body}\n```\n')
            continue

        # ── ATX Heading ───────────────────────────────────────────────────
        if re.match(r'^#{1,6}\s', line):
            m_hdr = re.match(r'^#{1,6}\s+(.*)', line)
            # Skip navigation-only headings (e.g. "## Mục lục")
            if m_hdr and slugify(m_hdr.group(1).strip()) == 'muc-luc':
                i += 1
                continue
            h = heading_line(line, level_shift)
            # Apply inline conversions to heading text (after the = markers)
            eq_m = re.match(r'^(=+\s+)(.*)', h)
            if eq_m:
                htxt = convert_inline(eq_m.group(2))
                htxt = escape_dollar(htxt)
                htxt = re.sub(r'@(?!hinh-\d+-\d+|bang-\d+-\d+)', r'\\@', htxt)
                h = eq_m.group(1) + htxt
            output.append('\n' + h + '\n')
            i += 1
            continue

        # ── Horizontal rule ───────────────────────────────────────────────
        if re.match(r'^(-{3,}|\*{3,}|_{3,})\s*$', line):
            output.append('\n#v(0.5em)\n')
            i += 1
            continue

        # ── Table ─────────────────────────────────────────────────────────
        if re.match(r'^\s*\|', line):
            tbl_lines = []
            while i < len(lines) and re.match(r'^\s*\|', lines[i]):
                tbl_lines.append(lines[i])
                i += 1

            tbl_typst = parse_table(tbl_lines)
            if not tbl_typst:
                continue

            # Look for *Bảng N.M: caption* after the table (skip blank lines)
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                cm = re.match(
                    r'^\*Bảng\s+(\d+)\.(\d+):\s*(.+?)\*\s*$',
                    lines[j]
                )
                if cm:
                    i = j + 1  # advance past blanks and caption line
                    n1, n2, cap = cm.group(1), cm.group(2), cm.group(3)
                    output.append(
                        f'\n#figure(\n'
                        f'  kind: table,\n'
                        f'  caption: [{cap}],\n'
                        f'  {tbl_typst}\n'
                        f') <bang-{n1}-{n2}>\n'
                    )
                    continue

            output.append(f'\n#{tbl_typst}\n')
            continue

        # ── Blockquote → #callout ─────────────────────────────────────────
        if re.match(r'^>\s?', line):
            bq_lines = []
            while i < len(lines) and re.match(r'^>\s?', lines[i]):
                bq_lines.append(re.sub(r'^>\s?', '', lines[i]))
                i += 1
            content = ' '.join(bq_lines).strip()
            content = convert_inline(content)
            output.append(f'\n#callout[{content}]\n')
            continue

        # ── Unordered list item — skip nav links, pass through other bullets ──
        if re.match(r'^\s*-\s+', line):
            rest = re.sub(r'^\s*-\s+', '', line)
            if re.search(r'\[[^\]]+\]\([^\)]+\.md[^\)]*\)', rest):
                i += 1
                continue
            # Regular bullet — fall through to prose (Typst renders `- text` as list)

        # ── Numbered list item (1. 2. 3.) ────────────────────────────────────
        if re.match(r'^\d+\.\s+\S', line):
            rest = re.sub(r'^\d+\.\s+', '', line)
            # Skip navigation-style list items (links to .md files = chapter mini-TOC)
            if re.search(r'\[[^\]]+\]\([^\)]+\.md[^\)]*\)', rest):
                i += 1
                continue
            prose = convert_inline(rest)
            prose = apply_cross_refs(prose)
            prose = escape_dollar(prose)
            prose = re.sub(r'@(?!hinh-\d+-\d+|bang-\d+-\d+)', r'\\@', prose)
            output.append('+ ' + prose + '\n')
            i += 1
            continue

        # ── Standalone caption line *Hình/Bảng N.M: ...* ──────────────────
        # Already consumed after FIGURE block or table; skip any orphan
        if re.match(r'^\*(?:Hình|Bảng)\s+\d+\.\d+:', line):
            i += 1
            continue

        # ── Standalone pending image ![...](pending) ──────────────────────
        if re.match(r'^!\[', line):
            i += 1
            continue

        # ── Blank line ────────────────────────────────────────────────────
        if not line.strip():
            output.append('\n')
            i += 1
            continue

        # ── Normal prose ──────────────────────────────────────────────────
        prose = convert_inline(line)
        prose = apply_cross_refs(prose)
        prose = escape_dollar(prose)
        # Escape @ not part of @hinh-N-M / @bang-N-M cross-references
        prose = re.sub(r'@(?!hinh-\d+-\d+|bang-\d+-\d+)', r'\\@', prose)
        output.append(prose + '\n')
        i += 1

    return ''.join(output)


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────

HEADER = '#import "/typst/template.typ": safe-image, callout\n\n'

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input',       required=True, type=Path)
    ap.add_argument('--output',      required=True, type=Path)
    ap.add_argument('--level-shift', type=int, default=1, dest='level_shift')
    args = ap.parse_args()

    result = HEADER + convert_file(args.input, args.level_shift)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding='utf-8')
    print(f'  OK  {args.input.name}  ->  {args.output}')


if __name__ == '__main__':
    main()
