# AI Lead Qualification Agent
## Technical Project Specification & Implementation Guide

**Project Type:** AI Automation MVP  
**Use Case:** Service Business / Clinic  
**Primary Goal:** Automatically engage inbound leads, collect qualification information, score the lead using deterministic backend rules, store the result, and route qualified or review-required leads to a human/booking workflow.

---

# 1. Project Objective

Build a simple but production-minded **AI Lead Qualification Agent** for a fictional clinic.

The system should:

- Receive a new lead.
- Start a natural-language conversation.
- Understand the requested service.
- Ask relevant qualification questions.
- Extract structured lead information.
- Validate extracted information.
- Calculate a deterministic lead score.
- Assign a qualification status.
- Store the lead and qualification result.
- Trigger n8n automation.
- Notify a human team member when appropriate.
- Handle missing information.
- Handle invalid AI output.
- Handle API failures and timeouts.
- Support human handoff.
- Provide a small working demo.

The project is intentionally an **evaluation-level MVP**, not a complete clinic management platform.

The reviewer should be able to see clear evidence of:

- AI agent design
- LLM integration
- Structured extraction
- Backend validation
- Deterministic business logic
- API design
- Database design
- Automation
- Error handling
- Human-in-the-loop workflows
- Separation of concerns

---

# 2. Reviewer-Facing One-Page Summary

## What was built?

An AI-powered lead qualification system for **NovaCare Clinic**.

A visitor can chat with the AI assistant and provide information such as:

- Name
- Email/phone
- Requested service
- Timeline/urgency
- Budget
- Preferred appointment time

The AI converts the conversation into structured information.

The backend then validates that information and independently calculates the lead score.

The final result is stored in SQLite and passed to n8n for workflow orchestration.

## Core Architecture

```text
Lead
  ↓
Frontend Chat
  ↓
FastAPI
  ↓
AI Service
  ↓
Structured AI Output
  ↓
Backend Validation
  ↓
Deterministic Qualification Engine
  ↓
SQLite
  ↓
n8n Webhook
  ↓
┌──────────────┬───────────────┬──────────────┐
│  Qualified   │ Needs Review  │ Unqualified  │
│      ↓       │       ↓       │      ↓       │
│ Notification │ Human Review  │ Follow-up    │
│ / Handoff    │ Notification  │              │
└──────────────┴───────────────┴──────────────┘
```

## Important Engineering Decision

The LLM does **not** control important business actions.

The architecture is:

```text
Natural Language
      ↓
      LLM
      ↓
Structured Information
      ↓
Schema Validation
      ↓
Deterministic Backend Rules
      ↓
Final Score + Status
      ↓
Automation
```

The AI provides language understanding.

The backend provides reliability and business-rule enforcement.

## MVP Technologies

- Python
- FastAPI
- OpenAI API
- SQLite
- n8n
- HTML/CSS/JavaScript
- Pydantic
- pytest

## Main Demonstration

The reviewer should be able to:

1. Open the application.
2. Start a conversation.
3. Provide lead information.
4. See information extracted.
5. See deterministic qualification.
6. See score and status.
7. Verify database storage.
8. Trigger n8n.
9. See the appropriate notification/handoff.

---

# 3. Example Business

Use the fictional business:

**NovaCare Clinic**

Example services:

- General Consultation
- Dental Consultation
- Cosmetic Consultation
- Physiotherapy
- Skin Consultation

The AI qualifies potential customers before routing them to the clinic's reception/sales team.

---

# 4. High-Level Architecture

```text
                    ┌───────────────────┐
                    │       Lead        │
                    │    Web Chat       │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │     FastAPI       │
                    │      Backend      │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │    AI Service     │
                    │                   │
                    │ Intent Detection  │
                    │ Information       │
                    │ Extraction        │
                    │ Conversation      │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Schema Validation │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Qualification     │
                    │ Engine             │
                    │                   │
                    │ Validate data     │
                    │ Calculate score   │
                    │ Determine status  │
                    └─────────┬─────────┘
                              │
                 ┌────────────┼────────────┐
                 │            │            │
                 ▼            ▼            ▼
            Qualified     Needs Review  Unqualified
                 │            │            │
                 └────────────┼────────────┘
                              ▼
                    ┌───────────────────┐
                    │      SQLite       │
                    │   Lead Storage    │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │       n8n         │
                    │   Orchestration   │
                    └─────────┬─────────┘
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
             Notify Team   Human Review  Follow-up
```

---

# 5. Exact MVP Integration Boundary

This boundary must remain clear throughout development.

## Frontend Responsibility

The frontend is responsible only for:

- Chat UI
- Sending messages
- Displaying AI replies
- Showing loading state
- Showing errors
- Showing final qualification result

The frontend must NOT:

- Calculate lead score.
- Decide qualification status.
- Call OpenAI directly.
- Call n8n directly.
- Contain API keys.
- Implement business rules.

---

## FastAPI Responsibility

FastAPI is the main application/backend layer.

It is responsible for:

- API endpoints
- Request validation
- Session/conversation handling
- Calling AI service
- Validating AI output
- Running qualification logic
- Database operations
- Calling n8n
- Error handling
- Logging

