# Complete Lab Submission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete every graded Day 12 deliverable that remains after the deployed CP1–CP5 service and CI/CD bonus.

**Architecture:** The FastAPI service, Docker image, Redis instance, Render deployment, and GitHub Actions workflow already satisfy the executable checkpoints. Remaining work is evidence-based submission documentation: record reproducible Docker measurements, explain the observed deployment incident, fill ten personal reflection answers, and verify the grader against the live deployment.

**Tech Stack:** Python 3.11, FastAPI, Docker, Redis, Render, GitHub Actions, pytest.

## Global Constraints

- Do not place any secret value from `.env` in a tracked file or command output.
- Preserve the deployed API contract: `GET /healthz`, `GET /readyz`, and authenticated `POST /chat`.
- Use measured local Docker results for image-size and cache answers.
- Keep reflection answers specific to this repository and the observed Render deployment.
- Run `grade.py` and the full pytest suite before committing.

---

### Task 1: Establish the remaining grading baseline

**Files:**
- Read: `grade.py`, `README.md`, `exercises.md`, `tests/test_cp5.py`, `tests/test_bonus_cicd.py`

**Interfaces:**
- Consumes: existing deployed service URL in `DEPLOYMENT.md`
- Produces: an explicit inventory of executable and written deliverables

- [ ] **Step 1: Run the grader before documentation changes**

Run: `.venv\\Scripts\\python.exe grade.py`

Expected: CP1–CP5 and bonus results are reported; exercises show zero answered questions.

- [ ] **Step 2: Map every remaining placeholder in `exercises.md`**

Run: `rg -n "> \\*Câu trả lời" exercises.md`

Expected: ten answer placeholders are found.

### Task 2: Collect reproducible Docker evidence

**Files:**
- Create temporarily: a one-stage Dockerfile used only for the comparison build
- Read: `Dockerfile`, `.dockerignore`
- Modify: `exercises.md`

**Interfaces:**
- Consumes: repository Docker build context and production `Dockerfile`
- Produces: exact image-size and cache-observation statements for Questions 3 and 4

- [ ] **Step 1: Build a deliberately one-stage comparison image**

Use a Python 3.11 slim image, copy `requirements.txt`, install dependencies, then copy `app` and `utils`; start Uvicorn on `${PORT:-8000}`.

- [ ] **Step 2: Run both Docker builds and capture image sizes**

Run: `docker build -f <comparison-file> -t day12-chat:single .` and `docker build -t day12-chat:multi .`

Expected: both builds exit zero and Docker reports their image sizes.

- [ ] **Step 3: Verify cache boundaries without leaving a source edit behind**

Copy `app/main.py`, append a harmless newline, build again, restore the exact original bytes, and inspect the build output.

Expected: dependency-install layers are cached; the source-copy and final runtime-copy layers rebuild.

### Task 3: Complete the reflection submission

**Files:**
- Modify: `exercises.md`

**Interfaces:**
- Consumes: Tasks 1–2 evidence and the observed Redis deployment incident
- Produces: ten non-placeholder Vietnamese answers, each matching one numbered question

- [ ] **Step 1: Replace the header placeholders with student identity**

Set the name to Nguyễn Hùng Mạnh and student code to 2A202601256.

- [ ] **Step 2: Replace every answer placeholder with a repository-specific answer**

Cover fail-fast config, structured log fields, measured Docker comparison, Docker cache, non-root security, RFC 6750 responses, token-bucket math, daily budget behavior, liveness/readiness incident sequence, and the actual initial Redis hostname failure on Render.

- [ ] **Step 3: Ensure no secret-shaped strings are included**

Run: `rg -n "sk-|API_TOKEN\\s*[:=]\\s*[A-Za-z0-9_-]{12,}|redis(?:s)?://[^\\s]+@" exercises.md`

Expected: no output.

### Task 4: Verify, commit, and publish the completed submission

**Files:**
- Verify: `exercises.md`, `DEPLOYMENT.md`, `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: completed documentation and live deployment
- Produces: an auditable Git commit and green GitHub Actions run

- [ ] **Step 1: Run all automated tests**

Run: `.venv\\Scripts\\python.exe -m pytest tests -q`

Expected: no failed tests; only intended skips may remain.

- [ ] **Step 2: Run the full grader**

Run: `.venv\\Scripts\\python.exe grade.py`

Expected: all five checkpoints score full points, all 10 reflection answers are counted, and bonus CI/CD tests pass.

- [ ] **Step 3: Review tracked changes for accidental secret leakage**

Run: `git diff --check` and `git diff -- exercises.md`

Expected: no whitespace errors and no secret value in the diff.

- [ ] **Step 4: Commit and push only verified documentation changes**

Run: `git add exercises.md docs/superpowers/plans/2026-08-10-complete-lab-submission.md && git commit -m "docs: complete Day 12 reflection exercises" && git push origin main`

Expected: GitHub Actions starts from the pushed commit.
