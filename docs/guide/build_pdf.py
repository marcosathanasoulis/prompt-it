"""Build the public, selectable-text PDF from guide.md.

Layout notes
- Standard PDF fonts only (Helvetica family), so the build needs no font files.
- Two passes: the first pass records the page each section starts on, the second
  pass prints those numbers in the contents list on the cover.
- Every copyable prompt is one wrapped paragraph inside a shaded card, so it can be
  selected and copied as a whole.
- Diagrams are drawn as vectors so they stay sharp and inside the text frame.
"""
from __future__ import annotations

import io
import math
import re
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    BaseDocTemplate, CondPageBreak, Flowable, Frame, FrameBreak, KeepTogether,
    NextPageTemplate, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.platypus.doctemplate import ActionFlowable

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "guide.md"
OUTPUT = ROOT / "put-ai-to-work.pdf"

PAGE_W, PAGE_H = letter
MARGIN = 58
CONTENT_W = PAGE_W - 2 * MARGIN  # 496pt
FRAME_BOTTOM = 60
FRAME_TOP = 72
BAND_H = 318  # cover band height

NAVY = colors.HexColor("#123047")
TEAL = colors.HexColor("#087E8B")
MINT = colors.HexColor("#E6F4F1")
INK = colors.HexColor("#20313D")
SLATE = colors.HexColor("#5B6B75")
RULE = colors.HexColor("#C8D6DC")
PROMPT_BG = colors.HexColor("#F3F6F8")
ZEBRA = colors.HexColor("#F7FAFB")
SAND = colors.HexColor("#FFF6E5")
SKY = colors.HexColor("#EEF4FF")
LAVENDER = colors.HexColor("#F4ECFA")
PALE_MINT = colors.HexColor("#BFE3DC")


# --------------------------------------------------------------------------- text

def linkify(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" color="#087E8B"><u>\1</u></a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+)`", r"<font color='#123047'>\1</font>", text)
    return text.replace("\n", "<br/>")


def styles():
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=11, leading=15.5, textColor=INK, spaceAfter=7)
    return {
        "body": body,
        "lead": ParagraphStyle("lead", parent=body, fontSize=12, leading=17, spaceAfter=9),
        "bullet": ParagraphStyle("bullet", parent=body, leftIndent=16, bulletIndent=3, bulletFontName="Helvetica-Bold", bulletColor=TEAL, spaceAfter=3),
        "number": ParagraphStyle("number", parent=body, leftIndent=20, bulletIndent=2, bulletFontName="Helvetica-Bold", bulletColor=TEAL, spaceAfter=4),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=21, leading=25, textColor=NAVY),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=NAVY, spaceBefore=10, spaceAfter=5),
        "tag": ParagraphStyle("tag", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=TEAL, spaceBefore=10, spaceAfter=2),
        "prompt_title": ParagraphStyle("prompt_title", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=NAVY, spaceAfter=5),
        "prompt": ParagraphStyle("prompt", fontName="Helvetica", fontSize=10.5, leading=14.5, textColor=INK),
        "table": ParagraphStyle("table", fontName="Helvetica", fontSize=10.5, leading=14, textColor=INK),
        "table_head": ParagraphStyle("table_head", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=colors.white),
        "ref": ParagraphStyle("ref", parent=body, fontSize=10.5, leading=14, leftIndent=12, bulletIndent=0, bulletFontName="Helvetica-Bold", bulletColor=TEAL, spaceAfter=0),
        "note": ParagraphStyle("note", parent=body, fontSize=10.5, leading=14.5, spaceAfter=0),
        "closing": ParagraphStyle("closing", parent=body, fontName="Helvetica-Oblique", fontSize=10.5, leading=14.5, textColor=SLATE, spaceBefore=8),
        # cover
        "eyebrow": ParagraphStyle("eyebrow", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=PALE_MINT, spaceAfter=16),
        "cover_title": ParagraphStyle("cover_title", fontName="Helvetica-Bold", fontSize=44, leading=48, textColor=colors.white, spaceAfter=14),
        "cover_sub": ParagraphStyle("cover_sub", fontName="Helvetica", fontSize=16.5, leading=22, textColor=MINT, spaceAfter=22),
        "cover_author": ParagraphStyle("cover_author", fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=colors.white),
        "toc_label": ParagraphStyle("toc_label", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=TEAL, spaceAfter=10),
        "toc": ParagraphStyle("toc", fontName="Helvetica", fontSize=10.5, leading=13.5, textColor=INK),
        "toc_num": ParagraphStyle("toc_num", fontName="Helvetica-Bold", fontSize=10.5, leading=13.5, textColor=TEAL, alignment=TA_RIGHT),
        "toc_page": ParagraphStyle("toc_page", fontName="Helvetica", fontSize=10.5, leading=13.5, textColor=SLATE, alignment=TA_RIGHT),
        "cover_note": ParagraphStyle("cover_note", fontName="Helvetica", fontSize=10, leading=13.5, textColor=SLATE),
    }