---

## AI Service Responsibility

The AI service is responsible for:

- Understanding natural language.
- Detecting intent.
- Extracting lead information.
- Identifying missing information.
- Generating conversational replies.

The AI service must NOT:

- Save leads directly.
- Send notifications directly.
- Call n8n directly.
- Decide whether an external action should happen.
- Override backend business rules.
- Diagnose medical conditions.

---

## Qualification Service Responsibility

The qualification service is deterministic.

It is responsible for:

- Validating qualification criteria.
- Calculating score.
- Determining qualification status.
- Determining whether human review is required.

The qualification service must NOT depend on an LLM.

---

## Database Responsibility

SQLite stores:

- Lead information
- Qualification result
- Score
- Conversation summary
- Timestamps

Database access should remain isolated so SQLite can later be replaced with PostgreSQL.

---

## n8n Responsibility

n8n is responsible for orchestration after the backend produces a final qualification result.

n8n can:

- Receive webhook.
- Validate payload.
- Branch by qualification status.
- Trigger notification.
- Trigger human handoff.
- Trigger follow-up workflow.

n8n should NOT independently recalculate the lead score.

The authoritative score is generated by the backend qualification service.

---

# 6. Recommended Technology Stack

## Backend

Python + FastAPI

Reasons:

- Lightweight
- Easy API development
- Good AI integration support
- Strong validation with Pydantic
- Easy to demonstrate
- Clear separation of concerns

## AI

OpenAI API.

The exact model must be configurable.

Example:

```env
OPENAI_MODEL=gpt-4o-mini
```

Do not hard-code the model throughout the application.

## Database

SQLite.

Architecture must allow future migration to PostgreSQL.

## Automation

n8n.

## Frontend

Simple HTML/CSS/JavaScript.

Do not introduce React/Next.js unless there is a concrete reason.

---

# 7. Lead Data Model

Create a `Lead` model containing:

```text
id
name
email
phone
service
urgency
budget
preferred_time
location
booking_intent
service_matches_clinic
budget_is_suitable
timeline_is_suitable
qualification_status
lead_score
conversation_summary
created_at
updated_at
```

Possible qualification statuses:

```text
qualified
needs_review
unqualified
```

---

# 8. Qualification Scoring

## Critical Rule

The **AI must never be treated as the authoritative source for the lead score**.

The AI may provide evidence/features such as:

```json
{
  "booking_intent": true,
  "service_matches_clinic": true,
  "budget_is_suitable": true,
  "timeline_is_suitable": true
}
```

The backend qualification service calculates the final score.

---

# 9. Deterministic Scoring Rules

Default scoring:

| Criterion | Score |
|---|---:|
| Valid contact information | +10 |
| Clear service requirement | +20 |
| Service matches clinic offering | +20 |
| Strong intent to book | +20 |
| Suitable budget | +15 |
| Suitable timeline | +15 |
| **Maximum** | **100** |

Classification:

```text
80–100 → qualified
50–79  → needs_review
0–49   → unqualified
```

These values must be configurable.

Recommended configuration:

```python
SCORING_RULES = {
    "valid_contact": 10,
    "clear_service": 20,
    "service_match": 20,
    "booking_intent": 20,
    "suitable_budget": 15,
    "suitable_timeline": 15,
}
```

Thresholds should also be configurable:

```python
QUALIFIED_THRESHOLD = 80
REVIEW_THRESHOLD = 50
```

---

# 10. Missing Information Rule

A lead should not be considered fully qualified if required information is missing.

Required minimum information:

- Service
- Valid email OR valid phone
- Urgency/timeline

Budget and preferred time may be optional depending on the service/business rules.

If required information is missing:

```text
Do not finalize qualification.

Ask a follow-up question.
```

Example:

```json
{
  "missing_fields": [
    "phone",
    "urgency"
  ]
}
```

---

# 11. Emergency Safety Rule

The AI is NOT a medical diagnosis or treatment system.

It must not:

- Diagnose conditions.
- Prescribe medication.
- Recommend medical treatment.
- Make emergency medical decisions.
- Attempt normal lead qualification during an apparent emergency.

If a user indicates an emergency, the conversation should switch to a safety response recommending immediate appropriate emergency assistance or contacting the clinic.

Example:

```text
I'm sorry you're experiencing this. This assistant cannot handle medical emergencies. Please contact your local emergency service or seek immediate medical attention.
```

The system should record the conversation outcome appropriately without pretending to provide medical advice.

---

# 12. Conversation Flow

Example:

### Agent

Hi! Welcome to NovaCare Clinic.

I can help you find the right service and get your consultation request started.

What type of service are you interested in?

### Lead

I want a dental consultation.

### Agent

Sure. Are you looking for a general dental consultation, cosmetic treatment, or something else?

### Lead

Cosmetic treatment.

### Agent

Got it. How soon would you ideally like to have your consultation?

### Lead

Within the next two weeks.

### Agent

Thanks. Do you have an approximate budget range in mind?

### Lead

Around $500.

### Agent

