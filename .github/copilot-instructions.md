# Copilot Instructions — LeetCode Tracker

## Build & Run

```bash
# Setup (first time)
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
python seed.py                 # Pre-loads 75 LeetCode problems

# Run
python app.py                  # Starts on http://127.0.0.1:5000
```

No test suite or linter configured yet.

## Architecture

Flask app with two blueprints and a shared SQLAlchemy database:

- **`views.py`** — HTML page routes (`/`, `/problems`, `/problems/<id>`, `/log`). These are thin — they just render Jinja2 templates. All data fetching happens client-side via JS calling the API.
- **`api.py`** — REST API under `/api/`. This is where all business logic lives: problem listing, attempt logging, stats aggregation, Leitner scheduling.
- **`models.py`** — SQLAlchemy models + the Leitner spaced repetition engine. `Problem.record_attempt()` is the core method that handles box promotion/demotion.
- **`seed.py`** — One-time script to populate the DB with LeetCode 75 problems. Idempotent (skips if data exists).

Frontend is vanilla JS in Jinja2 templates — no build step. Templates fetch from `/api/*` endpoints and render dynamically. Chart.js is loaded from CDN.

## Leitner Spaced Repetition System

This is the core domain logic. Every problem has a `leitner_box` (1–5) and `next_review_date`:

- **Promotion:** passed=True AND confidence >= 3 → box + 1 (max 5)
- **Demotion:** failed OR confidence <= 2 → back to box 1
- **Intervals:** Box 1 = 1 day, Box 2 = 2 days, Box 3 = 4 days, Box 4 = 8 days, Box 5 = 16 days
- **Due queue:** `GET /api/due` returns problems where `next_review_date <= today`, ordered by lowest box first, randomized within each box for topic interleaving

The constants live in `LEITNER_INTERVALS` dict in `models.py`. The logic lives in `Problem.record_attempt()`.

## Key Conventions

- **No migrations.** Schema changes are done via `ALTER TABLE` on the SQLite DB directly, then updating the model. `db.create_all()` runs on every startup.
- **`to_dict()` pattern.** Every model has a `to_dict()` method for JSON serialization. `Problem.to_dict(include_attempts=True)` controls whether nested attempts are included.
- **Timestamps use local time** (`datetime.now()`), not UTC.
- **Database lives in `instance/tracker.db`** (gitignored). Losing it means re-running `seed.py` — attempt history is lost.

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/problems` | List problems. Filters: `category`, `topic`, `difficulty`, `box`, `status` |
| GET | `/api/problems/<id>` | Single problem with all attempts |
| GET | `/api/due` | Today's Leitner review queue |
| POST | `/api/attempts` | Log attempt — auto-updates Leitner box. Returns new box + next review date |
| GET | `/api/stats` | Dashboard stats: pass rate, confidence calibration, box distribution |
| GET | `/api/topics` | Per-topic analytics |

## Attempt Scoring Fields

Each attempt tracks multiple metrics — some user-reported, some AI-provided:

- `passed` (bool), `time_taken_minutes` (int), `confidence` (1–5) — user reports these
- `solution_code` (text) — the actual Python solution
- `ai_score` (1–10), `ai_feedback` (text) — AI analysis of solution quality
- `complexity_score` (1–5) — how accurately the user identified time/space complexity

## Copilot CLI Workflow for Logging Attempts

When the user pastes a LeetCode solution and says they completed a problem, follow this workflow:

1. **Identify the problem** from the solution code or user's message. Match it to a problem in the tracker.
2. **Analyze the solution** — assess correctness, time/space complexity, code quality, edge cases, and patterns used.
3. **Quiz the user on complexity** — ask "What's the time and space complexity of your solution?" BEFORE revealing your analysis. Score their answer 1–5 for `complexity_score`.
4. **Score the solution** 1–10 for `ai_score` with detailed `ai_feedback` covering: correctness, complexity analysis, code quality, pattern recognition, and improvement tips vs. previous attempts.
5. **Ask the user** for: confidence (1–5), time taken (minutes), and whether it passed all test cases.
6. **POST to the tracker API** at `http://127.0.0.1:5000/api/attempts` with all fields. Use PowerShell `Invoke-RestMethod`. Example:
   ```powershell
   $body = @{ problem_id = ID; passed = $true; time_taken_minutes = N; confidence = N; solution_code = "..."; ai_score = N; ai_feedback = "..."; complexity_score = N; notes = "..." } | ConvertTo-Json
   Invoke-RestMethod -Uri http://127.0.0.1:5000/api/attempts -Method POST -Body $body -ContentType "application/json"
   ```
7. **Report the result** — show the Leitner box update and next review date from the API response.
8. **Show the optimal solution** — present the best/cleanest solution for the problem with a brief explanation of what makes it better (e.g., fewer passes, in-place tricks, cleaner edge case handling). Then give specific, actionable tips on what the user should do differently next time based on comparing their solution to the optimal one.
