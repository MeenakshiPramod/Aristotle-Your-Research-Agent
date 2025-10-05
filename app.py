# app.py
import streamlit as st
import google.generativeai as genai
from config import GEMINI_API_KEY
from research_agent.question_gen import QuestionGenerator
from research_agent.retriever import Retriever
from research_agent.summarizer import Summarizer
from research_agent.reporter import build_markdown_report, build_pdf_report_bytes
from research_agent.chatbot import ResearchChatbot

# ---------------- Page config & CSS ----------------
st.set_page_config(page_title="Aristotle - Research Agent", page_icon="🔎", layout="wide")
st.markdown("""
<style>
.card { background:#fff; padding:16px; border-radius:10px; box-shadow:0 4px 14px rgba(31,41,55,0.08); margin-bottom:12px; }
.small { font-size:0.9rem; color:#6b7280; }
h1,h2,h3,h4 { font-family:'Lato',sans-serif; font-weight:700; }
.stButton>button { background:linear-gradient(90deg,#4f46e5,#3b82f6); color:white; border-radius:12px; padding:10px 20px; border:none; transition:0.3s ease-in-out; }
.stButton>button:hover { background:linear-gradient(90deg,#4338ca,#2563eb); transform:scale(1.03); }
.chat-box { background:#f9fafb; padding:12px; border-radius:10px; margin-bottom:10px; }
.user-msg { color:#1f2937; font-weight:600; }
.ai-msg { color:#111827; font-style:italic; }
</style>
""", unsafe_allow_html=True)

# ---------------- Configure Gemini ----------------
if not GEMINI_API_KEY:
    st.warning("Set GEMINI_API_KEY in your .env file (see README).")
genai.configure(api_key=GEMINI_API_KEY)

# Create model once (use generation_config if you want global settings)
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------- Initialize helpers ----------------
qgen = QuestionGenerator(model)
retriever = Retriever()
summarizer = Summarizer(model)

# ---------------- Initialize persistent session state ----------------
if "research_done" not in st.session_state:
    st.session_state.research_done = False
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "questions" not in st.session_state:
    st.session_state.questions = ""
if "web_results" not in st.session_state:
    st.session_state.web_results = []
if "papers" not in st.session_state:
    st.session_state.papers = []
if "wiki_text" not in st.session_state:
    st.session_state.wiki_text = ""
if "web_summaries" not in st.session_state:
    st.session_state.web_summaries = []
if "combined_context" not in st.session_state:
    st.session_state.combined_context = ""
if "gap_text" not in st.session_state:
    st.session_state.gap_text = ""
if "md_report" not in st.session_state:
    st.session_state.md_report = ""
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of dicts: {"role":"user"/"assistant","text":...}

# ---------------- Sidebar controls ----------------
with st.sidebar:
    st.title("Settings")
    num_web = st.slider("Web results", 1, 5, 3)
    num_papers = st.slider("arXiv papers", 0, 5, 2)
    num_questions = st.slider("Number of questions", 1, 8, 4)
    st.divider()
    st.markdown("**Export**")
    export_pdf = st.checkbox("Enable PDF export", value=True)
    export_md = st.checkbox("Enable Markdown export", value=True)

# ---------------- Main UI ----------------
st.title("🔎 Aristotle")
st.caption("Your AI-powered research assistant that generates research questions, fetches web & arXiv results, summarizes them, finds gaps, and exports reports.")

col1, col2 = st.columns([4, 1])
with col1:
    topic_input = st.text_input("Enter a research topic", value=st.session_state.topic, placeholder="e.g., AI in healthcare, federated learning, climate models...")
with col2:
    start_pressed = st.button("🚀 Start Research")

# If user starts new research, run the pipeline and save results into session_state
if start_pressed and topic_input:
    st.session_state.topic = topic_input
    st.session_state.research_done = False  # in progress

    # 1) Questions
    with st.spinner("Generating research questions..."):
        st.session_state.questions = qgen.generate(topic_input, num_questions=num_questions) or ""

    # 2) Retrievals
    with st.spinner("Fetching web results..."):
        st.session_state.web_results = retriever.web_search(topic_input, max_results=num_web)
    with st.spinner("Fetching arXiv results..."):
        st.session_state.papers = retriever.academic_search(topic_input, max_results=num_papers) if num_papers else []
    with st.spinner("Fetching Wikipedia summary..."):
        st.session_state.wiki_text = retriever.wiki_summary(topic_input, sentences=5) or ""

    # 3) Summaries (web snippets)
    st.session_state.web_summaries = []
    with st.spinner("Summarizing web results..."):
        for r in st.session_state.web_results:
            snippet = r.get("snippet", "") or ""
            s = summarizer.summarize_text(snippet) if snippet else "No snippet to summarize."
            st.session_state.web_summaries.append((r.get("title", "No title"), s))

    # 4) Combined context (keep modest size)
    parts = []
    if st.session_state.wiki_text:
        parts.append("Wikipedia summary:\n" + st.session_state.wiki_text)
    if st.session_state.web_summaries:
        web_texts = "\n\n".join([f"{t}: {s}" for t, s in st.session_state.web_summaries])
        parts.append("Web summaries:\n" + web_texts)
    if st.session_state.papers:
        paper_texts = "\n\n".join([p.get("abstract","") for p in st.session_state.papers])
        parts.append("Paper abstracts:\n" + paper_texts)
    combined = "\n\n".join(parts)
    # truncate context to avoid giant prompts (adjust limit as needed)
    def _truncate(text, max_chars=12000):
        if not text:
            return text
        return text if len(text) <= max_chars else text[-max_chars:]
    st.session_state.combined_context = _truncate(combined, max_chars=12000)

    # 5) Gap analysis using the same Gemini-backed chatbot (reuses parsing logic)
    chatbot_agent = ResearchChatbot(model, context=st.session_state.combined_context)
    gap_question = "List 5 concise research gaps, each as a single short sentence (one per line). Keep each under 25 words."
    with st.spinner("Finding research gaps..."):
        st.session_state.gap_text = chatbot_agent.answer(gap_question)

    # 6) Build reports and save
    st.session_state.md_report = build_markdown_report(
        st.session_state.topic,
        st.session_state.questions,
        st.session_state.web_results,
        st.session_state.papers,
        st.session_state.wiki_text,
        st.session_state.web_summaries,
        st.session_state.gap_text.splitlines()
    )
    st.session_state.pdf_bytes = None
    if export_pdf:
        with st.spinner("Generating PDF..."):
            st.session_state.pdf_bytes = build_pdf_report_bytes(
                st.session_state.topic,
                st.session_state.questions,
                st.session_state.web_results,
                st.session_state.papers,
                st.session_state.wiki_text,
                st.session_state.web_summaries,
                st.session_state.gap_text.splitlines()
            )

    st.session_state.research_done = True
    st.success("Research run complete — results saved. Scroll down to view outputs and chat.")

