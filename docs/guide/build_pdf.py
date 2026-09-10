"""Build the public, selectable-text PDF from guide.md."""
from __future__ import annotations

import re
from html import escape
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
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+)`", r"<font name=Helvetica>\1</font>", text)
    return text.replace("\n", "<br/>")


class Diagram(Flowable):
    """Vector maps with labeled, directed connections."""
    def __init__(self, kind: str):
        super().__init__()
        self.kind = kind
        self.width = 492
        self.height = 178 if kind == "loop" else 156

    def box(self, x, y, w, text, fill=MINT):
        c = self.canv
        c.setFillColor(fill); c.setStrokeColor(TEAL)
        c.roundRect(x, y, w, 38, 6, fill=1, stroke=1)
        lines = text.split("\n")
        c.setFillColor(INK); c.setFont("Helvetica-Bold", 9)
        for i, line in enumerate(lines):
            c.drawCentredString(x+w/2, y+23-(i*11 if len(lines)>1 else 5), line)

    def arrow(self, points, label=None, label_pos=None):
        import math
        c=self.canv; c.setStrokeColor(TEAL); c.setFillColor(TEAL); c.setLineWidth(1.1)
        path=c.beginPath(); path.moveTo(*points[0])
        for point in points[1:]: path.lineTo(*point)
        c.drawPath(path)
        x,y=points[-1]; px,py=points[-2]; a=math.atan2(y-py,x-px)
        for d in (-.48,.48): c.line(x,y,x-6*math.cos(a+d),y-6*math.sin(a+d))
        if label:
            c.setFillColor(INK); c.setFont("Helvetica",8.5); c.drawString(*label_pos,label)

    def draw(self):
        c=self.canv; c.saveState()
        if self.kind == "loop":
            self.box(0,120, 70,"Plan")
            self.box(104,120,70,"Act")
            self.box(208,120,70,"Test")
            self.box(316,120,80,"Inspect")
            self.box(426,120,66,"Done")
            for start,end in [(70,104),(174,208)]: self.arrow([(start,139),(end,139)])
            self.arrow([(278,139),(316,139)],"pass",(281,149))
            self.arrow([(396,139),(426,139)],"accept",(394,162))
            self.box(190,47,112,"Diagnose / revise")
            self.arrow([(243,120),(243,85)],"fail",(248,99))
            self.arrow([(356,120),(356,66),(302,66)],"revise",(361,92))
            self.arrow([(190,66),(139,66),(139,120)])
            self.box(369,6,123,"Human decision",colors.HexColor("#FFF6E5"))
            self.arrow([(302,56),(340,56),(340,25),(369,25)],"limit / access / stalled",(243,10))
        elif self.kind == "task":
            self.box(0,60,75,"Brief\nHuman")
            self.box(102,100,94,"Research\nSources")
            self.box(102,18,94,"Data check\nCounts")
            self.box(228,60,75,"Draft\nMaker")
            self.box(332,60,75,"Review\nFindings")
            self.box(437,60,55,"Accept\nHuman")
            self.arrow([(75,79),(87,79),(87,119),(102,119)])
            self.arrow([(75,79),(87,79),(87,37),(102,37)])
            self.arrow([(196,119),(213,119),(213,79),(228,79)])
            self.arrow([(196,37),(213,37),(213,79),(228,79)])
            self.arrow([(303,79),(332,79)])
            self.arrow([(407,79),(437,79)])
        else:
            self.box(0,60, 80,"Claim")
            self.box(135,100,112,"Source + date",colors.HexColor("#EEF4FF"))
            self.box(135,18,112,"Owner / decision",colors.HexColor("#FFF6E5"))
            self.box(343,60,139,"Affected output",colors.HexColor("#F4ECFA"))
            self.arrow([(80,79),(107,79),(107,119),(135,119)])
            self.arrow([(80,79),(107,79),(107,37),(135,37)])
            self.arrow([(247,119),(300,119),(300,79),(343,79)])
            self.arrow([(247,37),(300,37),(300,79),(343,79)])
        c.restoreState()


def styles():
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle("cover", parent=base["Title"], fontName="Helvetica-Bold", fontSize=30, leading=34, textColor=NAVY, alignment=TA_CENTER, spaceAfter=16),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontSize=15, leading=20, textColor=TEAL, alignment=TA_CENTER),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=20, leading=25, keepWithNext=True, textColor=NAVY, spaceBefore=3, spaceAfter=10),
        "h3": ParagraphStyle("h3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=12, leading=16, keepWithNext=True, textColor=TEAL, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="Helvetica", fontSize=11, leading=15, textColor=INK, spaceAfter=6),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontName="Helvetica", fontSize=11, leading=15, leftIndent=10, firstLineIndent=-7, textColor=INK, spaceAfter=2),
        "prompt": ParagraphStyle("prompt", parent=base["Code"], fontName="Helvetica", fontSize=10.5, leading=14, textColor=INK, leftIndent=7, rightIndent=7, spaceBefore=4, spaceAfter=8),
        "small": ParagraphStyle("small", parent=base["BodyText"], fontName="Helvetica", fontSize=10.5, leading=14, textColor=INK, spaceAfter=3),
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
            story.append(Diagram(["loop", "task", "evidence"][diagram_count])); diagram_count += 1; i += 1; continue
        if line.startswith("```"):
            if in_code:
                prompt = Paragraph(escape(" ".join(x.strip() for x in code)), s["prompt"])
                story.append(Table([[prompt]], colWidths=[492], style=[("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#F4F7F8")),("LINEBEFORE",(0,0),(0,-1),2,TEAL),("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
                code=[]; in_code=False
            else: in_code=True
            i += 1; continue
        if in_code: code.append(line); i += 1; continue
        if not line.strip(): i += 1; continue
        if line.startswith("# "):
            story.extend([Spacer(1, .35*inch), Paragraph(linkify(line[2:]), s["cover"])])
        elif line.startswith("## "):
            title=line[3:]
            if title == "A practical guide to getting things done, even if you don't code": story.append(Paragraph(linkify(title), s["subtitle"])); story.append(Spacer(1, .35*inch))
            else:
                if title.startswith("1. "):
                    story.append(NextPageTemplate("two")); story.append(PageBreak())
                else:
                    story.append(Spacer(1, 14))
                story.append(Paragraph(linkify(title), s["h2"]))

        elif line.startswith("### "):
            story.append(Paragraph(linkify(line[4:]), s["h3"]))
        elif line.startswith("> "):
            story.append(Table([[Paragraph(linkify(line[2:]), s["body"])]], colWidths=[492], style=[("BACKGROUND",(0,0),(-1,-1),MINT),("BOX",(0,0),(-1,-1),.6,TEAL),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        elif re.match(r"[-*] ", line): story.append(Paragraph("• " + linkify(line[2:]), s["bullet"]))
        elif re.match(r"\d+\. ", line): story.append(Paragraph(linkify(line), s["bullet"]))
        elif line.startswith("|"):
            table_lines=[]
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[-| ]+\|$", lines[i]): table_lines.append([x.strip() for x in lines[i].strip("|").split("|")])
                i += 1
            cells=[[Paragraph(("<font color=white><b>" + linkify(x) + "</b></font>") if ri == 0 else linkify(x), s["small"]) for x in row] for ri,row in enumerate(table_lines)]
            if cells:
                t=Table(cells, colWidths=[492/len(cells[0])]*len(cells[0]), repeatRows=1)
                t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.25,colors.HexColor("#C8D6DC")),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),3)])); story.append(t)
            continue
        else:
            para=[line]; i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#|>|\* |[-*] |\d+\. |\||```)", lines[i]): para.append(lines[i]); i += 1
            story.append(Paragraph(linkify(" ".join(para)), s["body"])); continue
        i += 1
    return story


def main():
    s=styles(); page_w,page_h=letter; margin=54
    frame=Frame(margin, 49, page_w-2*margin, page_h-94, id="body")
    doc=BaseDocTemplate(str(OUTPUT), pagesize=letter, title="Put AI to Work", author="Marcos Athanasoulis", subject="A practical guide to getting things done with AI agents")
    doc.addPageTemplates([PageTemplate(id="cover", frames=[frame], onPage=footer), PageTemplate(id="two", frames=[frame], onPage=footer)])
    doc.build(parse(SOURCE.read_text(encoding="utf-8"), s))


if __name__ == "__main__": main()