# ----------------------------------------------------------------------- flowables

class SectionBadge(Flowable):
    """Rounded navy square holding a section number."""
    def __init__(self, number: str):
        super().__init__()
        self.number = number
        self.width = 28
        self.height = 28

    def draw(self):
        c = self.canv
        c.setFillColor(TEAL)
        c.setStrokeColor(TEAL)
        c.roundRect(0, 0, 28, 28, 5, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(14, 9, self.number)


def section_heading(title: str, number: str | None, key: str, s) -> Table:
    text = Paragraph(f'<a name="{key}"/>{linkify(title)}', s["h2"])
    if number:
        rows = [[SectionBadge(number), text]]
        widths = [40, CONTENT_W - 40]
    else:
        rows = [[text]]
        widths = [CONTENT_W]
    t = Table(rows, colWidths=widths)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), 0.9, TEAL),
    ]))
    t.toc_key = key
    t.section_title = (f"{number}. " if number else "") + title
    t.spaceAfter = 12
    return t


def boxed(flowable, background, bar, pad=10) -> Table:
    t = Table([[flowable]], colWidths=[CONTENT_W], splitInRow=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), background),
        ("LINEBEFORE", (0, 0), (0, -1), 3, bar),
        ("LEFTPADDING", (0, 0), (-1, -1), pad + 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad),
        ("TOPPADDING", (0, 0), (-1, -1), pad - 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
    ]))
    t.spaceAfter = 10
    return t