Great. What is your preferred name and the best email or phone number to reach you?

---

# 13. AI Responsibilities

The AI should perform:

## Intent Detection

Determine what service the lead is interested in.

## Information Extraction

Extract:

```json
{
  "name": "",
  "email": "",
  "phone": "",
  "service": "",
  "urgency": "",
  "budget": null,
  "preferred_time": ""
}
```

## Missing Information Detection

Example:

```json
{
  "missing_fields": [
    "budget",
    "phone"
  ]
}
```

## Conversation Management

The AI should:

- Ask one or a small number of relevant questions.
- Avoid repeating questions.
- Use information already provided.
- Keep responses concise.
- Never invent information.

---

# 14. AI Output Contract

The LLM should return structured data.

Example:

```json
{
  "intent": "dental_cosmetic_consultation",
  "lead": {
    "name": "Sarah",
    "email": "sarah@example.com",
    "phone": null,
    "service": "Cosmetic Dental Consultation",
    "urgency": "within_2_weeks",
    "budget": 500,
    "preferred_time": "afternoon"
  },
  "missing_fields": [],
  "booking_intent": true,
  "service_matches_clinic": true,
  "budget_is_suitable": true,
  "timeline_is_suitable": true,
  "conversation_summary": "Lead is interested in cosmetic dental consultation within two weeks with an approximate $500 budget."
}
```

The backend then calculates:

```text
lead_score
qualification_status
requires_human_review
```

The LLM must NOT be authoritative for these final values.

---

# 15. AI Output Validation

Never trust raw LLM output.

Required flow:

```text
LLM Response
     ↓
Parse JSON
     ↓
Pydantic Validation
     ↓
Semantic Validation
     ↓
Qualification Service
     ↓
Database
     ↓
Automation
```

If invalid:

```text
AI Response
     ↓
Validation Failed
     ↓
Retry
     ↓
Still Invalid?
     ↓
Safe Fallback / Human Review
```

The application must never execute important business actions based on unvalidated raw AI output.

---

# 16. AI System Prompt

Create:

```text
prompts/lead_agent_prompt.txt
```

Use the following as the base system prompt:

```text
You are an AI lead qualification assistant for NovaCare Clinic.

Your responsibilities are:

1. Understand what service the user is interested in.
2. Collect required lead information.
3. Ask only relevant questions.
4. Do not ask for information that has already been provided.
5. Keep responses concise and natural.
6. Never diagnose medical conditions.
7. Never provide medical treatment recommendations.
8. If the user indicates a medical emergency, recommend immediate appropriate emergency assistance.
9. Extract structured information from the conversation.
10. Never invent missing information.
11. Clearly distinguish between information provided by the user and information that is unknown.
12. Do not directly perform external business actions.

Available clinic services:

- General Consultation
- Dental Consultation
- Cosmetic Consultation
- Physiotherapy
- Skin Consultation

Required information:

- name
- email or phone
- requested service
- urgency/timeline

Additional information when relevant:

- budget
- preferred appointment time
- location

Ask natural follow-up questions when required information is missing.

The AI provides language understanding and structured extraction only.

Final lead scoring and qualification are controlled by deterministic backend business logic.

Never call external services directly.
Never save records directly.
Never send notifications directly.
```

---

# 17. Backend API

Implement these endpoints.

## POST `/api/leads`

Create a new lead.

Request:

```json
{
  "name": "Sarah",
  "email": "sarah@example.com",
  "phone": "+123456789"
}
```

Response should return the created lead ID and basic information.

---

## POST `/api/chat`

Send a message to the AI agent.

Request:

```json
{
  "session_id": "abc123",
  "message": "I need a dental consultation"
}
```

Response:

```json
{
  "reply": "Sure. What type of dental consultation are you looking for?",
  "session_id": "abc123",
  "status": "collecting_information"
}
```

Possible statuses:

```text
collecting_information
ready_for_qualification
emergency
error
```

---

## POST `/api/qualify`

Run qualification.

Request:

```json
{
  "session_id": "abc123"
}
```

Response:

```json
{
  "lead_score": 85,
  "qualification_status": "qualified",
  "requires_human_review": false
}
```

The score must be calculated by the backend qualification service.

---

## GET `/api/leads/{lead_id}`

Return lead details.

---

## GET `/health`

Return:

```json
{
  "status": "ok"
}
```

---

# 18. Project Structure

Create:

```text
ai-lead-agent/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── leads.py
│   │   ├── chat.py
│   │   └── health.py
│   │
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── qualification_service.py
│   │   ├── notification_service.py
│   │   └── lead_service.py
│   │
│   ├── models/
│   │   └── lead.py
│   │
│   ├── schemas/
│   │   ├── lead.py
│   │   └── ai_response.py
│   │
│   ├── database/
│   │   └── database.py
│   │
│   └── config.py
│
├── n8n/
│   └── lead_qualification_workflow.json
│
├── prompts/
│   └── lead_agent_prompt.txt
│
├── tests/
│   ├── test_health.py
│   ├── test_qualification.py
│   └── test_leads.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── PROJECT_SPEC.md
```

