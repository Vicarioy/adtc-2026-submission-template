import streamlit as st
import os
from llama_cpp import Llama

# --- Page Config & UI/UX ---
st.set_page_config(
    page_title="HealthBridge Nigeria",
    page_icon="🏥",
    layout="centered"
)

# --- Emergency Guardrails ---
# Hardcoded triggers to catch critical situations before the AI even thinks
EMERGENCY_KEYWORDS = [
    "chest pain", "breathing", "poison", "bleeding", "unconscious", 
    "choking", "seizure", "stroke", "heart attack", "blood"
]

# --- Model Path ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "qwen2.5-1.5b-instruct-q4_k_m.gguf")

# --- Localized System Prompt ---
# Tuned specifically for local contexts and standard disclaimers
SYSTEM_PROMPT = (
    "You are HealthBridge, an offline AI health education assistant built for Nigeria. "
    "You provide clear, culturally relevant health information and first-aid education. "
    "If asked about prevalent local infectious diseases (like malaria, typhoid, or cholera), "
    "provide standard WHO/NCDC prevention and hydration advice. "
    "Crucially: You are an AI, NOT a doctor. You cannot diagnose or prescribe medication. "
    "Always politely advise users to visit a certified clinic or hospital for serious issues."
)

# --- Initialize Model (Cached) ---
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        st.error(f"Model file not found at `{MODEL_PATH}`.")
        st.stop()
    
    return Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,      
        n_threads=4,     
        verbose=False    
    )

try:
    llm = load_model()
except Exception as e:
    st.error(f"Failed to initialize model: {e}")
    st.stop()

# --- Header ---
st.title("🏥 HealthBridge")
st.caption("Offline AI Health Assistant — Fast, Safe, and 100% Local")
st.markdown("---")

# --- Chat History Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render past conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input & Main Logic ---
user_input = st.chat_input("Ask a health question...")

if user_input:
    # Save and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # --- Assistant Response Generation ---
    with st.chat_message("assistant"):
        
        # 1. Check Guardrails First
        is_emergency = any(word in user_input.lower() for word in EMERGENCY_KEYWORDS)
        if is_emergency:
            st.error("🚨 **EMERGENCY NOTICE:** Your message contains symptoms of a potential medical emergency. Please seek transport to the nearest hospital or medical clinic immediately. Do not wait for AI advice.")
            st.stop() # Halts the script here so the AI doesn't try to treat an emergency

        # 2. Proceed to Inference
        with st.spinner("HealthBridge is thinking..."):
            try:
                # ChatML Formatting for Qwen
                formatted_prompt = (
                    f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
                    f"<|im_start|>user\n{user_input}<|im_end|>\n"
                    f"<|im_start|>assistant\n"
                )

                # Execute with stream=True for real-time UI updates
                output_stream = llm(
                    formatted_prompt,
                    max_tokens=400,
                    temperature=0.3, # Lowered temperature slightly for more factual/clinical consistency
                    stop=["<|im_end|>"],
                    stream=True
                )
                
                # Generator function to yield tokens as they arrive
                def stream_pacing():
                    for chunk in output_stream:
                        yield chunk["choices"][0]["text"]

                # st.write_stream creates the cool "typing" effect
                response = st.write_stream(stream_pacing)

            except Exception as e:
                response = f"❌ Inference error: {e}"
                st.markdown(response)

    # Save final assistant response to state
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- Sidebar UI ---
with st.sidebar:
    st.markdown("### About HealthBridge")
    st.markdown(
        "HealthBridge Nigeria runs **100% offline** directly on your device CPU. "
        "No data leaves your computer, ensuring total privacy."
    )
    st.markdown("---")
    st.warning("⚠️ **Disclaimer:** This tool provides health education only. It is not a diagnostic tool. Always consult a qualified medical professional.")
    st.markdown("---")
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()