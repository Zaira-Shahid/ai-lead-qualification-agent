# AI Lead Qualification Agent

An AI-powered lead qualification system for **NovaCare Clinic**. A visitor chats with an AI assistant, which extracts structured lead information (service, contact, urgency, budget, timeline). The backend independently validates that information and deterministically calculates a lead score and qualification status. The result is stored in SQLite and handed to n8n for workflow orchestration (notifications, human handoff, follow-up).

See `PROJECT_SPEC.md` for the full specification this project was built against.

## Problem

A clinic's reception/sales team can't personally screen every inbound lead before deciding whether it's worth a human's time. This project automates the first pass: an AI assistant collects the information a human would ask for anyway, and a deterministic backend engine — not the AI — decides whether the lead is qualified, needs review, or should get a routine follow-up.

## Architecture

```
Lead
  |
Frontend Chat
  |
FastAPI
  |
AI Service (Groq, OpenAI-SDK-compatible)
  |
Structured AI Output
  |
Backend Validation
  |
Deterministic Qualification Engine
  |
SQLite
  |
n8n Webhook
  |
  +-------------+----------------+---------------+
  |             |                |               |
Qualified   Needs Review     Unqualified
  |             |                |
Notification  Human Review    Follow-up
/Handoff      Notification
```

**The core design decision:** the LLM never controls a business action. It only converts natural language into structured data.

```
Natural Language -> LLM -> Structured Information -> Schema Validation
  -> Deterministic Backend Rules -> Final Score + Status -> Automation
```

The AI provides language understanding. The backend provides reliability and business-rule enforcement. This makes the qualification result reproducible, testable, and independent of model behavior/drift.

## MVP Boundary

| Component | Responsible for | Must NOT do |
|---|---|---|
| **Frontend** (`frontend/`) | Chat UI, sending messages, showing replies/loading/errors, displaying the qualification result | Calculate score/status, call the AI provider or n8n directly, hold secrets |
| **FastAPI** (`app/api/`) | Endpoints, request validation, session handling, calling the AI service, validating AI output, running qualification, DB operations, calling n8n, error handling, logging | — |
| **AI service** (`app/services/ai_service.py`) | Understanding intent, extracting structured info, detecting missing fields, generating replies | Save leads, send notifications, call n8n, decide the final score/status, diagnose medical conditions |
| **Qualification service** (`app/services/qualification_service.py`) | Validating criteria, calculating score, determining status and human-review need — deterministically | Depend on the LLM in any way |
| **SQLite** (`app/database/`, `app/models/`) | Storing lead info, qualification result, score, conversation summary, timestamps | — |
| **n8n** (`n8n/lead_qualification_workflow.json`) | Receiving the webhook, validating payload shape, branching by status, triggering notification/handoff/follow-up | Recalculate the score or re-derive the status |

## Features

- AI conversation (Groq-backed, OpenAI-SDK-compatible) that collects service, contact, urgency, budget, and preferred time without re-asking for information already given
- Structured extraction validated against a Pydantic schema, with bounded retry on invalid/unparsable AI output
- Missing-information handling: the chat won't report "ready for qualification" until service, a valid contact, and urgency are present
- Deterministic lead scoring and qualification (`qualified` / `needs_review` / `unqualified`), independent of the AI, with configurable scoring rules and thresholds
- Medical emergency detection with a fixed, backend-controlled safety response
- SQLite storage of leads and qualification results, keyed by chat session
- n8n workflow orchestration: branches by qualification status, with the backend as the sole source of truth for score/status
- Structured logging (`lead_created`, `ai_request_started`, `qualification_completed`, `n8n_webhook_sent`, etc.)
- Error handling throughout: bounded AI retries, timeouts, graceful n8n-unreachable handling, database-failure handling — none of it crashes the user-facing response
- Minimal HTML/CSS/JS chat frontend served by FastAPI

## Tech Stack

```
Python
FastAPI
Groq (OpenAI-SDK-compatible; can switch back to OpenAI, see below)
n8n
SQLite (via SQLAlchemy)
HTML/CSS/JavaScript
Pydantic
pytest
```

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

Open [http://localhost:8000](http://localhost:8000) for the chat UI, or [http://localhost:8000/health](http://localhost:8000/health) to check the API is up.

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

### Backend integration

After `POST /api/qualify` computes and persists the qualification result, the backend automatically calls `N8N_WEBHOOK_URL` (see `.env.example`) with the Section 23 payload shape (`lead_id`, `name`, `email`, `phone`, `service`, `lead_score`, `qualification_status`, `requires_human_review`). This is implemented in `app/services/notification_service.py` and wired into `app/api/qualify.py`.

If n8n is unreachable, times out, or returns a non-2xx response, the failure is logged (`n8n_webhook_failed`) and `/api/qualify` still returns its normal response — a webhook problem never breaks the qualification result the caller sees. This was verified by qualifying a live session with n8n running (confirmed received and executed in n8n's editor) and again with n8n stopped (confirmed the API still returned 200 and the failure was logged).

## Demo

1. Open the chat UI and start typing: *"Hi, I want a cosmetic dental consultation."*
2. The agent asks how soon you'd like it — reply *"Within the next two weeks."*
3. The agent asks about budget — reply *"Around $500."*
4. The agent asks for your name and a way to reach you — provide a name and email.
5. Once service, contact, and urgency are all present, the frontend automatically calls `/api/qualify` and shows the **Qualification Result** panel: score, status, and whether human review is needed.
6. Check `leads.db` (or `GET /api/leads/{id}`) to see the row persisted, and n8n's execution log (if running) to see the webhook received and routed.

Try *"I am having severe chest pain right now"* at any point to see the emergency safety path instead of normal qualification.

## Future Improvements

Out of scope for this MVP, listed here rather than built:

- PostgreSQL in place of SQLite
- Authentication and role-based access control
- Real CRM/email/Slack integration in place of the n8n workflow's placeholder Set/NoOp nodes
- Appointment booking integration
- Retry queues for the n8n webhook call (currently single-attempt, graceful failure only)
- Rate limiting
- Observability/monitoring, prompt/version management, evaluation datasets, automated regression tests
- Multi-tenant architecture