---

# 19. Environment Variables

Create:

```text
.env.example
```

Content:

```env
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini

DATABASE_URL=sqlite:///./leads.db

N8N_WEBHOOK_URL=http://localhost:5678/webhook/lead-qualified

NOTIFICATION_EMAIL=team@example.com
```

Never commit:

```text
.env
```

to GitHub.

---

# 20. Qualification Service

Create:

```text
app/services/qualification_service.py
```

Responsibilities:

- Validate lead data.
- Calculate score.
- Determine status.
- Determine human review requirement.

Example:

```python
def calculate_lead_score(lead):
    score = 0

    if lead.email or lead.phone:
        score += SCORING_RULES["valid_contact"]

    if lead.service:
        score += SCORING_RULES["clear_service"]

    if lead.service_matches_clinic:
        score += SCORING_RULES["service_match"]

    if lead.booking_intent:
        score += SCORING_RULES["booking_intent"]

    if lead.budget_is_suitable:
        score += SCORING_RULES["suitable_budget"]

    if lead.timeline_is_suitable:
        score += SCORING_RULES["suitable_timeline"]

    return score
```

Then:

```python
if score >= QUALIFIED_THRESHOLD:
    status = "qualified"
elif score >= REVIEW_THRESHOLD:
    status = "needs_review"
else:
    status = "unqualified"
```

The implementation should prevent impossible scores above 100.

---

# 21. Qualification Consistency Rules

The following rules are mandatory.

### Rule 1

AI score is ignored as the authoritative score.

### Rule 2

Backend recalculates the score from validated fields.

### Rule 3

n8n uses the backend's final score/status.

### Rule 4

n8n does not recalculate the score.

### Rule 5

Frontend only displays the result returned by the backend.

### Rule 6

A missing required field prevents final qualification.

### Rule 7

Invalid contact information must not receive the valid-contact points.

### Rule 8

Unsupported services must not receive service-match points.

---

# 22. n8n Workflow

Create:

```text
n8n/lead_qualification_workflow.json
```

Workflow:

```text
Webhook
   ↓
Validate Input
   ↓
Receive Backend Qualification Result
   ↓
Switch Qualification Status
   │
   ├── qualified
   │      ↓
   │   Save/Confirm Lead
   │      ↓
   │   Notify Team
   │      ↓
   │   Human / Booking Handoff
   │
   ├── needs_review
   │      ↓
   │   Save/Confirm Lead
   │      ↓
   │   Notify Human
   │
   └── unqualified
          ↓
       Save/Confirm Lead
          ↓
       Follow-up
```

### Important Boundary

The backend remains the source of truth for:

```text
lead_score
qualification_status
```

n8n only orchestrates actions based on these values.

---

# 23. n8n Payload

Recommended webhook payload:

```json
{
  "lead_id": 123,
  "name": "Sarah",
  "email": "sarah@example.com",
  "phone": null,
  "service": "Cosmetic Dental Consultation",
  "lead_score": 85,
  "qualification_status": "qualified",
  "requires_human_review": false
}
```

---

# 24. Human Handoff

For example:

```text
Lead Score: 65
Status: needs_review
```

n8n should notify the team.

Example notification:

```text
New lead requires review.

Name: Sarah
Service: Cosmetic Dental Consultation
Score: 65

Please review before contacting the lead.
```

The system should clearly demonstrate human-in-the-loop automation.

---

# 25. Error Handling

The workflow must not fail silently.

Handle:

- AI failures
- API failures
- Database failures
- Invalid AI JSON
- Missing information
- n8n webhook failures
- Timeouts
- Notification failures

---

# 26. AI Failure Handling

Recommended pattern:

```text
AI Request
    ↓
Timeout?
    ↓
Retry
    ↓
Success?
 ┌──┴──┐
YES    NO
 │      │
 ▼      ▼
Continue
       ↓
Safe fallback
       ↓
Human review / error response
```

Use bounded retries.

Do not create infinite retry loops.

---

# 27. API Failure Handling

Implement:

- Request validation
- Timeouts
- Controlled retries where appropriate
- Structured error responses
- Logging
- Safe fallback behavior

---

# 28. Invalid AI Output

If the model returns invalid structured data:

```text
AI Response
     ↓
Parse
     ↓
Validation
     ↓
Invalid
     ↓
Retry with correction
     ↓
Still invalid
     ↓
Safe fallback
```

Never save unvalidated AI data as an authoritative qualification result.

---

# 29. Missing Information

If required information is missing:

```text
User Message
     ↓
AI Extraction
     ↓
Missing Fields
     ↓
Follow-up Question
     ↓
User Response
     ↓
Update Session
```

Do not qualify until required information is available.

---

# 30. Frontend Demo

Create a very simple chat interface.

Requirements:

- Clean interface
- Chat messages
- User messages
- AI messages
- Input box
- Send button
- Loading indicator
- Error state
- Qualification result

Example:

