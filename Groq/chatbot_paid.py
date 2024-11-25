from groq import Groq
from lingua import Language, LanguageDetectorBuilder
from Groq.prompt import *
import faiss
import numpy as np
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader
from llama_index.core import Settings




class LLMRag:
    def __init__(self, faiss_index_base_path: str, groq_api_key: str, model_name: str = "llama-3.1-8b-instant"):
        """
        Initialize the LLMRag class.
        Args:
            faiss_index_base_path: The base path for FAISS indices (without language suffix).
            groq_api_key: API key for the Groq client.
            model_name: The model name for the Groq client.
        """

        self.client = Groq(api_key=groq_api_key)
        
        # Configuration
        self.model_name = model_name
        self.faiss_index_base_path = faiss_index_base_path  
        self.faiss_index = None  
        self.SYSTEM_PROMPT = ""  
        self.lang = None  
        self.chat_history = []  



    def set_language(self, user_query: str):
        """Set the language of the system prompt and FAISS index based on the user query."""
        languages = [Language.ENGLISH, Language.GERMAN]
        detector = LanguageDetectorBuilder.from_languages(*languages).with_minimum_relative_distance(0.1).build()
        detected_lang = detector.detect_language_of(str(user_query))
        
        if detected_lang:
            self.lang = detected_lang.iso_code_639_1.name.lower()
        else:
            self.lang = "en"  

       

        self.SYSTEM_PROMPT = prompts_lang[self.lang]["SYSTEM_PROMPT"]

       
        lang_suffix = "en" if self.lang == "en" else "de"
        self.faiss_index = faiss.read_index(f"{self.faiss_index_base_path}_{lang_suffix}.index")

       

    def summarize_history(self, num_messages: int = 3, max_tokens: int = 50):
        """Summarize the last num_messages in the history."""
        if len(self.chat_history) < num_messages * 2:  
            num_messages = len(self.chat_history) // 2  
       

        relevant_history = self.chat_history[-(num_messages):]
        
        history_string = "\n".join([f"{msg['role']}: {msg['content']}" for msg in relevant_history])
        print('history string ', history_string)
        summary_prompt = f"Summarize the following conversation into {max_tokens} tokens, keeping only the essential keywords:\n\n{history_string}"

        summary = self.client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": "You are a summarization assistant. Focus on brevity and keywords."
            },
            {
                "role": "user",
                "content": summary_prompt,
            }],
            model=self.model_name,
            temperature=0.7,
            frequency_penalty=1.0,
            max_tokens=max_tokens,
            stop=None,
            stream=False,
        )
        return summary.choices[0].message.content.strip()

    def clear_history(self):
        """Clear the chatbot's conversation history."""
        self.chat_history = [] 


    def retrieve_top_k_documents(self, query: str, k=4, faiss_index=None, max_distance: float = 1.5):
        if faiss_index is None:
            faiss_index = self.faiss_index  
        embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") 
        documents = SimpleDirectoryReader(f"./data/{self.lang}").load_data() 

        query_embedding = embed_model.get_text_embedding(query)
        query_embedding = np.array([query_embedding]).astype(np.float32)

        distances, indices = faiss_index.search(query_embedding, k)
        
        
        filtered_docs = [
            documents[i] for i, distance in zip(indices[0], distances[0]) if distance <= max_distance
        ]
        
        return filtered_docs

    def retrieve_documents(self, user_query: str, k: int = 4):
        """Retrieve top-k documents based on user query."""
        if not self.faiss_index:
            raise ValueError("FAISS index is not loaded. Ensure `set_language` is called first.")
        return self.retrieve_top_k_documents(user_query, k=k)

    def chat(self, user_query: str):
        """Generate a chat completion using the Groq client."""

        messages=[{
                "role": "system",
                "content": self.SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_query,
            }]
        
       
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            temperature=0.9,
            frequency_penalty=1.0,
            max_tokens=1024,
            stop=None,
            stream=False,
        )
        chatbot_response = chat_completion.choices[0].message.content
        self.chat_history.append({"role": "assistant", "content": chatbot_response})
        
        return chatbot_response

    def generate_rag_response(self, user_query: str, k: int = 4):
        """Main function to generate a RAG-based response."""
        
        self.set_language(user_query)
        
        retrieved_docs = self.retrieve_documents(user_query, k=k)
        context = "\n".join([doc.text for doc in retrieved_docs])
        hist = self.summarize_history(num_messages=3, max_tokens=50)
        self.chat_history.append({"role": "user", "content": user_query})

        query_with_context = f"{{'user_query': '{user_query}', 'context': '{context}', 'history': '{hist}'}}"


        return self.chat(query_with_context)
