# CBAM Assistant

Open-source EU CBAM compliance tool for GCC exporters and consultants.

## What it does

GCC exporters (steel, aluminium, cement, fertilizers) can:
- Check if their HS/CN codes fall under CBAM
- Calculate embedded emissions using EU MRR methodology
- Validate shipment data against EU rules
- Generate EU-compliant XML and PDF reports

No consultant required.

## Modules

| Module | Description |
|---|---|
| HS Code Checker | Search CBAM-covered CN codes from Annex I of EU Reg 2023/956 |
| Emission Calculator | EU MRR methodology — BOF, EAF, aluminium, cement, fertilizers |
| Emission Factor Library | IEA + IPCC factors by country and material |
| Supplier Input | Web form + Excel bulk upload |
| Validation Engine | 12 rule-based checks, scored 0–100 |
| Report Generator | XML (CBAM Transitional Registry) + PDF |

## Stack

- Frontend: Next.js 14 + TypeScript + Tailwind CSS
- Backend: FastAPI (Python 3.11+) + SQLAlchemy 2.0
- Database: PostgreSQL (Supabase free tier)
- Auth: Supabase Auth
- PDF: WeasyPrint
- XML: lxml

## Local setup

### Option 1 — Docker (recommended)

```bash
git clone https://github.com/nvaradha22/cbam-assistant
cd cbam-assistant
cp .env.example .env
docker-compose up
```

Frontend: http://localhost:3000
Backend API docs: http://localhost:8000/docs

### Option 2 — Manual

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed  # seed HS codes + emission factors
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Environment variables

See `.env.example` for all required variables.

## Contributing

PRs welcome. Open an issue first for large changes.

## License

MIT

## Regulation reference

EU CBAM Regulation 2023/956: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32023R0956