```text
┌─────────────────────────────────────┐
│        NovaCare AI Assistant        │
├─────────────────────────────────────┤
│                                     │
│ AI: Hi! How can I help you today?  │
│                                     │
│ You: I need dental treatment        │
│                                     │
│ AI: What type of treatment are      │
│     you interested in?              │
│                                     │
├─────────────────────────────────────┤
│ Type your message...       [Send]   │
└─────────────────────────────────────┘
```

Do not spend excessive time on UI.

The technical workflow is more important.

---

# 31. Demo Scenario

Use one complete scenario.

### Step 1

User:

```text
Hi, I want a cosmetic dental consultation.
```

### Step 2

Agent asks:

```text
How soon would you like the consultation?
```

### Step 3

User:

```text
Within the next two weeks.
```

### Step 4

Agent asks:

```text
What budget range are you considering?
```

### Step 5

User:

```text
Around $500.
```

### Step 6

Agent asks for contact details.

### Step 7

System extracts:

```json
{
  "service": "Cosmetic Dental Consultation",
  "urgency": "within_2_weeks",
  "budget": 500
}
```

### Step 8

Backend qualification engine calculates:

```text
Lead Score: 85
Status: Qualified
```

### Step 9

n8n receives the result.

### Step 10

Lead is stored.

### Step 11

Notification is sent to the clinic team.

---

# 32. Test Cases

Create automated tests.

## Test 1 — Qualified Lead

Input:

```text
I want a cosmetic dental consultation.
I want it within two weeks.
My budget is around $500.
My email is test@example.com.
```

Expected:

```text
qualified
```

The exact score must come from the deterministic scoring rules.

---

## Test 2 — Missing Information

Input:

```text
I want dental treatment.
```

Expected:

```text
Agent asks follow-up questions.
```

---

## Test 3 — Invalid Email

Input:

```text
my email is hello
```

Expected:

```text
Agent asks for a valid email or phone.
```

---

## Test 4 — Unsupported Service

Input:

```text
I need a service that the clinic doesn't offer.
```

Expected:

```text
unqualified
```

or a clearly defined human-review path if business rules require it.

The behavior must be deterministic and tested.

---

## Test 5 — Emergency

Input:

```text
I am having severe chest pain right now.
```

Expected:

```text
Do not continue normal qualification.

Provide emergency-oriented safety guidance.
```

---

# 33. Logging

Add structured logs.

Examples:

```text
INFO lead_created
INFO ai_request_started
INFO ai_response_received
INFO qualification_started
INFO qualification_completed
INFO n8n_webhook_sent
ERROR ai_request_failed
ERROR ai_response_invalid
ERROR database_operation_failed
```

Do not unnecessarily log:

- Full conversations
- Personal information
- API keys
- Sensitive data

---

# 34. Security

Implement basic security practices:

- Environment variables for secrets.
- `.gitignore`.
- Request validation.
- Input sanitization where appropriate.
- API timeout.
- Bounded retries.
- No secrets in source code.
- No unnecessary personal data in logs.
- Basic rate limiting if practical.

Do not over-engineer authentication for the MVP.

---

# 35. README Requirements

The final README must contain:

## Project Overview

Explain what the agent does.

## Problem

Explain the business problem.

## Architecture

Include the architecture diagram.

## MVP Boundary

Explain responsibilities of:

- Frontend
- FastAPI
- AI
- Qualification service
- SQLite
- n8n

## Features

List:

- AI conversation
- Structured extraction
- Missing information handling
- Deterministic lead scoring
- Qualification
- Database storage
- n8n automation
- Human handoff
- Error handling

## Tech Stack

```text
Python
FastAPI
OpenAI
n8n
SQLite
HTML/CSS/JavaScript
Pydantic
pytest
```

## Installation

```bash
git clone <repository>
cd ai-lead-agent

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

Install:

```bash
pip install -r requirements.txt
```

Create environment file:

```bash
cp .env.example .env
```

On Windows, manually copy `.env.example` to `.env` if necessary.

Add API credentials.

Run:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000
```

## Testing

```bash
pytest
```

## n8n Setup

Explain:

- Import workflow JSON.
- Configure webhook.
- Configure notification.
- Start workflow.
- Test webhook.

## Demo

Explain the demo scenario.

## Future Improvements

List production improvements.

---

# 36. Demo Video

Target:

**3–5 minutes**

Do not make a long presentation.

## 0:00–0:30

Explain the problem:

> I built a simple AI lead qualification agent for a clinic. The goal is to automatically collect lead information, qualify the lead using deterministic business rules, and route the result to the clinic team.

## 0:30–1:30

Show the chat.

Demonstrate the conversation.

## 1:30–2:15

Show qualification result.

Explain:

- Extracted information
- Score
- Status
- Reason

## 2:15–3:15

Show n8n.

Explain:

```text
Webhook
→ validation
→ workflow branch
→ notification
```

## 3:15–4:00

Show code structure.

Explain separation between:

```text
AI
Business Logic
Database
API
Automation
```

## 4:00–5:00

Explain the main technical decision:

> The main design decision was not allowing the LLM to directly perform important business actions. The AI handles natural-language understanding and structured extraction, while deterministic backend logic validates the information and controls the actual workflow.

---

# 37. Important Technical Talking Points

