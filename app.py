import streamlit as st
import subprocess
import os

# --- Page config ---
# Sets browser tab title and page layout
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
# Finds model relative to where app.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#MODEL_PATH = os.path.join(BASE_DIR, "model", "qwen2.5-1.5b-instruct-q4_k_m.gguf")
MODEL_PATH = r"C:\Users\user\adtc-2026-submission-template\model\qwen2.5-1.5b-instruct-q4_k_m.gguf"

# Try llama-bin in repo first
LLAMA_CLI = os.path.join(BASE_DIR, "llama-bin", "llama-cli.exe")

# If not found, use absolute path directly
if not os.path.exists(LLAMA_CLI):
    LLAMA_CLI = r"C:\Users\user\adtc-2026-submission-template\llama-bin\llama-cli.exe"

# --- System prompt ---
# Tells model its role as health assistant
SYSTEM_PROMPT = (
    "You are HealthBridge, an offline health education assistant. "
    "You help users understand symptoms, common treatments, and when to seek "
    "urgent medical care. You provide clear, simple health information for "
    "educational purposes only. You do not replace a doctor. "
    "Always answer health questions helpfully and clearly."
)

# --- Chat history ---
# st.session_state persists data across reruns within same session
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display past messages ---
# Loops through saved messages and renders each one
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User input box ---
# st.chat_input = text box pinned to bottom of page
user_input = st.chat_input("Ask a health question...")

if user_input:
    # Save user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # --- Call model ---
    with st.chat_message("assistant"):
        with st.spinner("HealthBridge is thinking..."):
            try:
                # Build command list to run llama-cli
                # Each item = one part of the terminal command
                cmd = [
                    LLAMA_CLI,
                    "-m", MODEL_PATH,          # model file path
                    "--system-prompt", SYSTEM_PROMPT,  # role instruction
                    "-p", user_input,          # user's question
                    "-n", "400",               # max tokens to generate
                    "--no-display-prompt",     # hide prompt from output
                    "-c", "2048",              # context window size
                    "--log-disable",           # suppress llama.cpp logs
                ]

                # Run command, capture output, timeout after 120 seconds
                result = subprocess.run(
                    cmd,
                    capture_output=True,   # grab stdout and stderr
                    text=True,             # return as string not bytes
                    timeout=600            # give up after 5 minutes
                )

                # Get response text from stdout
                response = result.stdout.strip()

                # If empty output, show error instead
                if not response:
                    response = "Sorry, I could not generate a response. Please try again."

            except subprocess.TimeoutExpired:
                # Model took too long
                response = "Response timed out. Please try a shorter question."

            except FileNotFoundError:
                # llama-cli binary not found
                response = f"Error: llama-cli not found at {LLAMA_CLI}. Run download_model.sh first."

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
        # Wipe chat history
        st.session_state.messages = []
        st.rerun()