import streamlit as st
import os
import time
import requests
from dotenv import load_dotenv
from app.agent import RecommendationAgent
from app.retriever import HybridRetriever
from app.models import ChatMessage, MessageRole

# Load environment variables
load_dotenv()

# App Configuration & Responsive Layout Setup
st.set_page_config(
    page_title="SHL Assessment Recommendation Agent",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "https://winshaurya1-shl-assessment-api.hf.space")

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
    
    /* Responsive Assessment Recommendation Cards with very small rounded corners */
    .assessment-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 4px;
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
        border-radius: 2px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    
    /* Advanced progress and step pipeline card with very small rounded corners */
    .progress-pipeline {
        background: rgba(30, 41, 59, 0.4);
        border-left: 4px solid #6366f1;
        border-radius: 2px 4px 4px 2px;
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
        .stApp {
            padding: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize Local Fallback Resources
@st.cache_resource
def get_local_retriever():
    retriever = HybridRetriever()
    retriever.load_or_build()
    return retriever

@st.cache_resource
def get_local_agent():
    retriever = get_local_retriever()
    return RecommendationAgent(retriever=retriever)

# Sidebar Configuration & Profile Bio Card
with st.sidebar:
    st.image("https://img.shields.io/badge/SHL--Labs-AI--Intern--Assignment-indigo?style=for-the-badge", use_column_width=False)
    st.markdown("<h2 style='color: #38bdf8; font-size: 1.3rem; margin-top: 1rem; margin-bottom: 0.5rem;'>Settings & Configuration</h2>", unsafe_allow_html=True)
    
    # Connection Mode Display
    st.markdown(f"<div style='font-size: 0.82rem; color: #94a3b8; margin-bottom: 0.5rem;'>Backend Host: <code style='color: #38bdf8;'>{BACKEND_URL}</code></div>", unsafe_allow_html=True)
    
    # API Status Indicators with clean SVGs
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        st.markdown("<div style='font-size: 0.9rem; color: #f1f5f9; padding: 0.4rem 0.6rem; background: rgba(34, 197, 94, 0.15); border-left: 3px solid #22c55e; margin-bottom: 0.5rem; border-radius: 2px;'><svg width='8' height='8' style='vertical-align: middle; margin-right: 6px; margin-bottom: 2px;'><circle cx='4' cy='4' r='4' fill='#22c55e'/></svg>Gemini API Key Detected</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size: 0.9rem; color: #f1f5f9; padding: 0.4rem 0.6rem; background: rgba(234, 179, 8, 0.15); border-left: 3px solid #eab308; margin-bottom: 0.5rem; border-radius: 2px;'><svg width='8' height='8' style='vertical-align: middle; margin-right: 6px; margin-bottom: 2px;'><circle cx='4' cy='4' r='4' fill='#eab308'/></svg>Using Local Reasoning</div>", unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Quick Sample Queries with custom lightbulb SVG
    st.markdown("<h3 style='font-size: 1rem; color: #a5b4fc; margin-bottom: 0.5rem;'><svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='#a5b4fc' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align: middle; margin-right: 6px; margin-bottom: 2px;'><path d='M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A5.5 5.5 0 0 0 12.5 2.5a5.5 5.5 0 0 0-5 5.5c0 1.3.5 2.6 1.5 3.5.7.8 1.3 1.5 1.5 2.5'/><path d='M9 18h6'/><path d='M10 22h4'/></svg>Quick-Start Templates</h3>", unsafe_allow_html=True)
    sample_queries = [
        "Need technical & personality assessments for a junior Java backend engineer.",
        "What aptitude/reasoning tests do you have for executive management hiring?",
        "Compare the OPQ (Occupational Personality Questionnaire) and General Ability Screen."
    ]
    
    for sq in sample_queries:
        if st.button(sq, key=sq, use_container_width=True):
            st.session_state.sample_click = sq

    st.markdown("---")
    
    # Control Actions with custom trash/clear SVG
    if st.button("Clear Chat History", key="clear_chat_button", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Premium Profile Card with very small rounded corners and custom professional SVGs
    profile_html = """
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 4px; padding: 1rem; margin-top: 1.5rem;">
        <h4 style="color: #38bdf8; font-size: 0.95rem; margin: 0 0 0.4rem 0; font-weight: 700; display: flex; align-items: center; gap: 0.4rem;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
            AI Engineer Profile
        </h4>
        <div style="font-size: 1.05rem; font-weight: 600; color: #f1f5f9; line-height: 1.2;">Shaurya Mishra</div>
        <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 0.8rem;">AI Engineering Candidate</div>
        <div style="display: flex; flex-direction: column; gap: 0.5rem; border-top: 1px solid rgba(148, 163, 184, 0.1); padding-top: 0.6rem;">
            <a href="https://github.com/winshaurya" target="_blank" style="text-decoration: none; color: #a5b4fc; font-size: 0.8rem; display: flex; align-items: center; gap: 0.4rem;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle;"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>
                <b>GitHub:</b> @winshaurya
            </a>
            <a href="https://www.linkedin.com/in/shaurya-mishra-win" target="_blank" style="text-decoration: none; color: #a5b4fc; font-size: 0.8rem; display: flex; align-items: center; gap: 0.4rem;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle;"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
                <b>LinkedIn:</b> shaurya-mishra-win
            </a>
            <a href="mailto:p.shauryamishra@gmail.com" style="text-decoration: none; color: #a5b4fc; font-size: 0.8rem; display: flex; align-items: center; gap: 0.4rem;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle;"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                <b>Email:</b> p.shauryamishra@gmail.com
            </a>
        </div>
    </div>
    """
    st.markdown(profile_html, unsafe_allow_html=True)

# Main Application Panel - No emojis
st.markdown("<h1 class='gradient-text'>Conversational SHL Assessment Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p class='gradient-subtext'>An intelligent RAG system that matches and retrieves official SHL assessments based on your exact recruitment specifications.</p>", unsafe_allow_html=True)

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hybrid API and Local Fallback Request Executor
def execute_chat_query(api_messages):
    # Prepare payload
    payload = {
        "messages": [
            {"role": m.role.value, "content": m.content}
            for m in api_messages
        ]
    }
    
    # 1. Attempt API request to Hugging Face FastAPI backend
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json=payload,
            timeout=8.0 # High responsiveness boundary
        )
        if response.status_code == 200:
            data = response.json()
            # Parse into a duck-typed response matching local structure
            class APIResponse:
                def __init__(self, reply, recommendations, end_of_conversation):
                    self.reply = reply
                    self.end_of_conversation = end_of_conversation
                    # Map dict recommendations back to model objects
                    class Rec:
                        def __init__(self, name, url, test_type):
                            self.name = name
                            self.url = url
                            self.test_type = test_type
                        def model_dump(self):
                            return {"name": self.name, "url": self.url, "test_type": self.test_type}
                    
                    self.recommendations = [
                        Rec(r["name"], r["url"], r["test_type"])
                        for r in recommendations
                    ]
            
            return APIResponse(
                data["reply"],
                data["recommendations"],
                data.get("end_of_conversation", False)
            )
            
    except Exception as e:
        # Gracefully log API disruption and activate local fallback
        pass

    # 2. Local Fallback Route (Zero-latency Python execution)
    local_agent = get_local_agent()
    return local_agent.respond(api_messages)

# Grounded Multi-Step Progress Rendering Flow with clean status dot SVGs
def run_agent_with_progress(api_messages):
    progress_placeholder = st.empty()
    
    # Step 1 Animation
    progress_placeholder.markdown("""
    <div class="progress-pipeline">
        <div style="font-weight: 700; color: #a5b4fc; margin-bottom: 0.5rem;">Agentic RAG Context Flow</div>
        <div class="progress-step"><svg width="8" height="8" style="vertical-align: middle; margin-right: 4px;"><circle cx="4" cy="4" r="4" fill="#3b82f6"/></svg> <b>Phase 1:</b> Analyzing conversational intent and safety parameters...</div>
        <div class="progress-step" style="opacity: 0.4;"><svg width="8" height="8" style="vertical-align: middle; margin-right: 4px;"><circle cx="4" cy="4" r="4" fill="#64748b"/></svg> <b>Phase 2:</b> Searching Hybrid FAISS index database...</div>
        <div class="progress-step" style="opacity: 0.4;"><svg width="8" height="8" style="vertical-align: middle; margin-right: 4px;"><circle cx="4" cy="4" r="4" fill="#64748b"/></svg> <b>Phase 3:</b> Generating grounded assessment shortlist...</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(0.4)

    # Step 2 Animation
    progress_placeholder.markdown("""
    <div class="progress-pipeline">
        <div style="font-weight: 700; color: #a5b4fc; margin-bottom: 0.5rem;">Agentic RAG Context Flow</div>
        <div class="progress-step"><svg width="8" height="8" style="vertical-align: middle; margin-right: 4px;"><circle cx="4" cy="4" r="4" fill="#22c55e"/></svg> <b>Phase 1:</b> Intent analyzed.</div>
        <div class="progress-step"><svg width="8" height="8" style="vertical-align: middle; margin-right: 4px;"><circle cx="4" cy="4" r="4" fill="#3b82f6"/></svg> <b>Phase 2:</b> Querying semantic retriever catalog (top-k bounds)...</div>
        <div class="progress-step" style="opacity: 0.4;"><svg width="8" height="8" style="vertical-align: middle; margin-right: 4px;"><circle cx="4" cy="4" r="4" fill="#64748b"/></svg> <b>Phase 3:</b> Generating grounded assessment shortlist...</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(0.4)

    # Execute Hybrid query
    agent_res = execute_chat_query(api_messages)

    # Step 3 Animation
    progress_placeholder.markdown("""
    <div class="progress-pipeline">
        <div style="font-weight: 700; color: #a5b4fc; margin-bottom: 0.5rem;">Agentic RAG Context Flow</div>
        <div class="progress-step"><svg width="8" height="8" style="vertical-align: middle; margin-right: 4px;"><circle cx="4" cy="4" r="4" fill="#22c55e"/></svg> <b>Phase 1:</b> Intent analyzed.</div>
        <div class="progress-step"><svg width="8" height="8" style="vertical-align: middle; margin-right: 4px;"><circle cx="4" cy="4" r="4" fill="#22c55e"/></svg> <b>Phase 2:</b> FAISS catalog matching completed.</div>
        <div class="progress-step"><svg width="8" height="8" style="vertical-align: middle; margin-right: 4px;"><circle cx="4" cy="4" r="4" fill="#3b82f6"/></svg> <b>Phase 3:</b> Grounding outputs and generating final synthesis...</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(0.3)
    
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
                        <a href="{rec['url']}" target="_blank" class="assessment-title"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle; margin-right: 4px; margin-bottom: 2px;"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>{rec['name']}</a>
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