class Diagram(Flowable):
    """Vector maps with labeled, directed connections. Coordinates are in points."""
    HEIGHTS = {"loop": 200, "task": 160, "evidence": 160}

    def __init__(self, kind: str):
        super().__init__()
        self.kind = kind
        self.width = CONTENT_W
        self.height = self.HEIGHTS[kind]
        self.spaceBefore = 6
        self.spaceAfter = 12

    def box(self, x, y, w, text, fill=MINT, h=40):
        c = self.canv
        c.setFillColor(fill)
        c.setStrokeColor(TEAL)
        c.setLineWidth(0.9)
        c.roundRect(x, y, w, h, 6, fill=1, stroke=1)
        lines = text.split("\n")
        if len(lines) == 1:
            c.setFillColor(NAVY)
            c.setFont("Helvetica-Bold", 9.5)
            c.drawCentredString(x + w / 2, y + h / 2 - 3.5, lines[0])
            return
        c.setFillColor(NAVY)
        size = 9.5
        while stringWidth(lines[0], "Helvetica-Bold", size) > w - 8 and size > 7.5:
            size -= 0.5
        c.setFont("Helvetica-Bold", size)
        c.drawCentredString(x + w / 2, y + h / 2 + 3, lines[0])
        c.setFillColor(SLATE)
        size = 8.5
        while stringWidth(lines[1], "Helvetica", size) > w - 8 and size > 7:
            size -= 0.5
        c.setFont("Helvetica", size)
        c.drawCentredString(x + w / 2, y + h / 2 - 8.5, lines[1])

    def arrow(self, points):
        c = self.canv
        c.setStrokeColor(TEAL)
        c.setFillColor(TEAL)
        c.setLineWidth(1.2)
        path = c.beginPath()
        path.moveTo(*points[0])
        for point in points[1:]:
            path.lineTo(*point)
        c.drawPath(path, stroke=1, fill=0)
        x, y = points[-1]
        px, py = points[-2]
        a = math.atan2(y - py, x - px)
        head = c.beginPath()
        head.moveTo(x, y)
        head.lineTo(x - 7 * math.cos(a - 0.42), y - 7 * math.sin(a - 0.42))
        head.lineTo(x - 7 * math.cos(a + 0.42), y - 7 * math.sin(a + 0.42))
        head.close()
        c.drawPath(head, stroke=0, fill=1)

    def label(self, x, y, text, align="left"):
        c = self.canv
        c.setFillColor(INK)
        c.setFont("Helvetica-Oblique", 8)
        if align == "right":
            c.drawRightString(x, y, text)
        elif align == "center":
            c.drawCentredString(x, y, text)
        else:
            c.drawString(x, y, text)

    def draw(self):
        c = self.canv
        c.saveState()
        if self.kind == "loop":
            top = 154
            mid = top + 20
            self.box(0, top, 76, "Plan\napproved brief")
            self.box(105, top, 76, "Act\non a copy")
            self.box(210, top, 76, "Test\nobjective checks")
            self.box(315, top, 76, "Inspect\nevidence, quality")
            self.box(420, top, 76, "Done", fill=colors.HexColor("#D5EDE7"))
            self.arrow([(76, mid), (105, mid)])
            self.arrow([(181, mid), (210, mid)])
            self.arrow([(286, mid), (315, mid)])
            self.label(300, mid + 5, "pass", "center")
            self.arrow([(391, mid), (420, mid)])
            self.label(405, mid + 5, "accept", "center")
            self.box(200, 78, 160, "Diagnose and revise\nwith a changed hypothesis")
            self.arrow([(247, top), (247, 118)])
            self.label(252, 133, "fail")
            self.arrow([(351, top), (351, 118)])
            self.label(356, 133, "needs revision")
            self.arrow([(200, 98), (143, 98), (143, top)])
            self.label(171, 103, "retry", "center")
            self.box(356, 0, 140, "Ask a human", fill=SAND)
            self.arrow([(360, 98), (426, 98), (426, 40)])
            self.label(420, 69, "retry limit reached,", "right")
            self.label(420, 58, "access missing,", "right")
            self.label(420, 47, "or progress stalled", "right")
        elif self.kind == "task":
            mid = 62
            self.box(0, mid, 80, "Approved brief\nowner: human")
            self.box(98, 105, 100, "Research\nevidence: sources")
            self.box(98, 18, 100, "Data check\nevidence: counts")
            self.box(216, mid, 76, "Draft\nowner: maker")
            self.box(310, mid, 96, "Independent review\nevidence: findings")
            self.box(424, mid, 72, "Acceptance\nowner: human", fill=SAND)
            self.arrow([(80, 82), (89, 82), (89, 125), (98, 125)])
            self.arrow([(89, 82), (89, 38), (98, 38)])
            self.arrow([(198, 125), (207, 125), (207, 82), (216, 82)])
            self.arrow([(198, 38), (207, 38), (207, 82)])
            self.arrow([(292, 82), (310, 82)])
            self.arrow([(406, 82), (424, 82)])
        else:
            mid = 62
            self.box(0, mid, 84, "Claim")
            self.box(140, 105, 120, "Source + date", fill=SKY)
            self.box(140, 18, 120, "Owner / decision", fill=SAND)
            self.box(340, mid, 156, "Affected output", fill=LAVENDER)
            self.arrow([(84, 82), (112, 82), (112, 125), (140, 125)])
            self.arrow([(112, 82), (112, 38), (140, 38)])
            self.arrow([(260, 125), (300, 125), (300, 82), (340, 82)])
            self.arrow([(260, 38), (300, 38), (300, 82)])
        c.restoreState()


