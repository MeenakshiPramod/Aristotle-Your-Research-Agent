# research_agent/reporter.py
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def build_markdown_report(topic, questions, web_results, papers, wiki_summary, summaries, gaps):
    md = []
    md.append(f"# Research Report — {topic}\n")
    md.append("## Research Questions\n")
    md.append(questions + "\n")
    md.append("## Web Results\n")
    for r in web_results:
        md.append(f"- [{r['title']}]({r['link']})\n  - {r['snippet']}\n")
    md.append("## Academic Papers (arXiv)\n")
    for p in papers:
        md.append(f"### {p['title']}\n")
        md.append(f"- Authors: {', '.join(p['authors'])}\n")
        md.append(f"- Link: {p['url']}\n")
        md.append(f"- Abstract: {p['abstract']}\n")
    md.append("## Wikipedia Summary\n")
    md.append(wiki_summary + "\n")
    md.append("## Summaries (Web Results)\n")
    for title, s in summaries:
        md.append(f"### {title}\n{s}\n")
    md.append("## Gap Analysis\n")
    for g in gaps:
        md.append(f"- {g}\n")
    return "\n".join(md)

def build_pdf_report_bytes(topic, questions, web_results, papers, wiki_summary, summaries, gaps):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
    styles = getSampleStyleSheet()
    body_style = styles["BodyText"]
    heading = ParagraphStyle(name="Heading", parent=styles["Heading1"], fontSize=16, spaceAfter=12)
    subheading = ParagraphStyle(name="SubHeading", parent=styles["Heading2"], fontSize=12, spaceAfter=8)
    normal = ParagraphStyle(name="Normal", parent=body_style, fontSize=10, leading=12)

    elems = []
    elems.append(Paragraph(f"Research Report — {topic}", heading))
    elems.append(Spacer(1, 8))

    elems.append(Paragraph("Research Questions", subheading))
    elems.append(Paragraph(questions.replace("\n", "<br/>"), normal))
    elems.append(Spacer(1, 8))

    elems.append(Paragraph("Web Results", subheading))
    for r in web_results:
        elems.append(Paragraph(f"<b>{r['title']}</b>", normal))
        elems.append(Paragraph(f"{r['link']}", normal))
        elems.append(Paragraph(r['snippet'], normal))
        elems.append(Spacer(1, 6))

    elems.append(Paragraph("Academic Papers (arXiv)", subheading))
    for p in papers:
        elems.append(Paragraph(f"<b>{p['title']}</b>", normal))
        elems.append(Paragraph("Authors: " + ", ".join(p['authors']), normal))
        elems.append(Paragraph("Link: " + p['url'], normal))
        elems.append(Paragraph(p['abstract'], normal))
        elems.append(Spacer(1, 6))

    elems.append(Paragraph("Wikipedia Summary", subheading))
    elems.append(Paragraph(wiki_summary, normal))
    elems.append(Spacer(1, 8))

    elems.append(Paragraph("Summaries (Web Results)", subheading))
    for title, s in summaries:
        elems.append(Paragraph(f"<b>{title}</b>", normal))
        elems.append(Paragraph(s, normal))
        elems.append(Spacer(1, 6))

    elems.append(Paragraph("Gap Analysis", subheading))
    for g in gaps:
        elems.append(Paragraph("- " + g, normal))

    doc.build(elems)
    buffer.seek(0)
    return buffer.read()