During technical review, emphasize:

## AI is not the business logic

The LLM interprets conversation.

The backend makes business decisions.

## Structured Outputs

Use structured JSON rather than relying on free-form responses.

## Validation

Validate AI output before using it.

## Deterministic Scoring

The final lead score is calculated by backend rules.

## Human-in-the-Loop

Ambiguous or review-required leads can be routed to humans.

## Error Handling

External APIs can fail.

Therefore:

- Retries
- Timeouts
- Validation
- Fallbacks
- Logging

are necessary.

## Separation of Concerns

Keep:

```text
AI Service
Qualification Service
Lead Service
Database
API
Automation
```

separate.

---

# 38. MVP Scope

## MUST HAVE

```text
Chat
+
AI
+
Information Extraction
+
Missing Information Handling
+
Qualification
+
Deterministic Lead Score
+
SQLite Database
+
n8n Workflow
+
Notification
+
Human Handoff
+
Basic Frontend
+
Tests
+
Error Handling
```

## DO NOT BUILD

Do not spend time building:

- Authentication
- Complex dashboards
- Payment systems
- Advanced analytics
- Production deployment infrastructure
- Complex CRM
- Mobile app
- Multi-tenant SaaS
- Advanced appointment scheduling
- WhatsApp integration
- Voice agent

These are outside MVP scope.

The evaluation focuses on engineering thinking and working functionality.

---

# 39. Suggested Implementation Order

Follow these phases exactly.

---

## Phase 1 — Project Setup

Tasks:

- Create project folder.
- Create Python virtual environment.
- Install dependencies.
- Create `.env`.
- Create folder structure.
- Create FastAPI application.
- Implement `/health`.

Acceptance criteria:

```text
Application starts.
/
health endpoint works.
```

---

## Phase 2 — Database

Tasks:

- Create SQLite database.
- Create Lead model.
- Create database connection.
- Implement create/read lead operations.

Acceptance criteria:

```text
Lead can be created.
Lead can be retrieved.
Database persists data.
```

---

## Phase 3 — AI

Tasks:

- Create OpenAI service.
- Create system prompt.
- Implement conversation handling.
- Implement structured output.
- Add Pydantic validation.
- Handle invalid AI responses.

Acceptance criteria:

```text
AI conversation works.
Structured extraction works.
Invalid AI output is handled safely.
```

---

## Phase 4 — Qualification

Tasks:

- Implement deterministic scoring.
- Implement qualification status.
- Implement missing-information logic.
- Implement human-review condition.
- Add unit tests.

Acceptance criteria:

```text
Scores are calculated by backend.
Status is deterministic.
Tests pass.
```

---

## Phase 5 — Frontend

Tasks:

- Create simple chat UI.
- Connect to `/api/chat`.
- Display responses.
- Display loading/error states.
- Display final qualification result.

Acceptance criteria:

```text
Reviewer can use the application through browser.
```

---

## Phase 6 — n8n

Tasks:

- Create webhook.
- Validate payload.
- Receive backend qualification result.
- Branch by status.
- Trigger notification.
- Trigger human handoff.
- Export workflow JSON.

Acceptance criteria:

```text
Backend → n8n works.
Qualified route works.
Needs-review route works.
Unqualified route works.
```

---

## Phase 7 — Error Handling

Review the complete application.

Implement:

- Timeouts
- Bounded retries
- Validation
- Logging
- Safe fallbacks

Acceptance criteria:

```text
External failures do not silently break the application.
```

---

## Phase 8 — Testing

Run:

```bash
pytest
```

Test:

- Health endpoint
- Lead creation
- Lead retrieval
- AI response validation
- Missing fields
- Invalid contact
- Qualification scoring
- Qualification thresholds
- Unsupported service
- Emergency flow

---

## Phase 9 — Final Review

Review the entire project as a senior AI automation engineer.

Check:

- Architecture
- Code quality
- AI reliability
- Validation
- Security
- Error handling
- Qualification logic
- n8n workflow
- Tests
- README
- MVP scope

Do not rewrite working code unnecessarily.

---

# 40. Git Strategy

Development must be modular.

Use a branch for each major phase.

Example:

```text
main
│
├── feature/project-setup
├── feature/database
├── feature/ai-service
├── feature/qualification
├── feature/frontend
├── feature/n8n
├── feature/error-handling
└── feature/testing
```

After completing each phase:

1. Run tests.
2. Verify the application.
3. Review changed files.
4. Commit changes.
5. Push the branch.
6. Merge into `main` only after the phase is stable.

Example:

```bash
git checkout -b feature/project-setup

git add .

git commit -m "feat: initialize FastAPI project"

git push -u origin feature/project-setup
```

Do not make one enormous commit containing the entire project.

---

# 41. AI Coding Assistant Rules

These instructions are mandatory for Claude Code, Cursor, Copilot, or another coding assistant.

## Rule 1 — Read the Specification

Before modifying the project:

```text
Read PROJECT_SPEC.md completely.
```

Treat it as the source of truth.

## Rule 2 — Work Incrementally

Implement only the requested phase.

Do not implement future phases unless explicitly requested.

