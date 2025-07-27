import streamlit as st
from rag_system import get_transcript, create_vector_store, create_rag_chain

st.set_page_config(layout="wide", page_title="YouTube Video Chat")
st.title("Chat with any YouTube Video 💬")

# Initialize session state to store data across reruns
if 'rag_chain' not in st.session_state:
    st.session_state.rag_chain = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar for inputting the URL ---
with st.sidebar:
    st.header("Video Input")
    youtube_url = st.text_input("Enter YouTube Video URL:")
    
    if st.button("Process Video"):
        if youtube_url:
            with st.spinner("Processing video... This may take a moment."):
                try:
                    # Clear previous chat and chain
                    st.session_state.messages = []
                    st.session_state.rag_chain = None
                    
                    # 1. Get Transcript
                    transcript = get_transcript(youtube_url)
                    
                    # 2. Create Vector Store
                    vector_store = create_vector_store(transcript)
                    
                    # 3. Create RAG Chain
                    st.session_state.rag_chain = create_rag_chain(vector_store)
                    
                    st.success("Video processed! You can now ask questions.")
                    st.session_state.messages.append({"role": "assistant", "content": "Video loaded. How can I help you?"})
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a YouTube URL.")

# --- Main chat interface ---
st.header("Chat Window")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question about the video..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if the RAG chain is ready
    if st.session_state.rag_chain:
        with st.spinner("Thinking..."):
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                try:
                    response = st.session_state.rag_chain.invoke(prompt)
                    st.markdown(response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"An error occurred during generation: {e}")
    else:
        st.warning("Please process a video first before asking questions.")