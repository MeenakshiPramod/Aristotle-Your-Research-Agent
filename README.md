# 🤖 Aristotle: Your Self Research Agent

An AI-powered research assistant built with **Streamlit** and **Google Generative AI**, designed to streamline knowledge discovery, summarize large texts, and provide interactive chatbot-style responses. This project demonstrates the integration of Generative AI APIs, retrieval-augmented generation (RAG)-like workflows, and an intuitive web-based UI for real-world research tasks.

---
## Live Demo
https://aristotle-your-research-agent.streamlit.app/
---
## 🚀 Features

### 🔍 Research Assistance
* Accepts custom queries or topics and generates structured research insights.
* Provides summarized responses for faster knowledge absorption.
* Supports multi-turn conversations to refine queries and drill deeper.

### 💬 Chatbot Functionality
* Interactive chat interface for Q&A.
* Context-aware responses that mimic a research assistant.
* Handles follow-up questions dynamically.

### 📄 Content Summarization
* Summarizes articles, reports, or long documents into concise, easy-to-read points.
* Extracts key insights, statistics, and highlights from input text.

### 🎯 Gap Analysis
* Identifies missing areas in research or knowledge gaps.
* Suggests next directions, references, or questions to strengthen the research scope.

### 🛠️ Configurable Workflow
* Adjustable response depth (summary vs. detailed).
* Flexible prompting system for experimentation with queries.

---

## 📂 Tech Stack
* **Frontend**: Streamlit
* **Backend**: Python 3.10+
* **AI Engine**: Google Generative AI (Gemini)
* **Deployment**: Streamlit Cloud

---

## 🏗️ Project Relevance
* ✅ Demonstrates full-stack AI application development.
* ✅ Integrates Generative AI models into a production-like workflow.
* ✅ Solves a real-world problem: accelerating research and learning.
* ✅ Showcases UI/UX design, API integration, and prompt engineering skills.
* ✅ Relevant for startups in AI, EdTech, SaaS, and productivity tools.


---

## ⚙️ Setup & Installation
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/self-research-agent.git](https://github.com/your-username/self-research-agent.git)
    cd self-research-agent
    ```
2.  **Create a virtual environment & activate it:**
    ```bash
    # Mac/Linux
    python -m venv venv
    source venv/bin/activate
    
    # Windows
    python -m venv venv
    venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up environment variables in `.env`:**
    ```
    GOOGLE_API_KEY=your_api_key_here
    ```
5.  **Run the app locally:**
    ```bash
    streamlit run app.py
    ```

---

## ☁️ Deployment on Streamlit Cloud
1.  Push your code to a public GitHub repository.
2.  Go to Streamlit Cloud -> New App.
3.  Connect your GitHub repo and select `app.py` as the entry point.
4.  Add `GOOGLE_API_KEY` as a Secret under `Settings` -> `Secrets`.
5.  Deploy 🎉

---

## 📊 Future Enhancements
* **🔗 Integrate external knowledge sources** (e.g., arXiv, PubMed, Wikipedia).
* **📑 Enable document uploads** (PDF/Word) for summarization.
* **🧠 Add vector database** (Pinecone/FAISS) for RAG-style memory.
* **🌐 Multi-language support** for global users.
* **📱 Mobile-responsive UI.**

---

## 📌 Why This Project Matters
In today’s AI-driven world, the ability to build intelligent, user-friendly, and practical tools sets candidates apart. This project not only highlights technical skills but also the ability to think critically about user needs and product relevance.

---

## 👤 Author
**Meenakshi Pramod**
* 🚀 AI & Web Development Enthusiast
* 💡 Passionate about building meaningful applications with Generative AI
  
✨ If you like this project, consider giving it a ⭐ on GitHub!