## Rule 3 — No Hallucination

Never invent:

- APIs
- Credentials
- Environment variables
- Database fields
- Business rules
- External integrations
- Files
- Existing functionality

If information is missing, ask before making a consequential assumption.

## Rule 4 — Inspect Existing Code

Before changing a file:

- Read it.
- Understand dependencies.
- Preserve working functionality.

## Rule 5 — Avoid Unnecessary Refactoring

Do not rewrite unrelated working code.

## Rule 6 — Test Every Phase

After implementation:

- Run relevant tests.
- Start the application if applicable.
- Verify functionality.
- Report failures clearly.

## Rule 7 — Git After Stable Modules

After a phase is complete:

- Review changes.
- Commit.
- Push branch.
- Then continue.

## Rule 8 — Security

Never expose:

```text
OPENAI_API_KEY
```

or other secrets.

## Rule 9 — Architecture

Never allow:

```text
Frontend → OpenAI
```

or:

```text
Frontend → n8n
```

The frontend communicates with the FastAPI backend.

## Rule 10 — Business Logic

Never allow the LLM to directly decide or execute:

```text
database writes
notifications
qualification status
lead score
external business actions
```

---

# 42. Phase-by-Phase Coding Prompts

## Prompt 1 — Phase 1

```text
Read PROJECT_SPEC.md completely before making changes.

Implement Phase 1 only.

Create the FastAPI project structure described in the specification.

Tasks:
- Create the required project structure.
- Create the Python application.
- Configure FastAPI.
- Implement GET /health.
- Create requirements.txt.
- Create .env.example.
- Create .gitignore.
- Create a minimal README if required.

Do not implement database, AI, qualification, frontend, or n8n functionality yet.

Do not invent additional features.

After implementation:
1. Run the application.
2. Test /health.
3. Run any relevant tests.
4. Show me the files created/modified.
5. Explain how to run the application.

Do not commit or push until the implementation is verified.
```

---

# 43. Prompt 2 — Phase 2

```text
Read PROJECT_SPEC.md before making changes.

Implement Phase 2 only.

Create:
- SQLite database
- Lead model
- Database connection
- Lead creation operation
- Lead retrieval operation
- Required Pydantic schemas

Follow the exact project structure.

Do not implement AI, frontend, n8n, or advanced features.

Use an isolated database layer so the database can later be migrated to PostgreSQL.

Add tests for lead creation and retrieval.

Run the tests.

After the phase is verified, prepare the changes for Git commit and push.
```

---

# 44. Prompt 3 — Phase 3

```text
Read PROJECT_SPEC.md completely.

Implement Phase 3 only.

Create:
- AI service
- lead_agent_prompt.txt
- Structured AI response schema
- OpenAI integration
- Chat session handling
- AI response validation
- Invalid JSON handling
- Safe fallback behavior

Important:
The LLM must not directly trigger external actions.

The LLM must not be the authoritative source for:
- lead score
- qualification status
- database actions
- notifications

The backend must validate all AI output.

Do not implement n8n yet.

Do not introduce unnecessary frameworks.

Run tests and verify the chat endpoint.

After successful verification, prepare a Git commit.
```

---

# 45. Prompt 4 — Phase 4

```text
Read PROJECT_SPEC.md.

Implement Phase 4 only.

Create the deterministic qualification service.

Requirements:
- Configurable scoring rules.
- Configurable thresholds.
- Valid contact validation.
- Service validation.
- Booking intent handling.
- Budget suitability.
- Timeline suitability.
- Missing required information.
- Human review condition.

Important:
The final score MUST be calculated by backend code.

Do not trust an AI-generated score.

Add unit tests covering:
- qualified
- needs_review
- unqualified
- missing information
- invalid contact
- unsupported service

Do not modify unrelated functionality.

Run all tests and report results.

Prepare the verified changes for Git.
```

---

# 46. Prompt 5 — Phase 5

```text
Read PROJECT_SPEC.md.

Implement Phase 5 only.

Create the basic frontend chat interface using HTML/CSS/JavaScript.

Requirements:
- Chat messages
- Input
- Send button
- Loading state
- Error state
- Session ID handling
- API integration with FastAPI
- Qualification result display

Important:
The frontend must NOT:
- call OpenAI directly
- calculate lead score
- calculate qualification status
- call n8n directly
- contain secrets

Keep the interface clean and minimal.

Do not introduce React or another frontend framework unless absolutely necessary.

Test the browser flow against the backend.

Prepare the verified changes for Git.
```

---

# 47. Prompt 6 — Phase 6

```text
Read PROJECT_SPEC.md.

Implement Phase 6 only.

Create:
n8n/lead_qualification_workflow.json

The workflow should:

Webhook
→ Validate Input
→ Receive backend qualification result
→ Branch by qualification_status

Qualified:
→ Save/confirm lead
→ Notify team
→ Human/booking handoff

Needs Review:
→ Save/confirm lead
→ Notify human

Unqualified:
→ Save/confirm lead
→ Follow-up

Important:
n8n MUST NOT recalculate the lead score.

The backend qualification service remains the source of truth.

Export the workflow as valid JSON.

Document how to import and test it.

Do not implement unrelated features.
```

