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

## Run

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000/health](http://localhost:8000/health).

## Testing

```bash
pytest
```
