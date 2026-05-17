import streamlit as st
import os
import time
from dotenv import load_dotenv
from app.agent import RecommendationAgent
from app.retriever import HybridRetriever
from app.models import ChatMessage, MessageRole

# Load environment variables
load_dotenv()

# App Configuration & Responsive Layout Setup
st.set_page_config(
    page_title="SHL Assessment Recommendation Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced Responsive CSS
st.markdown("""
<style>
    /* Main body background styling */
    .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
    }
    
    /* Sleek gradient header - highly responsive */
    .gradient-text {
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0.3rem;
        line-height: 1.2;
    }
    
    .gradient-subtext {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    
    /* Responsive Assessment Recommendation Cards */
    .assessment-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.6rem 0;
        transition: all 0.25s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .assessment-card:hover {
        transform: translateY(-2px);
        border-color: #6366f1;
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.15);
    }
    
    .assessment-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #38bdf8 !important;
        margin-bottom: 0.4rem;
        text-decoration: none !important;
        display: block;
    }
    
    .assessment-badge {
        display: inline-block;
        background-color: rgba(99, 102, 241, 0.25);
        color: #a5b4fc;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    
    /* Advanced progress and step pipeline card */
    .progress-pipeline {
        background: rgba(30, 41, 59, 0.4);
        border-left: 4px solid #6366f1;
        border-radius: 4px 12px 12px 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .progress-step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.4rem 0;
        font-size: 0.9rem;
    }
    
    /* Media Queries for Perfect Mobile Rendering */
    @media (max-width: 768px) {
        .gradient-text {
            font-size: 1.6rem;
        }
        .gradient-subtext {
            font-size: 0.9rem;
        }
        .assessment-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        .assessment-title {
            font-size: 1rem;
        }
        /* Tighten margins for smaller mobile viewports */
        .stApp {
            padding: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize Resources
@st.cache_resource
def get_retriever():
    retriever = HybridRetriever()
    retriever.load_or_build()
    return retriever

@st.cache_resource
def get_agent():
    retriever = get_retriever()
    return RecommendationAgent(retriever=retriever)

try:
    agent = get_agent()
except Exception as e:
    st.error(f"Error loading retriever catalog resources: {e}")
    st.stop()

# Sidebar Configuration & Profile Bio Card
with st.sidebar:
    st.image("https://img.shields.io/badge/SHL--Labs-AI--Intern--Assignment-indigo?style=for-the-badge", use_column_width=False)
    st.markdown("<h2 style='color: #38bdf8; font-size: 1.3rem; margin-top: 1rem; margin-bottom: 0.5rem;'>Settings & Configuration</h2>", unsafe_allow_html=True)
    
    # API Status Indicators
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        st.success("🟢 Gemini API Key Detected")
        st.caption(f"Model: `{os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')}`")
    else:
        st.warning("🟡 Using Rule-Based Fallback")
        st.info("To enable advanced reasoning, add `GEMINI_API_KEY` to your environment or `.env` file.")
        
    st.markdown("---")
    
    # Quick Sample Queries
    st.markdown("<h3 style='font-size: 1rem; color: #a5b4fc; margin-bottom: 0.5rem;'>💡 Quick-Start Templates</h3>", unsafe_allow_html=True)
    sample_queries = [
        "Need technical & personality assessments for a junior Java backend engineer.",
        "What aptitude/reasoning tests do you have for executive management hiring?",
        "Compare the OPQ (Occupational Personality Questionnaire) and General Ability Screen."
    ]
    
    for sq in sample_queries:
        if st.button(sq, key=sq, use_container_width=True):
            st.session_state.sample_click = sq

    st.markdown("---")
    
    # Control Actions
    if st.button("🧹 Clear Chat History", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Premium Responsive Profile Card
    profile_html = """
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 12px; padding: 1rem; margin-top: 1.5rem;">
        <h4 style="color: #38bdf8; font-size: 0.95rem; margin: 0 0 0.4rem 0; font-weight: 700; display: flex; align-items: center; gap: 0.3rem;">
            ⚙️ AI Engineer Profile
        </h4>
        <div style="font-size: 1.05rem; font-weight: 600; color: #f1f5f9; line-height: 1.2;">Shaurya Mishra</div>
        <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 0.8rem;">AI Engineering Candidate</div>
        <div style="display: flex; flex-direction: column; gap: 0.5rem; border-top: 1px solid rgba(148, 163, 184, 0.1); padding-top: 0.6rem;">
            <a href="https://github.com/winshaurya" target="_blank" style="text-decoration: none; color: #a5b4fc; font-size: 0.8rem; display: flex; align-items: center; gap: 0.4rem;">
                🐙 <b>GitHub:</b> @winshaurya
            </a>
            <a href="https://www.linkedin.com/in/shaurya-mishra-win" target="_blank" style="text-decoration: none; color: #a5b4fc; font-size: 0.8rem; display: flex; align-items: center; gap: 0.4rem;">
                💼 <b>LinkedIn:</b> shaurya-mishra-win
            </a>
            <a href="mailto:p.shauryamishra@gmail.com" style="text-decoration: none; color: #a5b4fc; font-size: 0.8rem; display: flex; align-items: center; gap: 0.4rem;">
                📧 <b>Email:</b> p.shauryamishra@gmail.com
            </a>
        </div>
    </div>
    """
    st.markdown(profile_html, unsafe_allow_html=True)

# Main Application Panel
st.markdown("<h1 class='gradient-text'>🔍 Conversational SHL Assessment Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p class='gradient-subtext'>An intelligent RAG system that matches and retrieves official SHL assessments based on your exact recruitment specifications.</p>", unsafe_allow_html=True)

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Grounded Multi-Step Progress Rendering Flow
def run_agent_with_progress(api_messages):
    progress_placeholder = st.empty()
    
    # Step 1 Animation
    progress_placeholder.markdown("""
    <div class="progress-pipeline">
        <div style="font-weight: 700; color: #a5b4fc; margin-bottom: 0.5rem;">🧠 Agentic RAG Context Flow</div>
        <div class="progress-step">🔵 <b>Phase 1:</b> Analyzing conversational intent & safety parameters...</div>
        <div class="progress-step" style="opacity: 0.4;">⚪ <b>Phase 2:</b> Searching Hybrid FAISS index database...</div>
        <div class="progress-step" style="opacity: 0.4;">⚪ <b>Phase 3:</b> Generating grounded assessment shortlist...</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(0.5)

    # Step 2 Animation
    progress_placeholder.markdown("""
    <div class="progress-pipeline">
        <div style="font-weight: 700; color: #a5b4fc; margin-bottom: 0.5rem;">🧠 Agentic RAG Context Flow</div>
        <div class="progress-step">🟢 <b>Phase 1:</b> Intent analyzed.</div>
        <div class="progress-step">🔵 <b>Phase 2:</b> Querying semantic retriever catalog (top-k bounds)...</div>
        <div class="progress-step" style="opacity: 0.4;">⚪ <b>Phase 3:</b> Generating grounded assessment shortlist...</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(0.5)

    # Call agent respond
    agent_res = agent.respond(api_messages)

    # Step 3 Animation
    progress_placeholder.markdown("""
    <div class="progress-pipeline">
        <div style="font-weight: 700; color: #a5b4fc; margin-bottom: 0.5rem;">🧠 Agentic RAG Context Flow</div>
        <div class="progress-step">🟢 <b>Phase 1:</b> Intent analyzed.</div>
        <div class="progress-step">🟢 <b>Phase 2:</b> FAISS catalog matching completed.</div>
        <div class="progress-step">🔵 <b>Phase 3:</b> Grounding outputs and generating final synthesis...</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(0.4)
    
    # Clean up progress bar
    progress_placeholder.empty()
    return agent_res

# If a sample query is clicked, simulate user sending it
if "sample_click" in st.session_state:
    clicked_prompt = st.session_state.pop("sample_click")
    st.session_state.messages.append({
        "role": MessageRole.USER,
        "content": clicked_prompt,
        "recommendations": []
    })
    
    # Generate api_messages from clean history
    api_messages = [
        ChatMessage(role=m["role"], content=m["content"])
        for m in st.session_state.messages
    ]
    
    # Generate Agent response with detailed pipeline flow
    agent_res = run_agent_with_progress(api_messages)
    st.session_state.messages.append({
        "role": MessageRole.ASSISTANT,
        "content": agent_res.reply,
        "recommendations": [r.model_dump() for r in agent_res.recommendations]
    })
    st.rerun()

# Display Chat Dialogue History
for msg in st.session_state.messages:
    role = msg["role"].value
    content = msg["content"]
    recs = msg.get("recommendations", [])

    with st.chat_message(role):
        st.write(content)
        
        # Display recommendations side-by-side as premium visual cards
        if recs:
            st.markdown("<p style='font-size: 0.95rem; font-weight: 600; color: #a5b4fc; margin-top: 1rem; margin-bottom: 0.2rem;'>Recommended SHL Assessments:</p>", unsafe_allow_html=True)
            
            # Show cards in a clean dynamic grid
            cols = st.columns(min(len(recs), 3))
            for i, rec in enumerate(recs):
                col_idx = i % len(cols)
                with cols[col_idx]:
                    card_html = f"""
                    <div class="assessment-card">
                        <span class="assessment-badge">Type: {rec['test_type']}</span>
                        <a href="{rec['url']}" target="_blank" class="assessment-title">🔗 {rec['name']}</a>
                        <p style="font-size: 0.82rem; color: #94a3b8; margin-top: 0.5rem; line-height: 1.4;">Official catalog details and specifications.</p>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

# User Chat Input
user_input = st.chat_input("Specify hiring requirements (e.g. role, skills, seniority, focus)...")
if user_input:
    # Render user query
    st.session_state.messages.append({
        "role": MessageRole.USER,
        "content": user_input,
        "recommendations": []
    })
    
    # Generate api_messages from clean history
    api_messages = [
        ChatMessage(role=m["role"], content=m["content"])
        for m in st.session_state.messages
    ]
    
    # Generate Agent response with detailed pipeline flow
    agent_res = run_agent_with_progress(api_messages)
    st.session_state.messages.append({
        "role": MessageRole.ASSISTANT,
        "content": agent_res.reply,
        "recommendations": [r.model_dump() for r in agent_res.recommendations]
    })
    st.rerun()