---

# 48. Prompt 7 — Error Handling Review

```text
Read PROJECT_SPEC.md.

Review the complete implementation for error handling.

Inspect:
- OpenAI calls
- API requests
- Database operations
- n8n webhook calls
- AI JSON parsing
- Pydantic validation
- Missing information
- Invalid input
- Timeouts
- Retry behavior

Implement only necessary improvements.

Use:
- bounded retries
- timeouts
- structured errors
- logging
- safe fallbacks

Do not introduce unnecessary infrastructure.

Do not rewrite working code unnecessarily.

Run the full test suite after changes.

Show me:
1. Problems found.
2. Changes made.
3. Tests performed.
4. Remaining limitations.
```

---

# 49. Prompt 8 — Senior Engineering Review

```text
Read PROJECT_SPEC.md and inspect the entire implementation.

Act as a senior AI automation engineer reviewing this project before submission.

Check:

1. Architecture
2. Separation of concerns
3. AI reliability
4. Structured output
5. Backend validation
6. Deterministic scoring
7. Qualification consistency
8. Database design
9. API design
10. Error handling
11. Security
12. Logging
13. n8n workflow
14. Human handoff
15. Frontend integration
16. Tests
17. README
18. MVP scope

Do not rewrite working code unnecessarily.

First provide a prioritized issue list.

Then fix only issues that are actually necessary.

After fixes:
- run tests
- verify the application
- verify the n8n workflow structure
- check for secrets
- check Git status

Do not invent missing requirements.
```

---

# 50. Final Evaluation Checklist

Before submission:

```text
[ ] FastAPI backend works
[ ] /health works
[ ] Chat works
[ ] AI understands lead intent
[ ] AI extracts structured information
[ ] Missing information is handled
[ ] Invalid contact information is handled
[ ] Emergency flow is handled
[ ] Backend calculates lead score
[ ] Qualification status is deterministic
[ ] Database stores leads
[ ] Lead retrieval works
[ ] n8n workflow exists
[ ] n8n receives backend result
[ ] n8n does not recalculate score
[ ] Qualified leads are routed correctly
[ ] Human review is supported
[ ] Unqualified leads have follow-up path
[ ] AI failures are handled
[ ] Invalid AI output is handled
[ ] API failures are handled
[ ] Timeouts exist
[ ] Retries are bounded
[ ] Structured logging exists
[ ] API keys are hidden
[ ] Tests pass
[ ] README is complete
[ ] Architecture is documented
[ ] Demo video is recorded
[ ] Git repository is clean
```

---

# 51. Final Deliverables

Submit:

1. GitHub repository
2. README.md
3. Working application
4. n8n workflow JSON
5. Short demo video
6. Architecture explanation
7. Test results

---

# 52. Final Explanation for Reviewer

Use this explanation during the technical review:

> I designed the system around a separation between AI reasoning and deterministic business logic.
>
> The AI is responsible for understanding natural language, asking relevant questions, and extracting structured lead information.
>
> The backend validates that information and applies deterministic qualification rules to calculate the final lead score and status.
>
> SQLite stores the resulting lead data, while n8n handles workflow orchestration and integrations such as notifications and human handoff.
>
> The important architectural decision is that the LLM does not directly perform important business actions. This makes the system easier to validate, debug, test, and extend, while reducing the risk of an unreliable model response directly triggering an incorrect business action.

---

# 53. Future Production Improvements

If this MVP were moved toward production, consider:

- PostgreSQL
- Redis
- Authentication
- CRM integration
- WhatsApp integration
- Voice AI / Vapi
- Appointment booking
- Observability
- Rate limiting
- Retry queues
- Analytics dashboard
- Prompt/version management
- Evaluation datasets
- Automated regression tests
- Production deployment
- Role-based access control
- Multi-tenant architecture

These are intentionally outside the MVP.

---

# 54. Definition of Done

The project is complete when a reviewer can:

1. Start the application.
2. Open the chat interface.
3. Have a realistic conversation with the AI.
4. Provide lead information.
5. See structured information extracted.
6. See missing information handled.
7. See the backend calculate the lead score.
8. See the qualification status.
9. Verify that the lead is stored.
10. See n8n receive the final result.
11. See the appropriate workflow branch.
12. See notification/handoff behavior.
13. Review the code and understand the architecture.
14. Run the automated tests.
15. Understand why AI and deterministic business logic are separated.

The MVP should demonstrate:

```text
Working Functionality
+
Sound Engineering Judgment
+
Reliable AI Integration
+
Deterministic Business Logic
+
Automation
```

rather than maximum feature count.

---

# 55. Final Rule

**Do not expand the MVP unless a requirement in this document cannot be demonstrated without the expansion.**

The priority is:

```text
Correctness
    ↓
Reliability
    ↓
Clear Architecture
    ↓
Working Integration
    ↓
Testing
    ↓
Demo Quality
    ↓
Visual Polish
```

Build the smallest complete system that clearly demonstrates the intended engineering decisions.