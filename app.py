import streamlit as st
from src.helper import get_pdf_text, get_text_chunks, get_vector_store, get_conversational_chain
import os

# 💬 Handle user interaction
def handle_user_input(user_question):
    with st.spinner("Generating response..."):
        response = st.session_state.conversation({
            'question': user_question,
            'chat_history': st.session_state.chatHistory
        })
    st.session_state.chatHistory = response['chat_history']

# 🚀 Main Streamlit UI
def main():
    st.set_page_config("PDF QA with Groq", layout="wide")

    # Sidebar width adjustment
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                min-width: 350px;
                max-width: 350px;
            }
            .input-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-top: 30px;
            }
            .custom-input input {
                background-color: #111827;
                color: white;
                border: 1px solid #4b5563;
                border-radius: 10px;
                padding: 10px 15px;
                width: 100%;
            }
            .custom-submit {
                margin-top: 15px;
                background: linear-gradient(to right, #10b981, #059669);
                color: white;
                padding: 10px 25px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .custom-submit:hover {
                background: linear-gradient(to right, #059669, #047857);
                transform: scale(1.05);
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h1 style='display: flex; align-items: center; gap: 10px;'>
        🧾 Medical Prescription Analyzer (Groq + FAISS)
    </h1>
    <p style='color: #bbb; font-size: 16px; margin-top: -10px;'>
        ⚠️ Upload your medical prescription PDF and ask your queries. This tool is for informational purposes only and does not replace professional medical advice.
    </p>
    """, unsafe_allow_html=True)

    # 🔁 Session setup
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chatHistory" not in st.session_state:
        st.session_state.chatHistory = []

    # ➕ Input with Submit button below
    with st.container():
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        user_question = st.text_input(
            "", placeholder="Ask a question about your PDF files:",
            key="question_input", label_visibility="collapsed"
        )
        submit_clicked = st.button("Submit", key="submit_button")
        st.markdown('</div>', unsafe_allow_html=True)

    if submit_clicked and user_question and st.session_state.conversation:
        handle_user_input(user_question)

    # 📜 Show chat history with recent first and user-bot pairs
    chat_blocks = []
    for i in range(0, len(st.session_state.chatHistory), 2):
        if i + 1 < len(st.session_state.chatHistory):
            user_msg = st.session_state.chatHistory[i]
            bot_msg = st.session_state.chatHistory[i + 1]

            pair_html = f"""
            <div style="margin-bottom: 20px;">
                <!-- User message -->
                <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                    <div style="max-width: 80%; background-color: #f0f0f0; color: #000; padding: 10px 15px; border-radius: 15px 0px 15px 15px;">
                        <strong>👤 You:</strong><br>{user_msg.content}
                    </div>
                </div>
                <!-- Bot message -->
                <div style="display: flex; justify-content: flex-end;">
                    <div style="max-width: 80%; background-color: #e6f4ea; color: #000; padding: 10px 15px; border-radius: 0px 15px 15px 15px;">
                        <strong>🤖 Bot:</strong><br>{bot_msg.content}
                    </div>
                </div>
            </div>
            """
            chat_blocks.append(pair_html)

    # Show latest at the top
    for block in reversed(chat_blocks):
        st.markdown(block, unsafe_allow_html=True)

    # 📂 Sidebar for PDF Upload
    with st.sidebar:
        st.header("Upload PDFs")
        pdf_docs = st.file_uploader("Upload multiple PDFs", accept_multiple_files=True)
        if st.button("Submit & Process"):
            with st.spinner("Reading and indexing your files..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                vector_store = get_vector_store(text_chunks)
                st.session_state.conversation = get_conversational_chain(vector_store)
                st.success("PDFs processed successfully!")

# 🏁 Run the App
if __name__ == "__main__":
    main()
