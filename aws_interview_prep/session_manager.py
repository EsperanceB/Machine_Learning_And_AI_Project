"""Interview session management service."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from .answer_evaluator import evaluate_answer
from .document_ingestion import parse_job_description, parse_resume
from .models import (
    Candidate,
    CandidateAnswer,
    InterviewQuestion,
    InterviewSession,
    JobDescription,
    LeadershipPrinciple,
    SessionConfig,
)
from .question_generator import generate_question_set


def create_session_id() -> str:
    """Generate a unique session ID."""
    return f"session_{uuid.uuid4().hex[:12]}"


class InterviewSessionManager:
    """Manages interview sessions including creation, question delivery, and evaluation."""

    def __init__(self, llm_client: Optional[object] = None) -> None:
        """Initialize the session manager.

        Args:
            llm_client: Optional OpenAI-compatible client for LLM features
        """
        self.llm_client = llm_client
        self.sessions: dict[str, InterviewSession] = {}

    def create_session(
        self,
        candidate_name: str,
        resume_text: str = "",
        portfolio_summary: str = "",
        job_description_text: str = "",
        job_title: str = "Software Development Engineer",
        num_questions: int = 5,
        focus_lps: Optional[list[LeadershipPrinciple]] = None,
        difficulty_level: int = 3,
    ) -> InterviewSession:
        """Create a new interview session.

        Args:
            candidate_name: Name of the candidate
            resume_text: Raw text from candidate's resume
            portfolio_summary: Summary of candidate's portfolio/projects
            job_description_text: Raw text of job description
            job_title: Title of the target position
            num_questions: Number of questions to generate
            focus_lps: Specific Leadership Principles to focus on
            difficulty_level: Question difficulty (1-5)

        Returns:
            Configured InterviewSession ready to start
        """
        # Parse candidate information
        candidate = parse_resume(resume_text, candidate_name)
        if portfolio_summary:
            candidate.portfolio_summary = portfolio_summary

        # Parse job description
        job_description = None
        if job_description_text:
            job_description = parse_job_description(
                job_description_text, title=job_title
            )

        # Create session config
        config = SessionConfig(
            num_questions=num_questions,
            focus_lps=focus_lps or [],
            difficulty_level=difficulty_level,
        )

        # Generate questions
        questions = generate_question_set(
            config=config,
            candidate=candidate,
            job_description=job_description,
            llm_client=self.llm_client,
        )

        # Create session
        session = InterviewSession(
            id=create_session_id(),
            candidate=candidate,
            job_description=job_description,
            config=config,
            questions=questions,
            status="created",
        )

        self.sessions[session.id] = session
        return session

    def start_session(self, session_id: str) -> InterviewSession:
        """Start an interview session.

        Args:
            session_id: ID of the session to start

        Returns:
            Updated session with 'in_progress' status

        Raises:
            ValueError: If session not found
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        session.status = "in_progress"
        session.started_at = datetime.now()
        return session

    def get_current_question(self, session_id: str) -> Optional[InterviewQuestion]:
        """Get the current unanswered question for a session.

        Args:
            session_id: ID of the session

        Returns:
            Current question or None if session complete

        Raises:
            ValueError: If session not found
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        return self.sessions[session_id].get_current_question()

    def submit_answer(
        self,
        session_id: str,
        answer_text: str,
    ) -> CandidateAnswer:
        """Submit an answer to the current question and get evaluation.

        Args:
            session_id: ID of the session
            answer_text: Candidate's answer text

        Returns:
            Evaluated CandidateAnswer with scores and feedback

        Raises:
            ValueError: If session not found or no current question
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        question = session.get_current_question()

        if question is None:
            raise ValueError("No more questions in this session")

        # Evaluate the answer
        evaluation = evaluate_answer(
            answer_text=answer_text,
            question=question,
            llm_client=self.llm_client,
        )

        # Record the answer
        session.answers.append(evaluation)
        session.current_question_index += 1

        # Check if session is complete
        if session.is_complete():
            session.status = "completed"
            session.completed_at = datetime.now()

        return evaluation

    def get_session_summary(self, session_id: str) -> dict:
        """Get a summary of the session including scores and feedback.

        Args:
            session_id: ID of the session

        Returns:
            Dictionary with session summary data

        Raises:
            ValueError: If session not found
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        return {
            "session_id": session.id,
            "candidate_name": session.candidate.name,
            "status": session.status,
            "questions_total": len(session.questions),
            "questions_answered": len(session.answers),
            "average_score": session.get_average_score(),
            "lp_summary": session.get_lp_summary(),
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "answers": [
                {
                    "question": next(
                        (q.question_text for q in session.questions if q.id == a.question_id),
                        "Unknown",
                    ),
                    "score": a.overall_score,
                    "feedback": a.feedback,
                }
                for a in session.answers
            ],
        }

    def get_session(self, session_id: str) -> InterviewSession:
        """Get a session by ID.

        Args:
            session_id: ID of the session

        Returns:
            The InterviewSession

        Raises:
            ValueError: If session not found
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        return self.sessions[session_id]

    def list_sessions(self) -> list[dict]:
        """List all sessions with basic info.

        Returns:
            List of session summary dictionaries
        """
        return [
            {
                "id": s.id,
                "candidate": s.candidate.name,
                "status": s.status,
                "questions": len(s.questions),
                "answered": len(s.answers),
            }
            for s in self.sessions.values()
        ]
