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
catalogue loading, medicine identification, same-medicine (active ingredient + strength +
dosage form) matching, and price comparison -- including normalized unit pricing (per
tablet/capsule/mL) so different pack sizes can be compared fairly. `data/medicines.csv` is
the source of truth for all medicine facts. RAG/LLM explanation, patient history and pattern
detection are separate layers, not implemented here.

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
  the verified record, same-medicine alternatives and a price comparison. Never guesses:
  unmatched medicines return `NOT_FOUND`, non-unique matches return `AMBIGUOUS` with the
  candidate records (no medicine is guessed).
- `GET /medicine/{medicine_id}` — verified catalogue record for a medicine_id, or 404.
- `GET /alternatives/{medicine_id}` — same-medicine records (same active ingredient,
  strength and dosage form as the given medicine_id -- brand and pack size may differ) and
  a price comparison, or 404.

### Price comparison basis

Alternatives only ever include records with the **same active ingredient, strength and
dosage form** as the matched medicine (a 500mg tablet is never compared against a 250mg
tablet or a syrup). Because pack sizes can still differ, `price_comparison` reports two
independent bases:

- **Pack price** (`lowest_pack_price`, `pack_price_difference`) — the total price for the
  pack as sold, always available whenever a price exists.
- **Unit price** (`lowest_unit_price`, `unit_price_difference`, `comparison_basis`) —
  price normalized per tablet/capsule or per mL, only populated when the pack quantity can
  be reliably parsed from `pack_size` for the items being compared (e.g. `"10's"`,
  `"1 x 10's"`, `"30ml"`). When it can't (e.g. `"Vial"`, `"200 doses"`), `comparison_basis`
  is `"PACK_PRICE_ONLY"` and the unit fields stay `null` rather than guessing a quantity.

Missing prices are always `null`, never `0` or estimated. The backend performs all of this
arithmetic; the LLM layer only explains the already-computed numbers.
