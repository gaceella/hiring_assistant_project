# AI-Powered Hiring Assistant 🤖

> Automate CV screening, rank candidates by fit score, and generate personalized interview questions — powered by Llama 3 via Groq API.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?style=flat-square&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)
![LLM](https://img.shields.io/badge/LLM-Llama3_via_Groq-purple?style=flat-square)

---

## What it does

HR managers spend hours manually reading CVs. This tool automates the entire screening process:

1. HR enters a job description and required skills
2. Uploads multiple candidate CVs (PDF format)
3. The system parses each CV, scores it against the job (0–100), and ranks all candidates
4. For each candidate, it generates 8 personalized interview questions

**Real-world use case:** Similar tools are actively being built by Pakistani HR-tech companies like Rozee.pk and Talentera.

---

## Demo

![Hiring Assistant Demo](assets/demo.png)

> Step 1: Enter job details → Step 2: Upload CVs → Step 3: View ranked results + interview questions

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Llama 3 (8B) via Groq API |
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| CV Parsing | PyPDF + Groq LLM |
| Database | SQLite |
| Deployment | Docker + Docker Compose |
| Language | Python 3.12 |

---

## System Architecture

```
┌─────────────────┐         HTTP          ┌──────────────────────┐
│  Streamlit UI   │ ◄──────────────────► │   FastAPI Backend     │
│  (port 8501)    │                       │   (port 8000)         │
└─────────────────┘                       └──────────┬───────────┘
                                                      │
                              ┌───────────────────────┼───────────────────┐
                              │                       │                   │
                    ┌─────────▼──────┐   ┌────────────▼──────┐  ┌────────▼───────┐
                    │  Groq API      │   │   SQLite DB        │  │  PDF Parser    │
                    │  (Llama 3)     │   │   (jobs +          │  │  (PyPDF)       │
                    │  CV parsing    │   │    candidates)     │  │                │
                    │  Ranking       │   └───────────────────-┘  └────────────────┘
                    │  Questions     │
                    └────────────────┘
```

---

## Project Structure

```
hiring_assistant/
├── backend/
│   ├── __init__.py
│   ├── main.py                 ← FastAPI routes (5 endpoints)
│   ├── cv_parser.py            ← PDF extraction + LLM structured parsing
│   ├── ranker.py               ← AI candidate scoring and ranking
│   ├── question_generator.py   ← Personalized interview question generation
│   └── db.py                   ← SQLite CRUD operations
├── frontend/
│   └── app.py                  ← Streamlit 3-tab UI
├── data/                       ← SQLite database (auto-created)
├── uploads/                    ← Uploaded CVs (auto-created)
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Docker (optional, for containerized deployment)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/gaceella/hiring-assistant.git
cd hiring-assistant

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Groq API key
export GROQ_API_KEY=gsk_your_key_here
```

### Run locally

```bash
# Terminal 1 — start backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — start frontend
streamlit run frontend/app.py
```

Open your browser at `http://localhost:8501`

### Run with Docker

```bash
# Build and run
docker build -t hiring-assistant .
docker run -p 8000:8000 -e GROQ_API_KEY=gsk_your_key hiring-assistant
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/jobs/create` | Create a new job posting |
| POST | `/jobs/{id}/upload-cvs` | Upload candidate CVs |
| GET | `/jobs/{id}/rank` | Rank all candidates with AI |
| GET | `/jobs/{id}/candidates/{name}/questions` | Generate interview questions |

Full API docs available at `http://localhost:8000/docs` (Swagger UI — auto-generated by FastAPI)

---

## How It Works

### CV Parsing
Each uploaded PDF is read by PyPDF to extract raw text. The text is then sent to Llama 3 via Groq API with a structured prompt asking it to extract name, email, skills, experience, and education as JSON.

### Candidate Ranking
For each candidate, the system sends both the job requirements and the candidate's parsed profile to Llama 3. The model returns a score (0–100), a recommendation (STRONG_YES / YES / MAYBE / NO), matching skills, missing skills, and a 2-3 sentence evaluation.

### Interview Questions
The system generates 8 personalized questions per candidate: 3 technical (based on required skills), 2 behavioral (STAR format), 2 targeted at skill gaps, and 1 Pakistan-specific situational question.

---

## License

MIT License — free to use and modify.
