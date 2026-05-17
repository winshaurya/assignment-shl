import streamlit as st
import os
from dotenv import load_dotenv
from app.agent import RecommendationAgent
from app.retriever import HybridRetriever
from app.models import ChatMessage, MessageRole

# Load environment variables
load_dotenv()

# App Configuration & Styling
st.set_page_config(
    page_title="SHL Assessment Recommendation Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS
st.markdown("""
<style>
    /* Main body background styling */
    .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
    }
    
    /* Sleek gradient header */
    .gradient-text {
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    
    /* Assessment Recommendation Cards */
    .assessment-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .assessment-card:hover {
        transform: translateY(-2px);
        border-color: #6366f1;
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.2);
    }
    
    .assessment-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #38bdf8 !important;
        margin-bottom: 0.4rem;
        text-decoration: none !important;
    }
    
    .assessment-badge {
        display: inline-block;
        background-color: rgba(99, 102, 241, 0.25);
        color: #a5b4fc;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    
    /* Info box styling */
    .info-box {
        background: rgba(30, 41, 59, 0.5);
        border-left: 4px solid #38bdf8;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
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

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.shields.io/badge/SHL--Labs-AI--Intern--Assignment-indigo?style=for-the-badge", use_column_width=False)
    st.markdown("<h2 style='color: #38bdf8; font-size: 1.5rem;'>Settings & Info</h2>", unsafe_allow_html=True)
    
    # API Status Indicators
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        st.success("🟢 Gemini API Key Detected")
        st.caption(f"Active Model: `{os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')}`")
    else:
        st.warning("🟡 Using Rule-Based Fallback")
        st.info("To enable advanced reasoning, add `GEMINI_API_KEY` to your environment or `.env` file.")
        
    st.markdown("---")
    
    # Quick Sample Queries
    st.markdown("<h3 style='font-size: 1.1rem; color: #a5b4fc;'>💡 Quick-Start Templates</h3>", unsafe_allow_html=True)
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

# Main Application Panel
col_title, col_logo = st.columns([5, 1])
with col_title:
    st.markdown("<h1 class='gradient-text'>🔍 Conversational SHL Assessment Recommender</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 1.05rem;'>An intelligent RAG system that matches and retrieves official SHL assessments based on your exact recruitment specifications.</p>", unsafe_allow_html=True)

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

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
    
    # Generate Agent response
    with st.spinner("Analyzing requirements and matching assessments..."):
        agent_res = agent.respond(api_messages)
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
            st.markdown("<p style='font-size: 0.95rem; font-weight: 600; color: #a5b4fc; margin-top: 1rem;'>Recommended SHL Assessments:</p>", unsafe_allow_html=True)
            
            # Show cards in a clean dynamic grid
            cols = st.columns(min(len(recs), 3))
            for i, rec in enumerate(recs):
                col_idx = i % len(cols)
                with cols[col_idx]:
                    card_html = f"""
                    <div class="assessment-card">
                        <span class="assessment-badge">{rec['test_type']}</span>
                        <a href="{rec['url']}" target="_blank" class="assessment-title">🔗 {rec['name']}</a>
                        <p style="font-size: 0.85rem; color: #94a3b8; margin-top: 0.5rem; line-height: 1.4;">Official assessment link and specifications.</p>
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
    
    # Generate Agent response
    with st.spinner("Analyzing requirements and matching assessments..."):
        agent_res = agent.respond(api_messages)
        st.session_state.messages.append({
            "role": MessageRole.ASSISTANT,
            "content": agent_res.reply,
            "recommendations": [r.model_dump() for r in agent_res.recommendations]
        })
    st.rerun()
