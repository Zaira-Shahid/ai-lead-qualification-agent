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

## n8n Workflow

`n8n/lead_qualification_workflow.json` implements the orchestration workflow from PROJECT_SPEC.md Section 22:

```
Webhook (POST /webhook/lead-qualified)
  -> Validate Input (Code)
  -> Payload Valid? (If)
       true  -> Branch by Qualification Status (Switch)
                  qualified     -> Save/Confirm Lead -> Notify Team -> Human/Booking Handoff
                  needs_review  -> Save/Confirm Lead -> Notify Human (Needs Review)
                  unqualified   -> Save/Confirm Lead -> Follow-up
       false -> Invalid Payload
```

The backend remains the source of truth for `lead_score` and `qualification_status`: the workflow only validates the incoming payload's shape (required fields present, `qualification_status` is one of the three valid values, `lead_score` is a number 0-100) and routes on the values it receives. It never recalculates the score or re-derives the status.

The "Save/Confirm Lead", "Notify Team", "Notify Human", "Human/Booking Handoff", and "Follow-up" steps are implemented as placeholder `Set`/`No Operation` nodes that produce the action and message content, since PROJECT_SPEC.md does not specify a particular email/CRM/booking provider. Replace these with real integration nodes (e.g. n8n's Email/Slack nodes with your own credentials) for production use — the routing logic and payload validation do not need to change.

### Import and test it

1. Start n8n (`npx n8n start`, or via Docker) and open its editor.
2. From the workflow list, use **Import from file...** and select `n8n/lead_qualification_workflow.json`.
3. Open the **Webhook** node and click **Listen for test event** (or activate the workflow to use its production URL) to get the test webhook URL, e.g. `http://localhost:5678/webhook-test/lead-qualified`.
4. Send a test payload matching the backend's qualification result shape (PROJECT_SPEC.md Section 23), for example:

```bash
curl -X POST http://localhost:5678/webhook-test/lead-qualified \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": 123,
    "name": "Sarah",
    "email": "sarah@example.com",
    "phone": null,
    "service": "Cosmetic Dental Consultation",
    "lead_score": 85,
    "qualification_status": "qualified",
    "requires_human_review": false
  }'
```

5. Change `qualification_status` to `needs_review` or `unqualified` to see the workflow take the other branches, or omit a required field (e.g. `lead_id`) to see it routed to **Invalid Payload**.

This workflow was built and verified against a real local n8n instance (v2.33.7): all three qualification branches and the invalid-payload path were exercised with live webhook calls and confirmed to route and produce output correctly before being committed here.

Once `N8N_WEBHOOK_URL` (see `.env.example`) points at your running n8n instance's webhook URL, the backend can be wired to POST the qualification result there after `/api/qualify` completes — that integration is not yet implemented in the backend as of this phase.
