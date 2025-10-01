# research_agent/citations.py
from datetime import datetime

def format_web_citation(result):
    """Format a web search result into APA style citation."""
    title = result.get("title", "No title")
    url = result.get("link", "")
    year = datetime.now().year
    return f"{title}. ({year}). Retrieved from {url}"

def format_paper_citation(paper):
    """Format an academic paper into APA style citation."""
    authors = ", ".join(paper.get("authors", [])) or "Unknown"
    year = paper.get("year", "n.d.")
    title = paper.get("title", "Untitled")
    url = paper.get("url", "")
    return f"{authors} ({year}). {title}. Available at: {url}"

def build_references(web_results, papers):
    """Builds a full references list from web + academic sources."""
    refs = []
    for w in web_results:
        refs.append(format_web_citation(w))
    for p in papers:
        refs.append(format_paper_citation(p))
    return refs
