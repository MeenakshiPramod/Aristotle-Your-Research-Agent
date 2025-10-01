# app.py
import streamlit as st
import google.generativeai as genai
from config import GEMINI_API_KEY
from research_agent.question_gen import QuestionGenerator
from research_agent.retriever import Retriever
from research_agent.summarizer import Summarizer
from research_agent.reporter import build_markdown_report, build_pdf_report_bytes

# Page config & CSS
st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")

# Simple CSS for card UI
st.markdown(
    """
    <style>
    .card {
      background: #ffffff;
      padding: 16px;
      border-radius: 10px;
      box-shadow: 0 4px 14px rgba(31, 41, 55, 0.08);
      margin-bottom: 12px;
    }
    .small {
      font-size:0.9rem;
      color: #6b7280;
    }
    h1, h2, h3, h4 {
    font-family: 'Lato', sans-serif;
    font-weight: 700;
}
    .search-box {
      display:flex;
      gap:8px;
    }
    /* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #4f46e5, #3b82f6);
    color: white;
    border-radius: 12px;
    padding: 10px 20px;
    border: none;
    transition: 0.3s ease-in-out;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #4338ca, #2563eb);
    transform: scale(1.03);
}

    </style>
    """,
    unsafe_allow_html=True,
)

# Configure Gemini
if not GEMINI_API_KEY:
    st.warning("Set GEMINI_API_KEY in your .env file (see README).")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Initialize helpers
qgen = QuestionGenerator(model)
retriever = Retriever()
summarizer = Summarizer(model)

# Sidebar controls
with st.sidebar:
    st.title("Settings")
    num_web = st.slider("Web results", min_value=1, max_value=5, value=3)
    num_papers = st.slider("arXiv papers", min_value=0, max_value=5, value=2)
    num_questions = st.slider("Number of questions", min_value=1, max_value=8, value=4)
    st.divider()
    st.markdown("**Export**")
    export_pdf = st.checkbox("Enable PDF export", value=True)
    export_md = st.checkbox("Enable Markdown export", value=True)
    st.divider()
    # st.markdown("Made with ❤️ by Meenakshi — Capstone MVP")

# Main UI
st.title("🔎Aristotle")
st.caption("Your AI-powered research assistant that generates research questions, fetches web & arXiv results, summarizes them, finds gaps, and exports reports.")

col1, col2 = st.columns([4,1])
with col1:
    topic = st.text_input("Enter a research topic", placeholder="e.g., AI in healthcare, federated learning, climate models...")
with col2:
    if st.button("🚀 Start Research") and topic:
        run = True
    else:
        run = False

if run and topic:
    with st.spinner("Generating research questions..."):
        questions = qgen.generate(topic, num_questions=num_questions)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("1️⃣ Research Questions")
    st.markdown(f"<div class='small'>{questions.replace(chr(10), '<br/>')}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Retrieve web + arXiv + wiki
    with st.spinner("Fetching web results..."):
        web_results = retriever.web_search(topic, max_results=num_web)
    with st.spinner("Fetching arXiv results..."):
        papers = retriever.academic_search(topic, max_results=num_papers) if num_papers>0 else []
    with st.spinner("Fetching Wikipedia summary..."):
        wiki_text = retriever.wiki_summary(topic, sentences=5)

    # Show web results in cards with summaries
    st.subheader("2️⃣ Web Results & Summaries")
    web_summaries = []
    for r in web_results:
        with st.expander(r["title"]):
            st.markdown(f"[Open link]({r['link']})")
            st.caption(r["snippet"])
            # Summarize snippet (cached)
            s = summarizer.summarize_text(r["snippet"])
            web_summaries.append((r["title"], s))
            st.markdown("**Summary:**")
            st.write(s)

    # Show arXiv results
    if papers:
        st.subheader("3️⃣ Academic Papers (arXiv)")
        for p in papers:
            st.markdown(f"**{p['title']}**")
            st.caption(", ".join(p["authors"]))
            st.write(p["abstract"])
            st.markdown(f"[Read on arXiv]({p['url']})")

    # Wikipedia
    st.subheader("4️⃣ Wikipedia Overview")
    st.info(wiki_text)

    # Gap analysis: ask Gemini to find missing pieces
    with st.spinner("Analyzing gaps in the current research..."):
        # combine main texts for context
        combined_context = "\n\n".join([s for _, s in web_summaries])
        # include arXiv abstracts too
        combined_context += "\n\n" + "\n\n".join([p["abstract"] for p in papers])
        gap_prompt = f"""
You are a research assistant. Based on the following collected summaries and abstracts:
{combined_context}

List 5 concise research gaps, missing perspectives, or underexplored questions that a researcher might pursue next.
Give each item as a single short sentence.
"""
        gap_resp = model.generate_content(gap_prompt)
        gap_text = gap_resp.text.strip()
        # split into lines for display
        gaps = [line.strip(" -\n") for line in gap_text.splitlines() if line.strip()]

    st.subheader("5️⃣ Gap Analysis")
    st.warning(gap_text)

    # Build report outputs
    st.markdown("---")
    st.subheader("6️⃣ Export Report")
    md_report = build_markdown_report(topic, questions, web_results, papers, wiki_text, web_summaries, gaps)
    pdf_bytes = None
    if export_pdf:
        with st.spinner("Generating PDF..."):
            pdf_bytes = build_pdf_report_bytes(topic, questions, web_results, papers, wiki_text, web_summaries, gaps)

    # Download buttons
    col_a, col_b = st.columns(2)
    if export_md:
        col_a.download_button("📄 Download Markdown", data=md_report, file_name=f"{topic.replace(' ','_')}_report.md", mime="text/markdown")
    if export_pdf and pdf_bytes:
        col_b.download_button("📥 Download PDF", data=pdf_bytes, file_name=f"{topic.replace(' ','_')}_report.pdf", mime="application/pdf")
    st.success("Done — report generated. You can expand cards to view details.")
