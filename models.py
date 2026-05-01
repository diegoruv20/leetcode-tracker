from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta, timezone
import time

db = SQLAlchemy()

LEITNER_INTERVALS = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    problems = db.relationship("Problem", backref="category", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Topic(db.Model):
    __tablename__ = "topics"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


ProblemTopic = db.Table(
    "problem_topics",
    db.Column("problem_id", db.Integer, db.ForeignKey("problems.id"), primary_key=True),
    db.Column("topic_id", db.Integer, db.ForeignKey("topics.id"), primary_key=True),
)


class Problem(db.Model):
    __tablename__ = "problems"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500))
    difficulty = db.Column(db.String(10))  # Easy, Medium, Hard
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    leitner_box = db.Column(db.Integer, default=1)
    next_review_date = db.Column(db.Date, default=date.today)
    last_reviewed_at = db.Column(db.DateTime)

    topics = db.relationship("Topic", secondary=ProblemTopic, backref="problems")
    attempts = db.relationship(
        "Attempt", backref="problem", lazy=True, order_by="Attempt.created_at.desc()"
    )

    @property
    def status(self):
        if not self.attempts:
            return "not_attempted"
        if self.leitner_box >= 4:
            return "mastered"
        return "learning"

    @property
    def latest_attempt(self):
        return self.attempts[0] if self.attempts else None

    def record_attempt(self, passed, confidence):
        """Update Leitner box based on attempt result."""
        if passed and confidence >= 3:
            self.leitner_box = min(self.leitner_box + 1, 5)
        else:
            self.leitner_box = 1
        interval = LEITNER_INTERVALS[self.leitner_box]
        self.next_review_date = date.today() + timedelta(days=interval)
        self.last_reviewed_at = datetime.now()

    def to_dict(self, include_attempts=False):
        d = {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "difficulty": self.difficulty,
            "category": self.category.to_dict() if self.category else None,
            "topics": [t.to_dict() for t in self.topics],
            "leitner_box": self.leitner_box,
            "next_review_date": self.next_review_date.isoformat() if self.next_review_date else None,
            "last_reviewed_at": self.last_reviewed_at.isoformat() if self.last_reviewed_at else None,
            "status": self.status,
            "attempt_count": len(self.attempts),
        }
        if include_attempts:
            d["attempts"] = [a.to_dict() for a in self.attempts]
        return d


class Attempt(db.Model):
    __tablename__ = "attempts"
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey("problems.id"), nullable=False)
    passed = db.Column(db.Boolean, default=False)
    time_taken_minutes = db.Column(db.Integer)
    confidence = db.Column(db.Integer)  # 1-5
    solution_code = db.Column(db.Text)
    ai_score = db.Column(db.Integer)  # 1-10
    ai_feedback = db.Column(db.Text)
    complexity_score = db.Column(db.Integer)  # 1-5: how well they identified time/space complexity
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "problem_id": self.problem_id,
            "passed": self.passed,
            "time_taken_minutes": self.time_taken_minutes,
            "confidence": self.confidence,
            "solution_code": self.solution_code,
            "ai_score": self.ai_score,
            "ai_feedback": self.ai_feedback,
            "complexity_score": self.complexity_score,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
