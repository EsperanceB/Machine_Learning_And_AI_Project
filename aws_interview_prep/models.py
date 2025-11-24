"""Data models for AWS Interview Prep Tool using Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class LeadershipPrinciple(str, Enum):
    """Amazon's 16 Leadership Principles."""
    CUSTOMER_OBSESSION = "Customer Obsession"
    OWNERSHIP = "Ownership"
    INVENT_AND_SIMPLIFY = "Invent and Simplify"
    ARE_RIGHT_A_LOT = "Are Right, A Lot"
    LEARN_AND_BE_CURIOUS = "Learn and Be Curious"
    HIRE_AND_DEVELOP_THE_BEST = "Hire and Develop the Best"
    INSIST_ON_HIGHEST_STANDARDS = "Insist on the Highest Standards"
    THINK_BIG = "Think Big"
    BIAS_FOR_ACTION = "Bias for Action"
    FRUGALITY = "Frugality"
    EARN_TRUST = "Earn Trust"
    DIVE_DEEP = "Dive Deep"
    HAVE_BACKBONE = "Have Backbone; Disagree and Commit"
    DELIVER_RESULTS = "Deliver Results"
    STRIVE_TO_BE_EARTHS_BEST_EMPLOYER = "Strive to be Earth's Best Employer"
    SUCCESS_AND_SCALE_BRING_BROAD_RESPONSIBILITY = "Success and Scale Bring Broad Responsibility"


class STARComponent(BaseModel):
    """STAR format component for behavioral answers."""
    situation: str = Field(default="", description="Context and background")
    task: str = Field(default="", description="What was required or the goal")
    action: str = Field(default="", description="Steps taken to address the task")
    result: str = Field(default="", description="Outcomes and impact")


class LPScore(BaseModel):
    """Leadership Principle score for an answer."""
    principle: LeadershipPrinciple
    score: int = Field(ge=1, le=5, description="Score from 1-5")
    feedback: str = Field(default="", description="Specific feedback for this LP")


class Candidate(BaseModel):
    """Candidate profile with CV and portfolio information."""
    name: str
    resume_text: str = Field(default="", description="Parsed text from CV/resume")
    portfolio_summary: str = Field(default="", description="Summary of portfolio/projects")
    skills: list[str] = Field(default_factory=list)
    experience_years: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)


class JobDescription(BaseModel):
    """Job description with parsed requirements."""
    title: str
    company: str = Field(default="Amazon")
    description: str
    requirements: list[str] = Field(default_factory=list)
    preferred_qualifications: list[str] = Field(default_factory=list)
    target_lps: list[LeadershipPrinciple] = Field(
        default_factory=list,
        description="Leadership Principles relevant to this role"
    )


class InterviewQuestion(BaseModel):
    """Interview question with LP tagging."""
    id: str
    question_text: str
    primary_lp: LeadershipPrinciple
    secondary_lps: list[LeadershipPrinciple] = Field(default_factory=list)
    difficulty: int = Field(ge=1, le=5, default=3)
    category: str = Field(default="behavioral", description="behavioral, technical, or situational")
    source: str = Field(default="generated", description="generated, database, or custom")


class CandidateAnswer(BaseModel):
    """Candidate's answer to an interview question."""
    question_id: str
    raw_answer: str
    star_format: Optional[STARComponent] = None
    lp_scores: list[LPScore] = Field(default_factory=list)
    overall_score: Optional[float] = Field(default=None, ge=1.0, le=5.0)
    feedback: str = Field(default="")
    improved_answer: str = Field(default="", description="AI-improved STAR format answer")


class SessionConfig(BaseModel):
    """Configuration for an interview session."""
    num_questions: int = Field(default=5, ge=1, le=20)
    focus_lps: list[LeadershipPrinciple] = Field(
        default_factory=list,
        description="Specific LPs to focus on"
    )
    difficulty_level: int = Field(default=3, ge=1, le=5)
    include_technical: bool = Field(default=True)
    time_limit_minutes: Optional[int] = Field(default=None, ge=1)


class InterviewSession(BaseModel):
    """Complete interview session state."""
    id: str
    candidate: Candidate
    job_description: Optional[JobDescription] = None
    config: SessionConfig = Field(default_factory=SessionConfig)
    questions: list[InterviewQuestion] = Field(default_factory=list)
    answers: list[CandidateAnswer] = Field(default_factory=list)
    current_question_index: int = Field(default=0)
    status: str = Field(default="created")  # created, in_progress, completed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def is_complete(self) -> bool:
        """Check if all questions have been answered."""
        return len(self.answers) >= len(self.questions)

    def get_current_question(self) -> Optional[InterviewQuestion]:
        """Get the current unanswered question."""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None

    def get_average_score(self) -> Optional[float]:
        """Calculate average score across all answered questions."""
        scores = [a.overall_score for a in self.answers if a.overall_score is not None]
        if scores:
            return sum(scores) / len(scores)
        return None

    def get_lp_summary(self) -> dict[str, float]:
        """Get average score per Leadership Principle."""
        lp_scores: dict[str, list[int]] = {}
        for answer in self.answers:
            for lp_score in answer.lp_scores:
                lp_name = lp_score.principle.value
                if lp_name not in lp_scores:
                    lp_scores[lp_name] = []
                lp_scores[lp_name].append(lp_score.score)

        return {lp: sum(scores) / len(scores) for lp, scores in lp_scores.items()}
