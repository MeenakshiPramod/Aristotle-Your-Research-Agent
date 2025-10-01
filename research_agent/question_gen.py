# research_agent/question_gen.py
import google.generativeai as genai

class QuestionGenerator:
    def __init__(self, model):
        self.model = model

    def generate(self, topic, num_questions=5):
        prompt = f"""
Generate {num_questions} concise research-style questions about the topic: "{topic}".
Number them and keep them clear and focused for academic research.
"""
        resp = self.model.generate_content(prompt)
        return resp.text.strip()
