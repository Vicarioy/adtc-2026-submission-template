import streamlit as st
import subprocess
import os
import asyncio

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
MODEL_PATH = os.path.join(BASE_DIR, "model", "qwen2.5-1.5b-instruct-q4_k_m.gguf")

#if not os.path.exists(MODEL_PATH):
    #st.error(f"Model file not found at `{MODEL_PATH}`. Please run `bash download_model.sh`.")
    #st.stop()

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
                # Ensure we have a valid string fallback for input
                safe_input = str(user_input) if user_input else ""
                
                # Clean prompt formatting
                formatted_prompt = f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n<|im_start|>user\n{safe_input}<|im_end|>\n<|im_start|>assistant\n"

                cmd = [
                    str(LLAMA_CLI),
                    "-m", str(MODEL_PATH),
                    "-p", formatted_prompt,
                    "-n", "400",
                    "-c", "2048",
                    "-t", "4",
                ]

                # This keeps the output inside Streamlit's safe thread-isolated context
                st.sidebar.text(f"Last executed: {' '.join(cmd)}")

                async def run_llama_async():
                    proc = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        stdin=asyncio.subprocess.PIPE
                    )
                    try:
                        # communicate(input=b"") instantly signals EOF to close stdin
                        stdout_bytes, stderr_bytes = await asyncio.wait_for(
                            proc.communicate(input=b""), 
                            timeout=300
                        )
                        return proc.returncode, stdout_bytes.decode(errors='ignore').strip(), stderr_bytes.decode(errors='ignore').strip()
                    except asyncio.TimeoutError:
                        try:
                            proc.kill()
                        except:
                            pass
                        raise TimeoutError

                # Run safely inside Streamlit's operational event loop
                returncode, stdout, stderr = asyncio.run(run_llama_async())

                if returncode != 0:
                    response = (
                        f"**Command failed with return code {returncode}**\n\n"
                        f"stderr:\n```\n{stderr}\n```"
                    )
                elif stdout:
                    # Clean up interactive menu boilerplate if present
                    if "available commands:" in stdout:
                        # Extract text after the final assistant tag block if needed
                        response = stdout.split("<|im_start|>assistant")[-1].strip()
                    else:
                        response = stdout
                else:
                    response = f"**No output from model.**\n\nstderr:\n```\n{stderr}\n```"

            except TimeoutError:
                response = "⏱️ Command timed out after 300 seconds."
            except FileNotFoundError as e:
                response = f"❌ Executable not found: {e.filename}"
            except Exception as e:
                response = f"❌ Unexpected error: {e}"

            # Display response safely
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