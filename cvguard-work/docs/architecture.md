# Architecture

## Request flow

`Browser → /api/v1 → authentication/authorization → services → PostgreSQL / private storage`

## Backend boundaries

- `api/v1`: HTTP transport and request validation.
- `dependencies.py`: authentication and role checks.
- `models.py`: persistence model.
- `services/scoring.py`: deterministic, explainable matching logic.
- `services/files.py`: upload validation, private storage and text extraction.
- `services/ai.py`: integration boundary for an optional external AI provider.
- `core/config.py`: environment configuration.

## Tenant isolation

Organization-owned resources are always queried with the authenticated user's `organization_id`. Job lookup during candidate creation uses the same tenant constraint, preventing cross-organization job references.

## Scoring

The current score is intentionally deterministic: explicit required-skill matches contribute most of the score and relevant job-description vocabulary contributes a bounded context component. Phrase skills such as `Machine Learning` are matched as phrases rather than as unrelated tokens. The API can expose the score as a signal; the application does not represent it as an automatic hiring decision.

## Database lifecycle

Alembic owns production schema changes. The FastAPI lifespan only creates tables when `APP_ENV=test`, keeping production startup from silently mutating the database schema.

## File security

Uploaded resumes are limited by configured size, extension and MIME type, renamed to random UUIDs and stored outside the frontend. PDF/DOCX parsing failures are converted to controlled client errors and partially written files are removed. Malware scanning remains an explicit production integration boundary.
