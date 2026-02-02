import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cohere import CohereRerank
from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_core.prompts import ChatPromptTemplate
from config import Config

class RAGEngine:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.llm = ChatGoogleGenerativeAI(
            model=Config.LLM_MODEL,
            temperature=0,
            convert_system_message_to_human=True
        )

    def _get_reranker_pipeline(self):
        """Sets up the Base Retriever -> Cohere Reranker pipeline."""
        base_retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 10}
        )
        
        compressor = CohereRerank(
            cohere_api_key=Config.COHERE_API_KEY,
            top_n=3, 
            model=Config.RERANKER_MODEL
        )
        
        return ContextualCompressionRetriever(
            base_compressor=compressor, 
            base_retriever=base_retriever
        )

    def query(self, user_query: str):
        """
        Executes the full RAG pipeline: Retrieve -> Rerank -> Generate.
        Returns a dictionary with the answer, source documents, and metrics.
        """
        start_time = time.time()
        
        # 1. Retrieve & Rerank
        retrieval_chain = self._get_reranker_pipeline()
        retrieved_docs = retrieval_chain.invoke(user_query)
        
        if not retrieved_docs:
            return None

        # 2. Format Context
        formatted_context = "\n\n".join(
            f"[{i+1}] {doc.page_content}" 
            for i, doc in enumerate(retrieved_docs)
        )

        # 3. Define Prompt
        template = """
        You are a helpful AI assistant. Answer the question based ONLY on the provided context below.
        
        If the answer is not in the context, strictly say "I cannot answer this based on the provided context."
        
        **Citation Requirement:** - You must cite your sources using the numbers [1], [2], etc.
        - Add citations at the end of sentences where the information is used.
        
        Context:
        {context}
        
        Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)
        
        # 4. Generate Answer
        chain = prompt | self.llm
        response = chain.invoke({"context": formatted_context, "question": user_query})
        
        end_time = time.time()
        
        # 5. Calculate Metrics (Rough Estimation)
        total_chars = len(formatted_context) + len(user_query)
        # Approx 4 chars per token
        est_tokens = total_chars / 4  
        cost = (est_tokens / 1000) * 0.0000185  # Gemini Flash Pricing

        return {
            "answer": response.content,
            "sources": retrieved_docs,
            "metrics": {
                "latency": round(end_time - start_time, 2),
                "cost": f"${cost:.6f}"
            }
        }