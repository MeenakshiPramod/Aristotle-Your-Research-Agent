# research_agent/summarizer.py
import google.generativeai as genai

class Summarizer:
    def __init__(self, model):
        self.model = model

    def summarize_text(self, text, max_words=100):
        """Summarize a text chunk into a concise researcher-friendly summary."""
        if not text:
            return "No text to summarize."
        prompt = f"""
Summarize the following text in about {max_words} words for a researcher.
Highlight the main points, methods (if mentioned), and findings or claims.

Text:
\"\"\"
{text}
\"\"\"
"""
        resp = self.model.generate_content(prompt)
        return resp.text.strip()