# ------------------------------------------------------------------------ document

class GuideDoc(BaseDocTemplate):
    def __init__(self, target, page_map: dict, **kw):
        super().__init__(target, **kw)
        self.page_map = page_map
        self.current_section = ""  # section in force at the top of the current page
        self._next_section = ""
        self._content_seen = False
        self._outline_started = False

    def handle_pageBegin(self):
        super().handle_pageBegin()
        self._content_seen = False

    def afterFlowable(self, flowable):
        key = getattr(flowable, "toc_key", None)
        if key:
            # A heading that opens a page names that page; otherwise the page keeps
            # the section it started in.
            if not self._content_seen:
                self.current_section = flowable.section_title
            self._next_section = flowable.section_title
            self.page_map[key] = self.page
            top = min(PAGE_H, self.frame._y + getattr(flowable, "_height", 0) + 24)
            self.canv.bookmarkPage(key, fit="XYZ", left=0, top=top, zoom=0)
            self.canv.addOutlineEntry(flowable.section_title, key, level=0, closed=False)
            if not self._outline_started:
                self.canv.showOutline()
                self._outline_started = True
        if not isinstance(flowable, (CondPageBreak, Spacer, ActionFlowable)):
            self._content_seen = True

    def handle_pageEnd(self):
        super().handle_pageEnd()
        self.current_section = getattr(self, "_next_section", self.current_section)


def draw_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - BAND_H, PAGE_W, BAND_H, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, PAGE_H - BAND_H - 5, PAGE_W, 5, fill=1, stroke=0)
    canvas.restoreState()


def draw_page(canvas, doc):
    canvas.saveState()
    y_rule = PAGE_H - 50
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.6)
    canvas.line(MARGIN, y_rule, PAGE_W - MARGIN, y_rule)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SLATE)
    canvas.drawString(MARGIN, y_rule + 6, doc.current_section.upper())
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawRightString(PAGE_W - MARGIN, y_rule + 6, "PUT AI TO WORK")
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(SLATE)
    canvas.drawCentredString(PAGE_W / 2, 34, str(doc.page))
    canvas.restoreState()


# --------------------------------------------------------------------------- parse

def split_prompt_heading(title: str):
    m = re.match(r"Copyable prompt (\d+)\s*-\s*(.+)", title)
    if not m:
        return None, title
    label = m.group(2).strip()
    return m.group(1), label[:1].upper() + label[1:]


def table_widths(ncols: int):
    if ncols == 3:
        return [CONTENT_W * r for r in (0.37, 0.30, 0.33)]
    if ncols == 2:
        return [CONTENT_W * r for r in (0.40, 0.60)]
    return [CONTENT_W / ncols] * ncols


