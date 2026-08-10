# 12-Factor Audit — Day 12 Chat Service

Day 12 does not claim that this small lab is a complete 12-factor SaaS. It implements and demonstrates the factors relevant to a containerized HTTP service, while documenting the factors that require product or platform policy beyond the lab.

| Factor | Status | Evidence in this repository |
|---|---|---|
| I. Codebase | Implemented | One Git repository and one deployable service from `main`. |
| II. Dependencies | Implemented | `requirements.txt` declares Python dependencies; Docker installs from that file. |
| III. Config | Implemented | `app/config.py` reads `PORT`, `API_TOKEN`, `REDIS_URL`, rate and budget settings from environment via `pydantic-settings`. `API_TOKEN` has no default, so a missing secret fails at startup. |
| IV. Backing services | Implemented | `REDIS_URL` is the interchangeable attachment for local Compose Redis, `fake://` tests, or Render Key Value. |
| V. Build, release, run | Implemented | `Dockerfile` creates the image; Render deploys that image with environment values supplied outside Git. |
| VI. Processes | Implemented | Conversation history, rate-limit state, and spend state live in Redis instead of process memory. |
| VII. Port binding | Implemented | Uvicorn binds to `PORT` in `Dockerfile`; Render supplies the production port. |
| VIII. Concurrency | Ready to scale | The service has no in-process user state, so multiple web instances can share the same Redis data. The current Render Free instance is intentionally single-instance. |
| IX. Disposability | Implemented | `app/lifecycle.py` handles SIGTERM/SIGINT; `/healthz` reports draining before Uvicorn exits. |
| X. Dev/prod parity | Implemented | Local Compose and Render run the same Docker image; only environment values and the Redis attachment change. |
| XI. Logs | Implemented | `app/logging_utils.py` emits one JSON object per line to stdout for platform log collection. |
| XII. Admin processes | Outside lab scope | The service has no migrations or scheduled administrative task. If added, it should run from the same image and environment as the web service. |

## Demo flow

1. Open `/docs` and show the three API operations.
2. Call `/healthz` (process liveness) and `/readyz` (real Redis readiness).
3. Call `/chat` without `Authorization` to show 401 and `WWW-Authenticate: Bearer`.
4. Authorize with the app's `API_TOKEN`, set `X-Client-Id`, then call `/chat` twice. The second response has a higher `turns_before`, proving history is in Redis.
5. Show the JSON `chat_completed` event in Render logs, then show the GitHub Actions test → build → deploy flow.

## CI/CD configuration

The GitHub Actions workflow uses two separate protected inputs:

- `RENDER_TOKEN` is a GitHub Actions **Secret** because it can control the Render account.
- `RENDER_SERVICE_ID` is a GitHub Actions **Variable** because it identifies the target service but is not a credential.

The `deploy` job runs only on pushes to `main`, only after `test` and `build` pass, and only when `RENDER_SERVICE_ID` is configured. It calls Render's deploy API; a successful GitHub job is evidence of continuous deployment, not merely continuous integration.
