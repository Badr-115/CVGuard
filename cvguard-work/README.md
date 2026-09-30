# CV Guard & Recruit

A production-oriented recruiting workspace for organizations to manage jobs, candidates and resumes, with deterministic, explainable resume-to-job fit signals.

> **Important:** fit scores are matching aids based on submitted resume/job text. They are not a hiring decision and should not be used as the sole basis for employment decisions.

## Stack

- **Frontend:** React 19 + TypeScript + Vite
- **Backend:** FastAPI + SQLAlchemy 2 + Pydantic 2
- **Database:** PostgreSQL 16
- **Authentication:** JWT + Argon2
- **Documents:** PDF/DOCX text extraction
- **Testing:** pytest + API integration tests
- **Deployment:** Docker Compose + Alembic migrations

## Features

- Organization-scoped multi-tenancy
- Registration, login and role-based authorization
- Job creation with required skills
- Candidate creation with optional PDF/DOCX resume upload
- Deterministic skill + context matching with explainable matched/missing skills in the service layer
- Candidate search and fit filtering API
- Database-backed health check
- Security headers and configurable CORS
- Private local resume storage abstraction
- API versioning under `/api/v1`
- Automated backend tests
- Responsive recruiting dashboard

## Project structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/v1/          # HTTP routes
│   │   ├── core/            # settings + security
│   │   ├── services/        # scoring, document handling, AI boundary
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── main.py
│   ├── alembic/             # database migrations
│   └── tests/
├── frontend/src/            # React application
├── docs/architecture.md
├── docker-compose.yml
└── .env.example
```

## Run with Docker

```bash
cp .env.example .env
# Replace JWT_SECRET with a strong random value.
docker compose up --build
```

- Frontend: http://localhost:5173
- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

The backend applies Alembic migrations before starting.

## Run locally

### Backend

Use Python 3.11+ and PostgreSQL:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='postgresql+psycopg://USER:PASSWORD@localhost:5432/cvguard'
export JWT_SECRET='replace-with-a-long-random-secret'
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

If the API is not on `http://localhost:8000/api/v1`, set `VITE_API_URL` before starting Vite.

## Test

```bash
cd backend
pytest -q
```

Tests use an isolated SQLite database and cover health, authentication, jobs, tenant isolation and scoring behavior.

## Production checklist

- Use managed PostgreSQL and private object storage such as S3-compatible storage.
- Set a strong secret through a secret manager; never commit `.env`.
- Serve the frontend and API over HTTPS.
- Configure an explicit production CORS allowlist.
- Add rate limiting and centralized logging/monitoring.
- Put antivirus/malware scanning behind the existing file-service integration boundary before accepting untrusted uploads in production.
- Run `alembic upgrade head` as part of the release process.
- Review candidate scoring with qualified HR/legal stakeholders before using it in a real hiring workflow.

## License

See `LICENSE`.
