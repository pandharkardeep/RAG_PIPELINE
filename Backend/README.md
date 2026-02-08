# RAG Pipeline Backend

A FastAPI backend for RAG-based tweet generation and news analysis.

---
title: RAG Pipeline Backend
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

## Features

- News article retrieval and analysis
- RAG-based tweet generation
- Chart extraction from articles
- Knowledge base management
- Research automation

## API Endpoints

- `/articles` - Fetch and process news articles
- `/tweets` - Generate tweets using RAG
- `/charts` - Extract and generate charts
- `/knowledge-base` - Manage knowledge base
- `/research` - Automated research workflows

## Environment Variables

Set these in your HF Space Settings → Variables and Secrets:

- `PINECONE_API_KEY`
- `PINECONE_INDEX_NAME`
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT`
