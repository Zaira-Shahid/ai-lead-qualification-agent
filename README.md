# AI Lead Qualification Agent

Phase 1: Project setup. FastAPI application with a working `/health` endpoint.

See `PROJECT_SPEC.md` for the full specification. This README will be expanded as later phases are implemented.

## Installation

```bash
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create environment file:

```bash
cp .env.example .env
```

## AI Provider: Groq instead of OpenAI

This project uses **Groq** as the AI provider instead of OpenAI, due to budget constraints (OpenAI's API requires paid credits; Groq offers a free tier).

Groq exposes an **OpenAI-SDK-compatible API**, so no new SDK or AI service code was needed — the existing `openai` Python package is reused, just pointed at Groq's base URL (`https://api.groq.com/openai/v1`) with a Groq API key. The AI service's responsibilities, prompt, and output contract are unchanged.

Provider selection is automatic:

- If `GROQ_API_KEY` is set in `.env`, the AI service calls Groq.
- If `GROQ_API_KEY` is blank/unset, it falls back to calling OpenAI directly with `OPENAI_API_KEY`.

Default model when using Groq: `openai/gpt-oss-120b` (set via `OPENAI_MODEL` in `.env`). Note: the model originally requested for this project, `llama-3.3-70b-versatile`, has since been retired from Groq's catalog; `openai/gpt-oss-120b` was confirmed available via Groq's `/models` endpoint at the time of writing. Run `client.models.list()` against Groq's API to see the current catalog if this changes again.

### Switching back to OpenAI

1. Remove or blank out `GROQ_API_KEY` in `.env`.
2. Set `OPENAI_API_KEY` to a valid OpenAI key.
3. Set `OPENAI_MODEL` to an OpenAI model, e.g. `gpt-4o-mini`.

No code changes are required to switch providers.

## Run

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000/health](http://localhost:8000/health).

## Testing

```bash
pytest
```
