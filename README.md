# ⚡ LeetCode Tracker

A local web app for tracking coding interview prep with **spaced repetition** (Leitner system). Built with Flask + SQLite.

Instead of randomly grinding problems, this tracker schedules your daily review queue using science-backed techniques — so you spend most of your time on problems you're weakest at.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Flask](https://img.shields.io/badge/Flask-3.x-green) ![License](https://img.shields.io/badge/license-MIT-gray)

## Features

- **📅 Daily Review Queue** — Leitner spaced repetition tells you exactly what to practice today
- **📊 Dashboard** — stats, topic heatmap, confidence-vs-reality calibration chart
- **🤖 AI Feedback** — log solutions via GitHub Copilot CLI for scoring, complexity analysis, and improvement tips
- **📈 Progress Tracking** — per-problem attempt history with confidence trends and solution diffs
- **🔌 REST API** — log attempts programmatically from scripts or CLI tools
- **75 problems** pre-loaded from the LeetCode 75 list

## How the Leitner System Works

Every problem lives in a box (1–5). Get it right → moves up (reviewed less often). Get it wrong → back to Box 1.

| Box | Review Interval | Meaning |
|-----|----------------|---------|
| 1 | Every day | New or struggling |
| 2 | Every 2 days | Starting to learn |
| 3 | Every 4 days | Getting comfortable |
| 4 | Every 8 days | Nearly mastered |
| 5 | Every 16 days | Mastered |

## Quick Start

```bash
# Clone
git clone https://github.com/diegoruv20/leetcode-tracker.git
cd leetcode-tracker

# Setup
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
# source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt

# Seed the database with LeetCode 75 problems
python seed.py

# Run
python app.py
```

Open **http://127.0.0.1:5000**

## Logging Attempts

### Via the Web UI
Go to `/log`, select a problem, enter your results, and paste your solution.

### Via Copilot CLI (recommended)
Paste your solution in a Copilot CLI session. Copilot will:
1. Analyze your code for correctness, complexity, and code quality
2. Quiz you on time/space complexity
3. Score it 1–10 with detailed feedback
4. POST everything to the tracker API automatically

### Via API
```bash
curl -X POST http://127.0.0.1:5000/api/attempts \
  -H "Content-Type: application/json" \
  -d '{
    "problem_id": 1,
    "passed": true,
    "time_taken_minutes": 15,
    "confidence": 4,
    "solution_code": "def twoSum(nums, target): ...",
    "ai_score": 8,
    "ai_feedback": "Clean solution using hash map.",
    "complexity_score": 5
  }'
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/problems` | List problems (filters: `category`, `topic`, `difficulty`, `box`, `status`) |
| GET | `/api/problems/<id>` | Problem detail with all attempts |
| GET | `/api/due` | Today's Leitner review queue |
| POST | `/api/attempts` | Log an attempt (auto-updates Leitner box) |
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/topics` | Per-topic analytics |

## Built With

- [Flask](https://flask.palletsprojects.com/) + [SQLAlchemy](https://www.sqlalchemy.org/) — backend
- [Chart.js](https://www.chartjs.org/) — visualizations
- [GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/about-copilot-cli) — AI feedback integration

