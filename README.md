 # AI Automation Feasibility Analyzer

 AI Automation Feasibility Analyzer is a lightweight toolkit that uses live web context, large language models, and a curated planning/generation workflow to determine whether a manual process can be automated, craft a detailed plan, and generate executable artifacts once the plan has been approved.

 ## Features

- **Feasibility assessment** using GPT-based reasoning enriched with live web context fetched via DuckDuckGo scraping.
- **Structured planning** agent that converts feasibility results into a detailed implementation plan with timelines, risk mitigation, and monitoring guidance.
- **Generator agent** that produces Python scripts, n8n workflows, and scheduling instructions after user approval.
- **Simple SPA frontend** to orchestrate the analysis → planning → generation flow.

 ## Tech stack

- **Backend**: FastAPI + Uvicorn
- **LLM**: OpenRouter (configured to use `openai/gpt-4o-mini` via the Gemini client wrapper)
- **Web context**: Scrapy selectors + requests to gather contextual signals from DuckDuckGo
- **Frontend**: Vanilla HTML/CSS/JavaScript served from `frontend/`

 ## Prerequisites

- Python 3.11+ (verify with `python --version`)
- `pip` for installing dependencies
- Internet access (LLM calls & DuckDuckGo lookups)

 ## Setup

1. Clone the repository and switch into the project directory.
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file or otherwise export the following environment variable:
   ```env
   OPENROUTER_API_KEY=<your OpenRouter API key>
   ```
   The backend relies on this key to call the OpenRouter / Gemini APIs.

 ## Running the project

The project provides both backend and frontend components. You can run them concurrently in separate terminals:

- **Backend (FastAPI)**
  ```bash
  uvicorn app:app --host 0.0.0.0 --port 5000 --reload
  ```
  This starts the API server that exposes endpoints for `/analyze`, `/plan`, `/generate`, `/health`, and a demo payload at `/demo/y-combinator`.

- **Frontend (static SPA)**
  ```bash
  cd frontend
  python -m http.server 8000
  ```
  Open `http://localhost:8000` and interact with the UI to submit workflows.

The `run.txt` file includes the above commands for convenience.

 ## API overview

### POST `/analyze`
- Request body: `{ "workflow": string }`
- Returns a JSON feasibility analysis enriched by live context and compliance checks.

### POST `/plan`
- Request body: `{ "workflow": ..., "analysis": ... }`
- Requires analysis to indicate the workflow is automatable; otherwise returns an error.
- Produces a structured plan with steps, risks, monitoring strategy, timeline, etc.

### POST `/generate`
- Request body: `{ "workflow": ..., "analysis": ..., "plan": ..., "approval": bool }`
- Only runs if `approval` is `true`; otherwise returns an error.
- Returns generated assets, run instructions, and limitations.

### GET `/health`
- Simple readiness indicator returning `{ "status": "ok" }`.

### GET `/demo/y-combinator?n=<int>`
- Returns a demo payload resembling Y Combinator pitch data.

## Project structure

- `app.py`: FastAPI entry point that wires together analyzer, planner, generator agents.
- `agents/`: Core orchestration layers that delegate to services (analyzer, planner, generator).
- `services/`: External integrations (Gemini client for OpenRouter LLM calls, `WebContextFetcher` for live context). 
- `frontend/`: Static SPA that submits workflows and shows analysis → plan → generation steps.
- `utils/`: Validators and helper scripts (current utilities include JSON validation and a demo payload builder).

## Development notes

- The analyzer emphasizes transparent decision-making by capturing `live_context_used`, `constraints`, `assumptions`, and `alternative_suggestions`.
- The planner strictly validates that required fields exist in the generated JSON before returning it to ensure downstream components have all they need.
- The generator enforces strict adherence to approved plans, validating the JSON structure before returning assets.

## Testing

- There are no automated tests provided yet. Use manual testing via the UI or curl/postman against the FastAPI endpoints.
  ```bash
  curl -X POST http://localhost:5000/analyze -H 'Content-Type: application/json' -d '{"workflow": "<your description>"}'
  ```

## Environment variables

- `OPENROUTER_API_KEY` – required by `services/gemini_client.GeminiClient` to authenticate with the OpenRouter LLM endpoint.

## Troubleshooting

- If `OPENROUTER_API_KEY` is missing, the backend raises `ValueError` on startup.
- DuckDuckGo scraping may intermittently fail if request limits are reached; the fetcher logs but continues gracefully.

## Contributing

Feel free to submit issues or pull requests to improve the assistant’s agents, expand the front-end UX, or add tests.

## License

This project does not specify a license (add one if you plan to open source it)."# Automation-Feasibility-Analyzer" 
