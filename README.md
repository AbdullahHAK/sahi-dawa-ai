# Sahi Dawa: AI Prescription Transparency & Care Assistant

**Pak Angels GenAI Hackathon (Cohort 11 - Health Care Category)**

## 🚀 The Vision
Patients often lack clarity regarding their prescribed medications—wondering if they fit their diagnosis, if cheaper generic equivalents exist, or if they are experiencing irrational, repetitive antibiotic prescribing. **Sahi Dawa** brings immediate transparency and cost awareness to patients, enabling them to consult confidently with qualified medical professionals. 

*Disclaimer: Sahi Dawa is an educational transparency tool. It does not replace doctor consultations, prescribe, or substitute medication autonomously.*

## 🛠️ MVP Feature Set
- **Prescription Analysis:** Inputs for diagnosis, medicine name, and dosage.
- **RAG-Powered Explanations:** Medicine definitions anchored safely to a curated, DRAP-referenced data catalogue (~30-50 verified records) to prevent AI hallucinations.
- **Cost Transparency:** Brand-vs-generic pricing comparisons to surface affordable local alternatives.
- **Agentic Memory & Pattern Detection:** Analyzes visit history across sequential encounters to flag risks like antimicrobial resistance from repeated antibiotic use.
- **Shareable Summary:** Generates a structured Patient Health Summary report.

## 👥 Hackathon Team Members
- **Abdullah Aamir** (Lead)
- **Abdullah**
- **Faraz Ahmed Memon**
- **Esha Inam**
- **Absar Ahmed**
- **Afra Naz**

## 🧱 Backend (deterministic catalogue layer)

The `backend/` service implements the deterministic, non-AI part of the pipeline: CSV
catalogue loading, medicine identification, same-active-ingredient matching, and price
comparison. `data/medicines.csv` is the source of truth for all medicine facts. RAG/LLM
explanation, patient history and pattern detection are separate layers, not implemented here.

### Setup

```bash
cd backend
pip install -r requirements.txt
```

### Run the API

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Interactive docs at `http://127.0.0.1:8000/docs`.

### Run the tests

```bash
cd backend
pytest
```

### Endpoints

- `POST /prescription` — identify a medicine (name + optional dosage), and if found, return
  the verified record, same-active-ingredient alternatives and a price comparison. Never
  guesses: unmatched medicines return `NOT_FOUND`, non-unique matches return `AMBIGUOUS`
  with the candidate records (no medicine is guessed).
- `GET /medicine/{medicine_id}` — verified catalogue record for a medicine_id, or 404.
- `GET /alternatives/{medicine_id}` — same-active-ingredient records and price comparison
  for a medicine_id, or 404.