# ---------------- If research is done, show results (from session_state) ----------------
if st.session_state.research_done:
    # 1) Questions
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("1️⃣ Research Questions")
    st.markdown(f"<div class='small'>{st.session_state.questions.replace(chr(10), '<br/>')}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2) Web results & summaries
    st.subheader("2️⃣ Web Results & Summaries")
    for idx, r in enumerate(st.session_state.web_results):
        title = r.get("title", f"Result {idx+1}")
        link = r.get("link", "")
        snippet = r.get("snippet", "")
        with st.expander(title):
            if link:
                st.markdown(f"[Open link]({link})")
            if snippet:
                st.caption(snippet)
            # show our summary
            try:
                summary = st.session_state.web_summaries[idx][1]
            except Exception:
                summary = "Summary unavailable."
            st.markdown("**Summary:**")
            st.write(summary)

    # 3) Papers
    if st.session_state.papers:
        st.subheader("3️⃣ Academic Papers (arXiv)")
        for p in st.session_state.papers:
            st.markdown(f"**{p.get('title','Untitled')}**")
            st.caption(", ".join(p.get("authors", [])))
            st.write(p.get("abstract",""))
            if p.get("url"):
                st.markdown(f"[Read on arXiv]({p.get('url')})")

    # 4) Wikipedia
    st.subheader("4️⃣ Wikipedia Overview")
    st.info(st.session_state.wiki_text)

    # 5) Gap analysis
    st.subheader("5️⃣ Gap Analysis")
    st.warning(st.session_state.gap_text)

    # 6) Export buttons
    st.markdown("---")
    st.subheader("6️⃣ Export Report")
    col_a, col_b = st.columns(2)
    if export_md:
        col_a.download_button("📄 Download Markdown", data=st.session_state.md_report,
                              file_name=f"{st.session_state.topic.replace(' ','_')}_report.md", mime="text/markdown")
    if export_pdf and st.session_state.pdf_bytes:
        col_b.download_button("📥 Download PDF", data=st.session_state.pdf_bytes,
                              file_name=f"{st.session_state.topic.replace(' ','_')}_report.pdf", mime="application/pdf")

    st.success("Done — report available for download.")

    # ---------------- Chatbot UI (outside of mutation to preserve across reruns) ----------------
    st.markdown("---")
    st.subheader("7️⃣ Chat with Research Assistant")

    # Build the chatbot fresh each rerun from saved context
    chatbot_agent = ResearchChatbot(model, context=st.session_state.combined_context)

    # Show previous chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-box user-msg'>👤 {msg['text']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-box ai-msg'>🤖 {msg['text']}</div>", unsafe_allow_html=True)

    # Use st.chat_input for nicer UX
    user_q = st.chat_input("Ask Aristotle about this research...")

    if user_q:
        # append user message
        st.session_state.chat_history.append({"role": "user", "text": user_q})
        st.markdown(f"<div class='chat-box user-msg'>👤 {user_q}</div>", unsafe_allow_html=True)

        # Streamed response (best-effort). If streaming fails, fallback to .answer()
        full_reply = ""
        assistant_placeholder = st.empty()
        for chunk in chatbot_agent.stream_answer(user_q):
            # If stream yields an error string, fallback to non-stream
            if isinstance(chunk, str) and chunk.startswith("[Error while streaming"):
                # fallback
                full_reply = chatbot_agent.answer(user_q)
                assistant_placeholder.markdown(f"<div class='chat-box ai-msg'>🤖 {full_reply}</div>", unsafe_allow_html=True)
                break
            else:
                full_reply += str(chunk)
                assistant_placeholder.markdown(f"<div class='chat-box ai-msg'>🤖 {full_reply}</div>", unsafe_allow_html=True)

        # if streaming didn't yield anything (empty), ensure we produce a reply
        if not full_reply:
            full_reply = chatbot_agent.answer(user_q)

        # save assistant reply
        st.session_state.chat_history.append({"role": "assistant", "text": full_reply})
