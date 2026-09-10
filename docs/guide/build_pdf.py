"""Build the public, selectable-text PDF from guide.md."""
from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, KeepTogether, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Preformatted, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "guide.md"
OUTPUT = ROOT / "put-ai-to-work.pdf"
NAVY = colors.HexColor("#123047")
TEAL = colors.HexColor("#087E8B")
MINT = colors.HexColor("#E6F4F1")
INK = colors.HexColor("#20313D")
GOLD = colors.HexColor("#E9B44C")


def linkify(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" color="#087E8B">\1</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return text.replace("\n", "<br/>")


class Diagram(Flowable):
    """Small, explanatory vector diagrams replacing Markdown Mermaid source."""

    def __init__(self, kind: str):
        super().__init__()
        self.kind = kind
        self.width = 7.0 * inch
        self.height = 1.55 * inch

    def _box(self, c, x, y, w, label, fill=MINT):
        c.setFillColor(fill); c.setStrokeColor(TEAL); c.roundRect(x, y, w, 26, 5, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont("Helvetica-Bold", 7.5)
        for i, line in enumerate(label.split("\n")):
            c.drawCentredString(x + w / 2, y + 10 - i * 8, line)

    def draw(self):
        c = self.canv; c.saveState(); c.setStrokeColor(TEAL); c.setFillColor(TEAL)
        if self.kind == "loop":
            labels = ["Plan", "Act", "Test", "Inspect", "Revise"]
            for i, label in enumerate(labels):
                x = 4 + i * 96; self._box(c, x, 54, 65, label)
                if i < 4:
                    c.line(x + 66, 67, x + 92, 67); c.line(x + 88, 71, x + 92, 67); c.line(x + 88, 63, x + 92, 67)
            c.setFont("Helvetica", 7); c.setFillColor(INK)
            c.drawString(10, 27, "Pass -> accept. Fail -> diagnose a changed hypothesis. Missing access or stalled work -> ask a human.")
        elif self.kind == "task":
            labels = [(5, "Approved brief\nHuman"), (126, "Research\nSources"), (126, "Data check\nCounts"), (270, "Draft\nMaker"), (405, "Review\nFindings"), (522, "Accept\nHuman")]
            ys = [68, 98, 35, 68, 68, 68]
            for (x, label), y in zip(labels, ys): self._box(c, x, y, 84, label)
            for a, b in [(89,126),(210,270),(210,270),(354,405),(489,522)]: c.line(a, 81, b, 81)
            c.setFont("Helvetica", 7); c.setFillColor(INK); c.drawString(7, 15, "Handoff evidence travels with each arrow; parallel work joins only after both checks are complete.")
        else:
            self._box(c, 12, 63, 92, "Claim")
            self._box(c, 151, 93, 96, "Source\n+ date", colors.HexColor("#EEF4FF"))
            self._box(c, 151, 28, 96, "Owner\n+ decision", colors.HexColor("#FFF6E5"))
            self._box(c, 304, 63, 110, "Affected\noutput", colors.HexColor("#F4ECFA"))
            for x1,y1,x2,y2 in [(104,76,151,106),(104,76,151,41),(247,106,304,76),(247,41,304,76)]: c.line(x1,y1,x2,y2)
            c.setFont("Helvetica", 7); c.setFillColor(INK); c.drawString(12, 15, "Connections make evidence easier to inspect. They do not prove a claim is true or current.")
        c.restoreState()


def styles():
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle("cover", parent=base["Title"], fontName="Helvetica-Bold", fontSize=30, leading=34, textColor=NAVY, alignment=TA_CENTER, spaceAfter=16),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontSize=15, leading=20, textColor=TEAL, alignment=TA_CENTER),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY, spaceBefore=3, spaceAfter=10),
        "h3": ParagraphStyle("h3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=TEAL, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="Helvetica", fontSize=9.3, leading=12.2, textColor=INK, spaceAfter=6),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontName="Helvetica", fontSize=9.1, leading=11.7, leftIndent=10, firstLineIndent=-7, textColor=INK, spaceAfter=2),
        "prompt": ParagraphStyle("prompt", parent=base["Code"], fontName="Courier", fontSize=7.4, leading=9.5, textColor=INK, leftIndent=7, rightIndent=7, spaceBefore=4, spaceAfter=8),
        "small": ParagraphStyle("small", parent=base["BodyText"], fontName="Helvetica", fontSize=7.2, leading=9, textColor=INK, spaceAfter=3),
    }


