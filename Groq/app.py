import logging
from huggingface_hub import login
import streamlit as st
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
from streamlit_chat import message as st_message
from chatbot import *
from dotenv import load_dotenv
import os

# Configure global logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__) 

# Initialize Streamlit page
def init_page() -> None:
    """Initializes the Streamlit page configuration."""
    logger.info("Initializing the Streamlit page.")
    st.set_page_config(page_title="CVisionary")
    st.header("CVisionary")
    st.sidebar.title("Options")
    # Add link to Mahnaz Mirhaj's CV
    st.sidebar.markdown("📝[About Me](https://mahnaz-mirhaj.github.io/CV/)", unsafe_allow_html=True)  
    st.sidebar.markdown("📧 [Contact Me](mailto:mahnazmirhaj1997@gmail.com)")
    st.sidebar.markdown("🤖[About CVisionary](https://github.com/Mahnaz-Mirhaj/CVisionary-chatbot)", unsafe_allow_html=True)  

# Clear and initialize messages
def init_messages() -> None:
    """Clears and initializes chat messages."""
    logger.info("Initializing chat messages.")
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    if clear_button or "messages" not in st.session_state:
        logger.info("Resetting messages state.")
        st.session_state.messages = []
        if "agent" in st.session_state and hasattr(st.session_state.agent, "clear_history"):
            logger.info("Clearing chatbot's internal history.")
            st.session_state.agent.clear_history()

# Main function to run the Streamlit app
def main() -> None:
    """
    The main function to run the Streamlit app.
    Handles chatbot initialization, user input, and response generation.
    """
    logger.info("Starting the chatbot application.")

    load_dotenv()

    FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "vector-store/faiss_index")  
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # Initialize the chatbot agent if not already present
    if "agent" not in st.session_state:
        logger.info("Initializing chatbot agent.")
        try:
            st.session_state.agent = LLMRag(
                                    faiss_index_base_path=FAISS_INDEX_PATH,
                                    groq_api_key=GROQ_API_KEY
                                )
        except Exception as e:
            logger.error(f"Failed to initialize the chatbot agent: {e}")
            st.error("Error initializing the chatbot. Please check the logs.")
            
    init_page()
    init_messages()

    # Display conversation history
    messages = st.session_state.get("messages", [])
    logger.info(f"Loaded {len(messages)} messages from session state.")

    for message in messages:
        if isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)

    # Get user input and generate responses
    if user_input := st.chat_input("Input your question!"):
        logger.info(f"Received user input: {user_input}")
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.chat_message("user"):
            st.markdown(user_input)
        try:
            with st.chat_message("assistant"):
                show_answer = st.empty()
                with st.spinner("CVisionary is thinking ..."):
                    answer = st.session_state.agent.generate_rag_response(user_input)
                    logger.info(f"Generated response: {answer}")
                    show_answer.write(answer)
                st.session_state.messages.append(AIMessage(content=answer))
        except Exception as e:
            logger.error(f"Error during response generation: {e}")
            st.error("An error occurred while generating the response. Please try again.")

if __name__ == "__main__":
    logger.info("Application starting.")
    main()
