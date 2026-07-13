import streamlit as st
import os
from llama_cpp import Llama

# --- Page config ---
st.set_page_config(
    page_title="HealthBridge",
    page_icon="🏥",
    layout="centered"
)

# --- Header ---
st.title("🏥 HealthBridge")
st.caption("Offline AI Health Assistant — No internet required")
st.markdown("---")

# --- Model path ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "qwen2.5-1.5b-instruct-q4_k_m.gguf")

# --- System prompt ---
SYSTEM_PROMPT = (
    "You are HealthBridge, an offline health education assistant. "
    "You help users understand symptoms, common treatments, and when to seek "
    "urgent medical care. You provide clear, simple health information for "
    "educational purposes only. You do not replace a doctor. "
    "Always answer health questions helpfully and clearly."
)

# --- Initialize Model (Cached to load only once) ---
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        st.error(f"Model file not found at `{MODEL_PATH}`.")
        st.stop()
    
    # Loads the GGUF model directly into Python memory
    return Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,      # Context window
        n_threads=4,     # Safe core count
        verbose=False    # Prevents terminal stream pollution
    )

try:
    llm = load_model()
except Exception as e:
    st.error(f"Failed to initialize model: {e}")
    st.stop()

# --- Chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display past messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User input box ---
user_input = st.chat_input("Ask a health question...")

if user_input:
    # Save user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # --- Call model natively ---
    with st.chat_message("assistant"):
        with st.spinner("HealthBridge is thinking..."):
            try:
                # Format using standard ChatML format that Qwen explicitly expects
                formatted_prompt = (
                    f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
                    f"<|im_start|>user\n{user_input}<|im_end|>\n"
                    f"<|im_start|>assistant\n"
                )

                # Generate the inference response natively
                output = llm(
                    formatted_prompt,
                    max_tokens=400,
                    temperature=0.7,
                    stop=["<|im_end|>"] # Cleanly cuts generation off at end of response
                )
                
                response = output["choices"][0]["text"].strip()

            except Exception as e:
                response = f"❌ Inference error: {e}"

            # Display response
            st.markdown(response)

    # Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- Sidebar info ---
with st.sidebar:
    st.markdown("### About")
    st.markdown(
        "HealthBridge Nigeria runs **100% offline**. "
        "No data leaves your device. "
        "Built for Nigerians with limited internet access."
    )
    st.markdown("---")
    st.markdown("⚠️ *This tool provides health education only. Always consult a qualified doctor for medical advice.*")
    st.markdown("---")
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()