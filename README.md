# AI Research Agent

A source-backed web research application built with the Claude Agent SDK, LiteLLM, OpenRouter, FastAPI and Vue 3. It accepts a research topic, searches the web, reads multiple sources and returns a structured Markdown report with citations.

## Features

- Accepts a research topic through a Vue interface.
- Searches the web with DDGS.
- Downloads webpages asynchronously with HTTPX.
- Extracts main article text with Trafilatura and uses BeautifulSoup as a fallback.
- Demonstrates Claude Agent SDK tool execution and conversation context.
- Supports follow-up questions through a saved research session.
- Lets the Agent SDK decide whether a follow-up needs another web search.
- Uses LiteLLM as the model gateway and OpenRouter as the model provider.
- Prioritizes government, international, university and established organization sources.
- Produces structured Markdown reports with inline source references.
- Validates report structure before returning it to the frontend.
- Provides a clearly labelled evidence fallback when free models time out or are rate-limited.
- Sanitizes rendered Markdown with DOMPurify.

## Architecture

```text
Vue 3 frontend
      |
      | Axios / HTTP
      v
FastAPI backend
      |
      +--> DDGS web search
      +--> HTTPX page download
      +--> Trafilatura / BeautifulSoup extraction
      +--> Claude Agent SDK tool and context demonstrations
      |
      v
LiteLLM Proxy
      |
      v
OpenRouter free models
```

The user-facing endpoint follows a bounded workflow: it performs two searches, selects two distinct usable sources, extracts a limited amount of text and sends the evidence through LiteLLM for report synthesis. The bounded design prevents uncontrolled tool loops and reduces free-model latency. If the free provider is unavailable, the API returns a labelled extractive evidence report instead of an unstructured failure.

## Technology Stack

| Area | Technology |
|---|---|
| Frontend | Vue 3, Vite, JavaScript |
| Styling and icons | CSS, Lucide Vue |
| HTTP client | Axios |
| Markdown display | Marked, DOMPurify |
| Backend | FastAPI, Pydantic |
| Agent framework | Claude Agent SDK |
| Model gateway | LiteLLM Proxy |
| Model provider | OpenRouter |
| Primary model | `openai/gpt-oss-20b:free` |
| Free fallback | `openrouter/free` |
| Web search | DDGS |
| Page download | HTTPX |
| Text extraction | Trafilatura, BeautifulSoup fallback |
| Testing | Pytest, pytest-asyncio, FastAPI TestClient |

## Project Structure

```text
research-agent/
|-- backend/
|   |-- app/
|   |   |-- agent/          # SDK tests and research orchestration
|   |   |-- tools/          # Search, download, extraction, SDK web tools
|   |   |-- main.py         # FastAPI application and endpoints
|   |   `-- models.py       # Pydantic request/response models
|   |-- tests/              # Backend automated tests
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- services/api.js # Axios API client
|   |   |-- App.vue         # Research interface
|   |   `-- style.css
|   `-- package.json
|-- litellm/
|   `-- config.yaml
|-- .env.example
|-- .gitignore
`-- README.md
```

## Prerequisites

- Python 3.10 or newer
- Node.js and npm
- Git
- A free OpenRouter API key

The project was developed and tested on Windows with Python 3.13.

## Setup

### 1. Clone the repository

```powershell
git clone https://github.com/himanshi-kaushik/research-agent.git
cd research-agent
```

### 2. Create the Python virtual environment

```powershell
python -m venv .venv
```

PowerShell may block activation scripts. Every command below calls the virtual-environment executable directly, so activation is not required.

### 3. Install backend dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

### 4. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace:

```text
OPENROUTER_API_KEY=replace_with_your_key
```

with your real OpenRouter key. Never commit `.env`; it is excluded by `.gitignore`.

### 5. Install frontend dependencies

```powershell
cd frontend
npm.cmd install
cd ..
```

## Running the Application

The application uses three local services. Run each service in a separate PowerShell terminal.

### Terminal 1: LiteLLM Proxy

```powershell
cd "C:\path\to\research-agent"

