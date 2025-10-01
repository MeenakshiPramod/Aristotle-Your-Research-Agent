# research_agent/retriever.py
from ddgs import DDGS
import feedparser
import urllib.parse
import wikipedia

class Retriever:
    def __init__(self):
        pass

    def web_search(self, query, max_results=3):
        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", "No title"),
                        "link": r.get("href") or r.get("url") or "No link available",
                        "snippet": r.get("body", r.get("snippet", ""))
                    })
        except Exception as e:
            results.append({"title": "Search error", "link": "", "snippet": f"Error: {e}"})
        return results

    def academic_search(self, query, max_results=3):
    # URL-encode the query to handle spaces and special characters
        encoded_query = urllib.parse.quote(query)
        
        base_url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}"
        feed = feedparser.parse(base_url)
        
        papers = []
        for entry in feed.entries:
            papers.append({
                "title": entry.title,
                "abstract": entry.summary,
                "authors": [a.name for a in entry.authors],
                "url": entry.link
            })
        
        return papers


    def wiki_summary(self, topic, sentences=5):
        try:
            return wikipedia.summary(topic, sentences=sentences)
        except wikipedia.exceptions.DisambiguationError as e:
            # return short list of options
            options = e.options[:5]
            return "Disambiguation. Possible pages: " + ", ".join(options)
        except Exception as e:
            return f"Wikipedia summary not found: {e}"

