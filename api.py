from flask import Blueprint, request, jsonify
from models import db, Problem, Attempt, Category, Topic
from datetime import date, timedelta
from sqlalchemy import func, case

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/problems")
def list_problems():
    query = Problem.query
    if cat := request.args.get("category"):
        query = query.join(Category).filter(Category.name == cat)
    if topic := request.args.get("topic"):
        query = query.filter(Problem.topics.any(Topic.name == topic))
    if diff := request.args.get("difficulty"):
        query = query.filter(Problem.difficulty == diff)
    if box := request.args.get("box"):
        query = query.filter(Problem.leitner_box == int(box))
    if status := request.args.get("status"):
        if status == "not_attempted":
            query = query.filter(~Problem.attempts.any())
        elif status == "mastered":
            query = query.filter(Problem.leitner_box >= 4)
        elif status == "learning":
            query = query.filter(Problem.attempts.any(), Problem.leitner_box < 4)

    problems = query.order_by(Problem.next_review_date.asc()).all()
    return jsonify([p.to_dict() for p in problems])


@api_bp.route("/problems/<int:problem_id>")
def get_problem(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    return jsonify(problem.to_dict(include_attempts=True))


@api_bp.route("/due")
def due_today():
    """Get problems due for review today (Leitner-scheduled), interleaved by topic."""
    problems = (
        Problem.query.filter(Problem.next_review_date <= date.today())
        .order_by(Problem.leitner_box.asc(), func.random())
        .all()
    )
    return jsonify([p.to_dict() for p in problems])


@api_bp.route("/attempts", methods=["POST"])
def log_attempt():
    data = request.get_json()
    problem = Problem.query.get_or_404(data["problem_id"])

    attempt = Attempt(
        problem_id=problem.id,
        passed=data.get("passed", False),
        time_taken_minutes=data.get("time_taken_minutes"),
        confidence=data.get("confidence"),
        solution_code=data.get("solution_code"),
        ai_score=data.get("ai_score"),
        ai_feedback=data.get("ai_feedback"),
        complexity_score=data.get("complexity_score"),
        notes=data.get("notes"),
    )
    db.session.add(attempt)

    problem.record_attempt(attempt.passed, attempt.confidence or 1)
    db.session.commit()

    return jsonify({
        "attempt": attempt.to_dict(),
        "leitner_update": {
            "new_box": problem.leitner_box,
            "next_review": problem.next_review_date.isoformat(),
        },
    }), 201


@api_bp.route("/stats")
def stats():
    total = Problem.query.count()
    attempted = Problem.query.filter(Problem.attempts.any()).count()
    mastered = Problem.query.filter(Problem.leitner_box >= 4).count()
    due_today_count = Problem.query.filter(Problem.next_review_date <= date.today()).count()

    attempts = Attempt.query.all()
    avg_confidence = (
        db.session.query(func.avg(Attempt.confidence)).scalar() or 0
    )
    avg_ai_score = (
        db.session.query(func.avg(Attempt.ai_score)).filter(Attempt.ai_score.isnot(None)).scalar() or 0
    )
    avg_complexity = (
        db.session.query(func.avg(Attempt.complexity_score)).filter(Attempt.complexity_score.isnot(None)).scalar() or 0
    )
    total_attempts = len(attempts)
    pass_rate = (
        sum(1 for a in attempts if a.passed) / total_attempts * 100
        if total_attempts
        else 0
    )

    # Confidence vs reality per topic
    calibration = []
    topics = Topic.query.all()
    for topic in topics:
        topic_attempts = (
            Attempt.query.join(Problem)
            .filter(Problem.topics.any(Topic.id == topic.id))
            .all()
        )
        if topic_attempts:
            t_conf = sum(a.confidence or 0 for a in topic_attempts) / len(topic_attempts)
            t_pass = sum(1 for a in topic_attempts if a.passed) / len(topic_attempts) * 100
            calibration.append({
                "topic": topic.name,
                "avg_confidence": round(t_conf, 1),
                "pass_rate": round(t_pass, 1),
                "attempt_count": len(topic_attempts),
            })

    # Box distribution
    box_dist = {}
    for box in range(1, 6):
        box_dist[str(box)] = Problem.query.filter(Problem.leitner_box == box).count()

    # Recent activity (last 10 attempts)
    recent = (
        Attempt.query.order_by(Attempt.created_at.desc()).limit(10).all()
    )

    return jsonify({
        "total_problems": total,
        "attempted": attempted,
        "mastered": mastered,
        "due_today": due_today_count,
        "total_attempts": total_attempts,
        "avg_confidence": round(float(avg_confidence), 1),
        "avg_ai_score": round(float(avg_ai_score), 1),
        "avg_complexity_score": round(float(avg_complexity), 1),
        "pass_rate": round(pass_rate, 1),
        "box_distribution": box_dist,
        "calibration": sorted(calibration, key=lambda x: x["pass_rate"]),
        "recent_activity": [
            {
                **a.to_dict(),
                "problem_name": a.problem.name,
            }
            for a in recent
        ],
    })


@api_bp.route("/topics")
def topic_analytics():
    topics = Topic.query.all()
    result = []
    for topic in topics:
        problems = topic.problems
        topic_attempts = (
            Attempt.query.join(Problem)
            .filter(Problem.topics.any(Topic.id == topic.id))
            .all()
        )
        avg_conf = (
            sum(a.confidence or 0 for a in topic_attempts) / len(topic_attempts)
            if topic_attempts
            else 0
        )
        pass_rate = (
            sum(1 for a in topic_attempts if a.passed) / len(topic_attempts) * 100
            if topic_attempts
            else 0
        )
        box_counts = {}
        for p in problems:
            box_counts[p.leitner_box] = box_counts.get(p.leitner_box, 0) + 1

        result.append({
            "topic": topic.to_dict(),
            "problem_count": len(problems),
            "attempt_count": len(topic_attempts),
            "avg_confidence": round(avg_conf, 1),
            "pass_rate": round(pass_rate, 1),
            "box_distribution": box_counts,
        })

    return jsonify(sorted(result, key=lambda x: x["pass_rate"]))


@api_bp.route("/calendar")
def calendar():
    """Daily attempt counts. Minimum 3 months lookback, expands to cover all history."""
    today = date.today()
    min_start = today - timedelta(days=90)

    earliest_attempt = db.session.query(func.min(func.date(Attempt.created_at))).scalar()
    if earliest_attempt:
        earliest = date.fromisoformat(str(earliest_attempt))
        start = min(earliest, min_start)
    else:
        start = min_start

    # Align start to previous Monday for clean grid
    while start.weekday() != 0:
        start -= timedelta(days=1)

    rows = (
        db.session.query(
            func.date(Attempt.created_at).label("day"),
            func.count().label("count"),
        )
        .filter(Attempt.created_at >= start.isoformat())
        .group_by(func.date(Attempt.created_at))
        .all()
    )
    counts = {str(r.day): r.count for r in rows}

    result = []
    d = start
    while d <= today:
        ds = d.isoformat()
        result.append({"date": ds, "count": counts.get(ds, 0)})
        d += timedelta(days=1)

    return jsonify(result)
