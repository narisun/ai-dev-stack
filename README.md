# ai-dev-stack

Local development orchestration for the Enterprise AI Platform — Docker Compose
stack that runs the agent + MCP servers + supporting infrastructure (Postgres,
Redis, OPA, OTel collector, LangFuse, LiteLLM).

## Quick start

```bash
cp .env.example .env   # fill in real secrets
make setup             # bring up the full stack and load test fixtures
make start             # bring up any stopped containers
make stop              # stop without losing data
make restart           # stop + start
make wipe              # nuclear: remove all volumes (loses Langfuse user accounts)
make logs S=analytics-agent N=200  # tail recent logs
```

## What runs

| Service | Image | Port | Purpose |
|---|---|---|---|
| analytics-agent | `ghcr.io/narisun/ai-agent-analytics:0.4.0` | 8086 | LangGraph orchestrator |
| data-mcp | `ghcr.io/narisun/ai-mcp-data:0.4.0` | 8080 | Read-only SQL MCP |
| salesforce-mcp | `ghcr.io/narisun/ai-mcp-salesforce:0.4.0` | 8081 | Salesforce CRM MCP |
| payments-mcp | `ghcr.io/narisun/ai-mcp-payments:0.4.0` | 8082 | Payments analytics MCP |
| news-search-mcp | `ghcr.io/narisun/ai-mcp-news-search:0.4.0` | 8083 | News search MCP (Tavily) |
| pgvector | `pgvector/pgvector:pg16` | 5432 | Postgres + pgvector |
| redis | `redis:7.2-alpine` | (network only) | Cache |
| opa | OpenPolicyAgent | 8181 | Authorization engine |
| otel-collector | OpenTelemetry | 4317/4318 | Trace pipeline |
| langfuse | langfuse/langfuse | 3001 | LLM trace UI |
| litellm | litellm/proxy | 4000 | LLM routing |

The Next.js dashboard (`narisun/ai-frontend-analytics`) deploys via Vercel and
points at the analytics-agent's URL — it's not part of this compose stack.

## Source repos

- SDK: https://github.com/narisun/ai-platform-sdk (v0.4.0)
- Analytics agent: https://github.com/narisun/ai-agent-analytics
- MCPs: https://github.com/narisun/ai-mcp-{data,salesforce,payments,news-search}
- Frontend: https://github.com/narisun/ai-frontend-analytics
- This repo (orchestration + integration tests): https://github.com/narisun/ai-dev-stack

## Bumping a service version

To pick up a new release of a service repo, update its `image:` tag in
`docker-compose.yml` and run `make restart`. CI's E2E workflow always
runs `docker compose pull` so it gets whatever's tagged at the time of the run.

## Integration tests

```bash
pip install -r tests/requirements.txt
pytest tests/integration -v
```

These tests assume the compose stack is running (`make setup` first).

## OPA policies

Policies live in `policies/` and are mounted into the OPA container.
Edit a `.rego` file and `make restart opa` to reload.