def build_story(source: str, s, page_map: dict):
    lines = source.splitlines()
    cover = {"title": "", "subtitle": "", "author": "", "note": ""}
    sections = []  # (key, number, title)
    body = []
    pending = []  # heading flowables to bond with the next flowable
    whole: list | None = None  # collects a short section that must stay on one page

    def add(flowable):
        nonlocal pending
        if whole is not None:  # the whole block is kept together later; no nesting
            whole.extend(pending + [flowable])
            pending = []
        elif pending:
            body.append(KeepTogether(pending + [flowable]))
            pending = []
        else:
            body.append(flowable)

    def close_whole():
        nonlocal whole
        if whole:
            body.append(KeepTogether(whole))
        whole = None

    i = 0
    diagram_kinds = ["loop", "task", "evidence"]
    diagram_count = 0
    in_code = False
    code_kind = "text"
    code: list[str] = []
    in_references = False
    reference_items: list[str] = []
    section_count = 0

    def flush_references():
        if not reference_items:
            return
        half = (len(reference_items) + 1) // 2
        cols = [reference_items[:half], reference_items[half:]]
        rows = []
        for r in range(half):
            row = []
            for col in cols:
                row.append(Paragraph(linkify(col[r]), s["ref"], bulletText="•") if r < len(col) else "")
            rows.append(row)
        t = Table(rows, colWidths=[CONTENT_W / 2] * 2)
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        add(t)
        reference_items.clear()

    while i < len(lines):
        line = lines[i]
        if line.startswith("```mermaid"):
            while i < len(lines) and lines[i] != "```":
                i += 1
            add(Diagram(diagram_kinds[diagram_count]))
            diagram_count += 1
            i += 1
            continue
        if line.startswith("```"):
            if in_code:
                formatted = "<br/>".join(escape(x) for x in code) if code_kind == "bash" or (code and code[0].startswith("/plugin ")) else "<br/><br/>".join(escape(" ".join(part.split())) for part in "\n".join(code).split("\n\n"))
                prompt = Paragraph(formatted, s["prompt"])
                add(boxed(prompt, PROMPT_BG, TEAL))
                code = []
                in_code = False
            else:
                in_code = True
                code_kind = line[3:].strip()
            i += 1
            continue
        if in_code:
            code.append(line)
            i += 1
            continue
        if not line.strip():
            i += 1
            continue
        if line.startswith("# "):
            cover["title"] = line[2:].strip()
        elif line.startswith("## "):
            title = line[3:].strip()
            if not cover["subtitle"] and not sections:
                cover["subtitle"] = title
            else:
                if in_references:
                    flush_references()
                close_whole()
                m = re.match(r"(\d+)\.\s+(.+)", title)
                number, clean = (m.group(1), m.group(2)) if m else (None, title)
                section_count += 1
                key = f"section-{section_count}"
                sections.append((key, number, clean))
                in_references = clean.lower().startswith("references")
                if len(sections) > 1:
                    body.append(CondPageBreak(2.0 * inch))
                if clean.startswith("Before you press"):
                    whole = []  # short checklist: heading, intro, table and note stay together
                pending.append(section_heading(clean, number, key, s))
        elif line.startswith("### "):
            title = line[4:].strip()
            num, label = split_prompt_heading(title)
            if num:
                pending.append(Paragraph(f"COPYABLE PROMPT {num}", s["tag"]))
                pending.append(Paragraph(linkify(label), s["prompt_title"]))
            else:
                pending.append(Paragraph(linkify(title), s["h3"]))
        elif line.startswith("> "):
            add(boxed(Paragraph(linkify(line[2:]), s["body"]), MINT, NAVY))
        elif re.match(r"[-*] ", line):
            if in_references:
                reference_items.append(line[2:])
            else:
                add(Paragraph(linkify(line[2:]), s["bullet"], bulletText="•"))
        elif re.match(r"\d+\. ", line):
            num, rest = line.split(". ", 1)
            add(Paragraph(linkify(rest), s["number"], bulletText=f"{num}."))
        elif line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[-| ]+\|$", lines[i]):
                    table_lines.append([x.strip() for x in lines[i].strip("|").split("|")])
                i += 1
            cells = [[Paragraph(linkify(x), s["table_head"] if ri == 0 else s["table"]) for x in row] for ri, row in enumerate(table_lines)]
            if cells:
                t = Table(cells, colWidths=table_widths(len(cells[0])), repeatRows=1)
                style = [
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
                for r in range(2, len(cells), 2):
                    style.append(("BACKGROUND", (0, r), (-1, r), ZEBRA))
                t.setStyle(TableStyle(style))
                t.spaceBefore = 4
                t.spaceAfter = 12
                add(t)
            continue
        else:
            para = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#|>|\* |[-*] |\d+\. |\||```)", lines[i]):
                para.append(lines[i])
                i += 1
            text = " ".join(para)
            if not sections:
                if text.startswith("**By "):
                    cover["author"] = text.strip("*").strip()
                elif text.startswith("**Setup reference checked"):
                    cover["note"] = text
                else:
                    add(Paragraph(linkify(text), s["body"]))
            elif in_references and text.startswith("*") and text.endswith("*"):
                flush_references()
                add(Paragraph(linkify(text), s["closing"]))
            else:
                add(Paragraph(linkify(text), s["body"]))
            continue
        i += 1
    flush_references()
    close_whole()
    return cover, sections, body


def cover_story(cover, sections, page_map, s):
    story = [
        Spacer(1, 58),
        Paragraph("A PRACTICAL GUIDE FOR PEOPLE WHO DON'T CODE", s["eyebrow"]),
        Paragraph(escape(cover["title"]), s["cover_title"]),
        Paragraph(escape(cover["subtitle"]), s["cover_sub"]),
        Paragraph(escape(cover["author"]), s["cover_author"]),
        FrameBreak(),
        Paragraph("IN THIS GUIDE", s["toc_label"]),
    ]
    half = (len(sections) + 1) // 2
    columns = [sections[:half], sections[half:]]
    rows = []
    for r in range(half):
        row = []
        for col in columns:
            if r < len(col):
                key, number, title = col[r]
                page = page_map.get(key, "")
                row += [
                    Paragraph(number or "", s["toc_num"]),
                    Paragraph(f'<a href="#{key}">{escape(title)}</a>', s["toc"]),
                    Paragraph(str(page), s["toc_page"]),
                ]
            else:
                row += ["", "", ""]
        rows.append(row)
    col_w = CONTENT_W / 2
    num_w, page_w, gap = 26, 28, 18
    text_w = col_w - num_w - page_w - gap / 2
    widths = [num_w, text_w, page_w, num_w + gap, text_w, page_w]
    t = Table(rows, colWidths=widths)
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (2, -1), 0.4, RULE),
        ("LINEBELOW", (3, 0), (-1, -1), 0.4, RULE),
        ("LEFTPADDING", (3, 0), (3, -1), gap),
    ]
    t.setStyle(TableStyle(style))
    story.append(t)
    story.append(Spacer(1, 26))
    story.append(boxed(Paragraph(linkify(cover["note"]), s["note"]), MINT, NAVY, pad=9))
    return story