def footer(canvas, doc):
    if doc.page == 1: return
    canvas.saveState(); canvas.setStrokeColor(colors.HexColor("#C8D6DC")); canvas.line(0.62*inch, 0.48*inch, 7.88*inch, 0.48*inch)
    canvas.setFont("Helvetica", 7.5); canvas.setFillColor(NAVY)
    canvas.drawString(0.62*inch, 0.31*inch, "PUT AI TO WORK")
    canvas.drawRightString(7.88*inch, 0.31*inch, f"{doc.page}")
    canvas.restoreState()


def parse(source: str, s):
    story = []
    lines = source.splitlines(); i = 0; first_section = True; in_code = False; code = []; diagram_count = 0
    no_break = {"A one-page routine", "Before you press “go”"}
    while i < len(lines):
        line = lines[i]
        if line.startswith("```mermaid"):
            while i < len(lines) and not (i > 0 and lines[i] == "```"): i += 1
            story.append(Diagram("loop" if diagram_count == 0 else "task")); diagram_count += 1; i += 1; continue
        if line.startswith("```"):
            if in_code:
                story.append(Preformatted("\n".join(code), s["prompt"], maxLineLength=76))
                code=[]; in_code=False
            else: in_code=True
            i += 1; continue
        if in_code: code.append(line); i += 1; continue
        if not line.strip(): i += 1; continue
        if line.startswith("# "):
            story.extend([Spacer(1, 1.45*inch), Paragraph(linkify(line[2:]), s["cover"])])
        elif line.startswith("## "):
            title=line[3:]
            if title == "A practical guide to getting things done, even if you don't code": story.append(Paragraph(linkify(title), s["subtitle"])); story.append(Spacer(1, .35*inch))
            else:
                if title not in no_break:
                    story.append(NextPageTemplate("two")); story.append(PageBreak())
                story.append(Paragraph(linkify(title), s["h2"]))
                if title == "11. Think in graphs: draw relationships before they surprise you": story.append(Diagram("evidence"))
        elif line.startswith("### "):
            story.append(Paragraph(linkify(line[4:]), s["h3"]))
        elif line.startswith("> "):
            story.append(Table([[Paragraph(linkify(line[2:]), s["body"])]], colWidths=[3.37*inch], style=[("BACKGROUND",(0,0),(-1,-1),MINT),("BOX",(0,0),(-1,-1),.6,TEAL),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        elif re.match(r"[-*] ", line): story.append(Paragraph("• " + linkify(line[2:]), s["bullet"]))
        elif re.match(r"\d+\. ", line): story.append(Paragraph(linkify(line), s["bullet"]))
        elif line.startswith("|"):
            table_lines=[]
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[-| ]+\|$", lines[i]): table_lines.append([x.strip() for x in lines[i].strip("|").split("|")])
                i += 1
            cells=[[Paragraph(linkify(x), s["small"]) for x in row] for row in table_lines]
            if cells:
                t=Table(cells, colWidths=[3.37*inch/len(cells[0])]*len(cells[0]), repeatRows=1)
                t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.25,colors.HexColor("#C8D6DC")),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),3)])); story.append(t)
            continue
        else:
            para=[line]; i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#|>|\* |[-*] |\d+\. |\||```)", lines[i]): para.append(lines[i]); i += 1
            story.append(Paragraph(linkify(" ".join(para)), s["body"])); continue
        i += 1
    return story


def main():
    s=styles(); page_w,page_h=letter; margin=.62*inch; gap=.23*inch; col=(page_w-2*margin-gap)/2
    cover=Frame(margin, .65*inch, page_w-2*margin, page_h-1.3*inch, id="cover")
    left=Frame(margin, .65*inch, col, page_h-1.3*inch, id="left")
    right=Frame(margin+col+gap, .65*inch, col, page_h-1.3*inch, id="right")
    doc=BaseDocTemplate(str(OUTPUT), pagesize=letter, title="Put AI to Work", author="", subject="A practical guide to getting things done with AI agents")
    doc.addPageTemplates([PageTemplate(id="cover", frames=[cover], onPage=footer), PageTemplate(id="two", frames=[left,right], onPage=footer)])
    doc.build(parse(SOURCE.read_text(encoding="utf-8"), s))


if __name__ == "__main__": main()
