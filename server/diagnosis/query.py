import os
import asyncio
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

embed_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={"device": "cpu"}
)
llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY)

prompt=PromptTemplate.from_template(
    """
You are a medical assistant AI. Analyze the provided medical report context and provide a structured diagnosis.

Format your response EXACTLY as follows:

Probable Diagnosis: [Provide a clear, specific diagnosis based on the findings]

Key Findings from the Report:
• [Finding 1]
• [Finding 2]
• [Finding 3]
• [Additional findings as needed]

Recommended Next Steps (Suggestions, not Medical Advice):

Suggestions:
• [Recommendation 1]
• [Recommendation 2]
• [Recommendation 3]
• [Additional recommendations as needed]

Context from Medical Report:
{context}

Patient Question: {question}

Provide a thorough, professional medical analysis.
    """
)

rag_chain = prompt | llm

async def diagnosis_report(user: str, doc_id: str, question: str):
    # Import mock vectorstore
    from .vectorstore_mock import mock_vectorstore
    
    # Check if doc_id is in mock vectorstore
    if doc_id not in mock_vectorstore:
        return {"diagnosis": None, "explanation": "No report content indexed for this doc_id"}
    
    # Get data from mock vectorstore
    data = mock_vectorstore[doc_id]
    contexts = data.get("texts", [])
    sources_set = set()
    
    # Extract sources from metadata
    for meta in data.get("metadatas", []):
        if meta.get("source"):
            sources_set.add(meta.get("source"))
    
    if not contexts:
        return {"diagnosis": None, "explanation": "No report content indexed for this doc_id"}
    
    # limit context size
    context_text = "\n\n".join(contexts[:5])

    # final call the rag chain
    try:
        final = await asyncio.to_thread(rag_chain.invoke, {"context": context_text, "question": question})
        return {"diagnosis": final.content, "sources": list(sources_set)}
    except Exception as e:
        print(f"LLM Error: {e}")
        # Return a fallback diagnosis if LLM fails
        return {
            "diagnosis": f"Based on the medical report analysis:\n\n**Preliminary Findings:**\n- Report has been successfully indexed and analyzed\n- {len(contexts)} relevant sections were found\n\n**Note:** AI diagnosis service is currently unavailable. Please consult with your healthcare provider for accurate diagnosis.\n\n**Report Summary:**\n{context_text[:500]}...",
            "sources": list(sources_set)
        }


    