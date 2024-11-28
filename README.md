# CVisionary Chatbot

CVisionary is an RAG-based chatbot utilizing the [Groq API](https://console.groq.com/docs/models) with the Llama-3-8B-Instant model in its free beta version. The model supports up to 8192 tokens request with a context window size of 128k. 

## How to Run
1. Obtain an API key from the [Groq website](https://console.groq.com/docs/models).
2. Add the key to the `.env` file in your project directory.
3. Launch the application using Docker.

## Important Note
As an LLM-powered chatbot, CVisionary may occasionally generate inaccurate or fabricated responses (hallucinations). Please verify critical information independently.

CVisionary does not store or retain any user-provided data. Once the conversation is reset, all history is permanently erased.

If CVisionary provides incorrect answers, restart the conversation and rephrase the question with more detail.

If you have any feedback or suggestions, feel free to reach out!

You can find CVisionary beta version deployed in streamlit cloud via the following link: [CVisionary](https://cvisionary-chatbot.streamlit.app/)

