# AGENTS.md

## Purpose
This repository contains a Python-based system that ingests EIA.gov pipeline data, stores and or transforms the data for api endpoint availability as well a simple UI detailing predictions for the next week's supply levels. 

Primary initial focus:
- Consume and normalize data
- Expose data via api and simple UI
- Make predictions with spot WTI prices and existing crude levels from multiple pad sites

---

## High-Level Goals
When working in this repository, optimize for the following priorities in order:

1. Accuracy
2. Production-ready output
3. Automation
4. Cost minimization
5. Learning and explanations
6. Reliability
7. Speed

---

## General Working Rules
- Prefer Python for implementation unless there is a compelling reason otherwise.
- Keep solutions simple and practical. Do not over-engineer.
- Do not hallucinate behavior, APIs, schemas, or market logic.
- Do not ignore explicit constraints given by the user.
- Ask for clarification only when necessary; otherwise make a reasonable, documented assumption.
- Favor modular design with clean boundaries between ingestion, analytics, signaling, storage, APIs, and frontend support.
- Design code so it can begin as an MVP but evolve cleanly toward production.

---

## Repository Expectations
Agents working in this repository may:
- Read files
- Inspect repository structure and code
- Propose code changes
- Create branches for proposed work
- Add or update documentation
- Suggest architecture changes
- Add tests and developer tooling

Agents must not:
- Delete files unless explicitly instructed
- Spend money or require paid services without approval
- Send emails or messages to external recipients without approval
- Introduce breaking architectural changes without clearly documenting them
- Invent data sources, credentials, or infrastructure that do not exist

Pull requests must be approved by the user before merge.

---

## Required Documentation Practice
- Always record meaningful work, findings, experiments, and decisions in `EXPERIMENT.md`.
- Preserve history rather than overwriting prior results without context.
- When changing architecture or workflows, update relevant docs in the same effort.
- If assumptions are made, document them clearly.

---

## Coding Standards
### Python
- Follow PEP 8 naming and style conventions.
- Prefer clear, maintainable code over clever code.
- Use type hints where practical.
- Use small, testable functions.
- Keep business logic separate from transport or framework code.
- Avoid large monolithic scripts when modules are more appropriate.

### Project Structure
- `src/pipeline_pred/` for ingestion, storage, features, models, CLI, and API implementation
- `scheduler/` compatibility entrypoint for scheduled CLI execution
- `api/` compatibility entrypoint and optional API-only Dockerfile
- `images/` store for any assets delivered to web front
- `notebooks/` legacy research history
- `tests/` for automated validation
- `Dockerfile` image that runs scheduled ingest and prediction

### Configuration
- Keep secrets out of source control.
- Use environment variables or `.env` files for credentials and environment-specific settings.
- Commit a safe `.env.example` when useful.
- Prefer config-driven symbols, intervals, thresholds, and notification settings.

---

## Architecture Guidance
When proposing or implementing solutions:
- Treat market data ingestion as a source-of-truth boundary.
- Keep trading logic separate from ingestion plumbing.
- Prefer closed-candle logic first unless there is a strong reason for tick-level logic.
- Design alerting so duplicate notifications are prevented.
- Make timeframes, symbols, tolerances, and Fib levels configurable.
- Prefer components that can run independently if the system later grows into multiple services.
- Avoid unnecessary coupling between backend analytics and frontend rendering.

---

## Frontend / Web Client Direction
This project is expected to deliver real-time and near-time data for web clients, database servers and cache servers.

When building backend services, prefer interfaces that are easy for a frontend to consume:
- stable JSON responses
- predictable field names
- explicit timestamps and timezone offsets
- clear status/health endpoints

If websocket or SSE support is added later, keep those concerns isolated from the analytics core.

---

## Testing and Validation
- Validate edge cases around swing anchors, tolerance bands, timeframe rollovers, and deduplication.
- Prefer unit tests for math and logic, and integration tests for ingestion/storage boundaries where practical.
- If no test is added, explain why.

---

## Change Management
When making meaningful changes:
- Describe the problem being solved
- Describe the chosen approach
- Call out tradeoffs
- Note any follow-up work still needed

For larger efforts, phase work as:
1. Minimal working version
2. Stabilization / cleanup
3. Production hardening

---

## Preferred Output Style for Agents
- Be concise
- Use bullet points when helpful
- Give simple reasoning
- Present options when warranted
- Do not overwhelm with unnecessary complexity

---

## Default Assumptions for This Repository
Unless told otherwise, assume:
- Python is the primary language
- Correct and Real-time market data is important
- A web client frontend consumes backend outputs
- Data will be stored in relational databases and cache servers
- Internal tools and services should be practical, maintainable, and automation-friendly

---

## What Good Looks Like
A good contribution in this repository:
- moves the system toward a usable automated data ingestion platform
- improves correctness or maintainability
- keeps the design understandable
- avoids unnecessary complexity
- documents decisions and experiments clearly