def build(target, page_map: dict):
    s = styles()
    cover, sections, body = build_story(SOURCE.read_text(encoding="utf-8"), s, page_map)
    band_frame = Frame(MARGIN, PAGE_H - BAND_H, CONTENT_W, BAND_H, id="band",
                       leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    lower_frame = Frame(MARGIN, 48, CONTENT_W, PAGE_H - BAND_H - 48 - 40, id="lower",
                        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    body_frame = Frame(MARGIN, FRAME_BOTTOM, CONTENT_W, PAGE_H - FRAME_BOTTOM - FRAME_TOP, id="body",
                       leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc = GuideDoc(target, page_map, pagesize=letter, title=cover["title"], author=cover["author"].replace("By ", "", 1),
                   subject=cover["subtitle"], creator="build_pdf.py (ReportLab)")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[band_frame, lower_frame], onPage=draw_cover),
        PageTemplate(id="body", frames=[body_frame], onPageEnd=draw_page),
    ])
    story = cover_story(cover, sections, page_map, s)
    story += [NextPageTemplate("body"), PageBreak()]
    story += body
    doc.build(story)


def main():
    page_map: dict = {}
    build(io.BytesIO(), page_map)  # first pass: learn section page numbers
    build(str(OUTPUT), dict(page_map))  # second pass: print them on the cover
    print(f"wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
