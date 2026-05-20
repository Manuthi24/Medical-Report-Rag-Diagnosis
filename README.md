# 🏥 Medical Report Diagnosis Application  
## AI-Powered RAG System for Medical Report Analysis

A full-stack AI-driven healthcare application designed to analyze medical reports and generate AI-assisted preliminary diagnostic insights using **Retrieval-Augmented Generation (RAG)**. The system improves the reliability of AI responses by retrieving relevant medical context before generating explainable and medically grounded insights.

> ⚠️ **Disclaimer:** This application is designed for educational and research purposes only. The generated outputs are AI-assisted preliminary insights and should not be considered as a replacement for professional medical advice, diagnosis, or treatment.

---

## 📌 Project Overview

Medical reports often contain complex clinical terms, lab values, and diagnostic indicators that may be difficult to interpret quickly. This project provides a platform where users can upload medical reports in PDF or text format, extract meaningful content, retrieve relevant medical context, and generate AI-assisted diagnostic explanations using an LLM-powered RAG pipeline.

The system combines **FastAPI**, **Streamlit**, **PostgreSQL**, **Pinecone**, and **LLMs** to create a scalable, modular, and intelligent healthcare analysis platform.

---

## 🎯 Project Objectives

- Enable secure medical report upload and analysis
- Generate AI-assisted preliminary diagnostic insights
- Organize patient medical records and diagnosis history
- Improve LLM response reliability using retrieved medical context
- Build a scalable and modular healthcare AI system
- Provide an interactive dashboard for report analysis and diagnosis review

---

## ✨ Key Features

- 📄 PDF and text-based medical report upload
- 🔍 Automated text extraction and preprocessing
- 🧠 Semantic chunking and vector embedding generation
- 📚 Medical context retrieval using Pinecone vector database
- 🤖 Context-aware diagnosis generation using RAG
- 🩺 Doctor dashboard with diagnosis history
- 🗄️ Persistent storage of users, reports, and diagnosis data
- ⚡ FastAPI backend with asynchronous REST APIs
- 📊 Streamlit frontend for interactive usage and visualization

---

## 🏗️ System Architecture

```text
User / Doctor
     |
     v
Streamlit Frontend
     |
     v
FastAPI Backend
     |
     |----------------------|
     |                      |
     v                      v
PostgreSQL              Pinecone Vector DB
User Data               Medical Context Embeddings
Report Data
Diagnosis History
     |
     v
RAG Pipeline
Text Extraction → Chunking → Embedding → Retrieval → LLM Response
