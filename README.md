# 🧠 AI Screening Agent — Smart Hiring with Autonomous AI Orchestration

> A modular, agent-based AI system for autonomous candidate screening, feedback collection, and interview scheduling — built as a personal full-stack project using FastAPI, PostgreSQL, pgvector, SentenceTransformers, and React (Chakra UI + Framer Motion).

---

## 📌 Project Overview

This project simulates a fully working **AI-powered hiring assistant** that:

* Parses resumes
* Matches candidates to job descriptions
* Scores them with AI reasoning
* Schedules interviews
* Collects feedback from interviewers
* Performs similarity search across past candidates using embeddings

The backend is built using **FastAPI**, **SQLAlchemy**, **pgvector**, and **SentenceTransformers**, while the frontend (in progress) uses **React**, **Chakra UI**, and **Framer Motion**

---

## 🏗️ Architecture

### 🔹 Backend Stack

* **FastAPI**: REST API with modular agent-based endpoints
* **PostgreSQL** + **pgvector**: Database + vector similarity
* **SQLAlchemy**: ORM + raw queries
* **SentenceTransformers (BGE)**: Embedding resumes & LLM outputs
* **Modular Agents**: Parsing, Matching, Scheduling, Feedback, Orchestrator

### 🔹 Frontend Stack (WIP)

* **React** with **Vite**
* **Chakra UI**: Component system
* **Framer Motion**: Soft animations
* **Glassmorphism UI**: For professional, elegant user experience

---

## 🚀 Features

| Feature                       | Description                                                             |
| ----------------------------- | ----------------------------------------------------------------------- |
| ✅ Resume Parsing              | Extracts key info (skills, availability, enthusiasm score) from text    |
| ✅ Job Matching                | Compares candidate embedding with job metadata                          |
| ✅ Tier Classification         | Scores relevance and classifies into `Strong`, `Optional`, `Drop`       |
| ✅ Scheduling Agent            | Auto-generates mock interview schedule                                  |
| ✅ Feedback Collection         | API to submit and retrieve interviewer feedback                         |
| ✅ Feedback Summary            | Job-wise average rating, decision breakdown, and notes                  |
| ✅ Embedding Similarity Search | Finds top-k similar past candidates using `pgvector` + FAISS            |
| ✅ Modular Agent Design        | Each stage of the pipeline is handled by an agent (clean orchestration) |
| ✅ Developer Debug Endpoints   | Easily inspect internal in-memory DBs                                   |

---

## 📁 Repository Structure

```
ai_screening_agent/
│
├── backend/
│   ├── app/
│   │   ├── agents/              # Modular AI agents (Orchestrator, Matching, Feedback, etc.)
│   │   ├── api/routes/          # FastAPI endpoints
│   │   ├── models/              # Pydantic + ORM models
│   │   ├── core/                # In-memory DBs, orchestrator pipeline
│   │   ├── services/            # PostgreSQL, LLM logging
│   │   └── utils/               # Embeddings, logging, summarization
│
├── frontend/                    # React + Chakra UI (glassmorphism UI in progress)
│
├── scripts/                     # Utility scripts for testing, fake data generation
├── tests/                       # Pytest unit + API tests
├── deployments/                # Docker, startup configs
├── .env
├── requirements.txt
└── README.md
```

---

## 🔧 Setup Instructions

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/ai_screening_agent.git
cd ai_screening_agent
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start PostgreSQL (Local)

Ensure you have PostgreSQL 14+ with `pgvector` extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Create required tables:

```bash
psql -d ai-screening-agent -f migrations/schema.sql
```

### 3. Run Backend

```bash
uvicorn backend.app.api.main:app --reload
```

Test via:

```bash
curl -X POST http://localhost:8000/api/screen \
  -H "Content-Type: application/json" \
  -d '{"job_id": "job123", "resume_text": "Senior backend engineer with AWS experience"}'
```

---

## 📊 API Endpoints

| Route                            | Method   | Description                   |
| -------------------------------- | -------- | ----------------------------- |
| `/api/screen`                    | POST     | Runs full screening pipeline  |
| `/api/screening/similar`         | POST     | Find similar past candidates  |
| `/api/feedback/{candidate_id}`   | POST/GET | Submit or fetch feedback      |
| `/api/feedback/job/{job_id}`     | GET      | Feedback list for a job       |
| `/api/feedback/summary/{job_id}` | GET      | Avg rating + status breakdown |
| `/api/jobs`                      | GET/POST | Create or fetch dummy jobs    |
| `/api/debug/candidates`          | GET      | In-memory candidate store     |

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 💡 Future Roadmap

* [ ] Frontend: Glassmorphism UI with screening funnel
* [ ] LLM reasoning trace + logging panel
* [ ] LLM fallback support (OpenRouter, Ollama)
* [ ] Real PDF resume upload
* [ ] Admin dashboard to manage pipeline


---

## ⭐️ Why This Project?

This project was built from scratch to:

* Demonstrate real-world use of Retrieval-Augmented AI in hiring
* Showcase multi-agent pipeline design + pgvector usage
* Build a scalable, production-grade backend + clean frontend
* Highlight full ownership of architecture, modeling, and deployment

---

## 📜 License

MIT License © 2025 Saurabh Rajput
