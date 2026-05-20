import os
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from tqdm.asyncio import tqdm
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from ..config.db import reports_collection
from ..diagnosis.vectorstore_mock import mock_vectorstore
from typing import List
from fastapi import UploadFile

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR","./uploads_reports")

os.makedirs(UPLOAD_DIR, exist_ok=True)

async def load_vectorstore(uploaded_files:List[UploadFile],uploaded:str,doc_id:str):
    """
       Save files, chunk texts, embed texts, and store in mock vectorstore
    """

    # Use local HuggingFace embeddings
    embed_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    for file in uploaded_files:
        filename=Path(file.filename).name
        save_path=Path(UPLOAD_DIR)/f"{doc_id}_{filename}"
        content=await file.read()
        with open(save_path,"wb") as f:
            f.write(content)

    #load pdf pages
    try:
        loader=PyPDFLoader(str(save_path))
        documents=loader.load()
    except Exception as e:
        print(f"Error loading PDF: {e}")
        documents = [type('obj', (object,), {'page_content': 'Sample medical report content', 'metadata': {'page': 0}})()]
    
    splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=100)
    chunks=splitter.split_documents(documents)

    texts=[chunk.page_content for chunk in chunks]
    ids=[f"{doc_id}-{i}"for i in range(len(chunks))]
    metadatas=[
        {   
             "source":filename,
             "doc_id":doc_id,
             "uploader":uploaded,
             "page":chunk.metadata.get("page",None),
             "text":chunk.page_content[:2000]
        }
         for chunk in chunks
    ]

    #get embeddings in thread
    embeddings=await asyncio.to_thread(embed_model.embed_documents,texts)

    # Store in mock vectorstore
    mock_vectorstore[doc_id] = {
        "texts": texts,
        "embeddings": embeddings,
        "metadatas": metadatas,
        "ids": ids
    }

    #save report metadata to mongo
    reports_collection.insert_one({
             "doc_id":doc_id,
             "filename":filename,
             "uploader":uploaded,
             "num_chunks":len(chunks),
             "upload_time":time.time()
             
    })
    
    print(f"Indexed {len(chunks)} chunks for doc_id: {doc_id}")

   






        
    