Get-Content .env | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object { $name,$value = $_ -split '=',2; Set-Item -Path "Env:$name" -Value $value }

.\.venv\Scripts\litellm.exe --config .\litellm\config.yaml --port 4000
```

### Terminal 2: FastAPI

```powershell
cd "C:\path\to\research-agent"
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --port 8000
```

On Windows, do not use Uvicorn's `--reload` option with the Claude Agent SDK. The reload event loop cannot launch the SDK subprocess.

FastAPI documentation is available at `http://127.0.0.1:8000/docs`.

### Terminal 3: Vue

```powershell
cd "C:\path\to\research-agent\frontend"
npm.cmd run dev
```

Open the Vite URL, normally `http://localhost:5173`.

## API

### Health check

```http
GET /api/health
```

### Generate research

```http
POST /api/research
Content-Type: application/json

{
  "topic": "Benefits and limitations of solar energy adoption"
}
```

Successful response:

```json
{
  "topic": "Benefits and limitations of solar energy adoption",
  "report": "# Research Report: ...",
  "session_id": "generated-session-id"
}
```

### Ask a follow-up question

```http
POST /api/followup
Content-Type: application/json

{
  "session_id": "generated-session-id",
  "question": "Which limitation is most important?"
}
```

The backend restores the original topic, report and recent conversation turns. The Agent SDK then decides whether the saved evidence is sufficient or whether it should call the web tools again.

## Testing

Run all backend tests:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -v
```

Build the frontend:

```powershell
npm.cmd --prefix frontend run build
```

The current project contains 23 backend tests covering URL validation, extraction, orchestration rules, report validation, session context, API validation, successful responses and safe failure handling.

## Agent SDK Demonstrations

With LiteLLM running, the following scripts demonstrate the required Agent SDK capabilities:

```powershell
# Basic SDK connection
.\.venv\Scripts\python.exe -m backend.app.agent.sdk_smoke_test

# Real in-process tool execution
.\.venv\Scripts\python.exe -m backend.app.agent.sdk_tool_test

# Multi-turn conversation context
.\.venv\Scripts\python.exe -m backend.app.agent.sdk_context_test

# Search, select, read and answer workflow
.\.venv\Scripts\python.exe -m backend.app.agent.sdk_research_test
```

## Free-Model Limitations

The project is designed to operate without paid model usage. OpenRouter free models can be slow, temporarily unavailable, removed, or rate-limited. For that reason:

- LiteLLM configures a specific primary model and a dynamic free fallback.
- The API has a fixed timeout.
- Source text is bounded before synthesis.
- Incomplete model output is rejected.
- When no free model is available, the API returns a labelled evidence report from the retrieved sources.

The fallback keeps the demonstration usable, but it is extractive and less polished than a model-generated synthesis.

## Security and Reliability

- API keys remain in `.env` and are never sent to Vue.
- Only HTTP and HTTPS webpages are accepted.
- Localhost URLs and unsupported content types are blocked.
- Page size and request time are limited.
- Webpage content is treated as untrusted evidence, not instructions.
- Generated Markdown is sanitized before browser rendering.
- Backend exceptions are logged while the API returns a safe generic error.

## Key Learnings

- Agent prompts need explicit stopping conditions and tool budgets.
- Tool-call capability does not guarantee consistent tool-loop behaviour.
- Search and page extraction should be deterministic before model synthesis.
- Free-model routing requires timeouts, validation and graceful fallbacks.
- Dependency versions must be pinned when LiteLLM and FastAPI compatibility changes.
- A local Git repository is separate from GitHub until a remote is connected and pushed.
- Conversation context can be maintained by storing a session identifier with its report and recent turns.

## Deliverables

- Source code
- Setup and run instructions
- Automated tests
- Structured research reports with source attribution
- Architecture and key-learnings documentation
