# Architecture, Tools and Key Learnings

## 1. Project Overview

The AI Research Agent accepts a topic, gathers information from multiple webpages and returns a structured Markdown report with source attribution. It also demonstrates agent-controlled tool use and multi-turn conversation context through the Claude Agent SDK.

## 2. Architecture

The project is split into three layers:

1. **Vue frontend** : collects the research topic, calls the backend and safely displays the Markdown report.
2. **FastAPI backend** : validates requests, coordinates research, handles failures and exposes the API.
3. **Research and model layer** : searches and reads webpages, prepares evidence and uses LiteLLM and OpenRouter for report synthesis.

```text
User
  -> Vue 3 interface
  -> FastAPI /api/research
  -> DDGS search
  -> HTTPX page download
  -> Trafilatura / BeautifulSoup extraction
  -> bounded evidence collection
  -> LiteLLM Proxy
  -> OpenRouter free model
  -> validated Markdown report
  -> Vue display
```

The Claude Agent SDK is integrated into the user-facing workflow as well as the demonstration scripts. For new research it can select and execute the registered web tools. If a free model or SDK route fails, the application uses deterministic evidence collection followed by LiteLLM synthesis. This keeps the application available while retaining agent-controlled tool use as the primary path.

Each completed report receives a session identifier. The backend stores the topic, report and recent follow-up turns. During a follow-up the SDK receives this context and decides whether it can answer directly or needs to call the web tools for new evidence.

## 3. Main Technical Decisions

### Bounded research instead of an unrestricted agent loop

The workflow performs a limited number of searches, chooses distinct sources and limits extracted text. This was selected over an unrestricted tool loop because free models can repeatedly call tools, become slow, or fail to stop. The bounded design gives predictable time and resource usage.

### DDGS for search

DDGS was selected because it is free and does not require an API key. Services such as Tavily and Brave Search offer stronger commercial APIs but their free tiers have quotas or require separate credentials.

### HTTPX for page downloading

HTTPX supports asynchronous requests, timeouts, redirects and response limits. It was preferred over Requests because the FastAPI workflow is asynchronous and over Playwright because most research pages do not require the overhead of a full browser.

### Trafilatura with BeautifulSoup fallback

Trafilatura is the primary extractor because it removes navigation, advertising and other page boilerplate. BeautifulSoup is used when Trafilatura cannot extract useful text. BeautifulSoup alone provides more control but requires more manual cleanup.

### LiteLLM Proxy with OpenRouter

LiteLLM provides one model interface and keeps the application independent of a single model provider. OpenRouter supplies free model access. A specific free model is attempted first and `openrouter/free` is used as a dynamic fallback.

### Pydantic validation

Pydantic validates API input and output through typed models. This prevents empty or malformed topics from reaching the research workflow and gives clients consistent error responses.

### Structured Markdown reports

Markdown is readable, portable and easy to render in Vue. The backend checks for required report sections, while the frontend uses Marked and DOMPurify so formatted output is displayed safely.

### Normal HTTP before streaming

The first version uses a normal request-response API because it is simpler to implement and test. Server-Sent Events can be added later to show live progress without changing the core research tools.

### SQLite deferred

Active conversation context is integrated through an in-memory session store. Persistent SQLite history remains an extension for deployments that need conversations to survive a server restart.

## 4. Reliability and Safety

- Only public HTTP and HTTPS URLs are accepted.
- Localhost and unsupported URL schemes are rejected.
- Downloads have time and size limits.
- Webpage text is treated as untrusted evidence rather than agent instructions.
- Search count, source count and evidence length are bounded.
- Model output is checked for required report sections.
- Free-model timeouts and rate limits produce a clearly labelled evidence fallback.
- Secrets stay in `.env` and are not exposed to the frontend or committed to Git.

## 5. Testing

The backend test suite covers search validation, URL safety, extraction, research orchestration, report validation, request validation, successful API responses and failure handling. The Vue production build checks that the frontend compiles correctly.

## 6. Key Learnings

- An agent needs clear tool descriptions, stopping rules and usage limits.
- Tool-capable models do not always execute multi-step loops reliably.
- Deterministic retrieval combined with model synthesis is more dependable for free models.
- Source quality, distinct-source selection and citations are as important as fluent writing.
- Free services require fallbacks, timeouts and output validation.
- Separating frontend, API, tools and model access makes the project easier to test and modify.
- A local Git commit becomes visible on GitHub only after it is pushed to the configured remote.
