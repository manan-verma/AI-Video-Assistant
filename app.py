import streamlit as st
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

st.set_page_config(page_title="AI Video Assistant", page_icon="🎥", layout="wide")

def run_pipeline(source: str, language: str = "english") -> dict:
    chunks = process_input(source)
    transcript = transcribe_all(chunks, language)
    title = generate_title(transcript)
    summary = summarize(transcript)
    action_item = extract_action_items(transcript)
    decisions = extract_key_decisions(transcript)
    questions = extract_questions(transcript)
    rag_chain = build_rag_chain(transcript)
    
    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_item,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }

if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("⚙️ Configuration")
    source_input = st.text_input("YouTube URL or Local File Path")
    language_input = st.selectbox("Language", ["english", "hinglish"])
    process_button = st.button("Process Media", type="primary", use_container_width=True)

if process_button and source_input:
    with st.spinner("Processing media and generating insights..."):
        try:
            st.session_state.pipeline_result = run_pipeline(source_input, language_input)
            st.session_state.messages = []
            st.success("Processing complete!")
        except Exception as e:
            st.error(f"An error occurred during processing: {e}")

if st.session_state.pipeline_result:
    res = st.session_state.pipeline_result
    
    st.title(f"📌 {res['title']}")
    
    tab_overview, tab_details, tab_transcript, tab_chat = st.tabs([
        "📋 Overview", 
        "✅ Actions & Decisions", 
        "📝 Transcript", 
        "💬 Chat Assistant"
    ])
    
    with tab_overview:
        st.subheader("Summary")
        st.write(res["summary"])
        st.divider()
        st.subheader("❓ Open Questions")
        st.write(res["open_questions"])
        
    with tab_details:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Action Items")
            st.info(res["action_items"])
        with col2:
            st.subheader("🔑 Key Decisions")
            st.success(res["key_decisions"])
            
    with tab_transcript:
        st.subheader("Raw Transcript")
        with st.container(height=400):
            st.write(res["transcript"])
            
    with tab_chat:
        st.subheader("Chat with your meeting")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        if prompt := st.chat_input("Ask a question about this meeting..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = ask_question(res["rag_chain"], prompt)
                    st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

else:
    st.info("👈 Enter a media source in the sidebar and click **Process Media** to begin.")