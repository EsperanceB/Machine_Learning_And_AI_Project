"""Question generation engine for AWS interview preparation."""

from __future__ import annotations

import os
import random
import uuid
from typing import Optional

from .leadership_principles import LEADERSHIP_PRINCIPLES_DB, get_example_questions
from .models import (
    Candidate,
    InterviewQuestion,
    JobDescription,
    LeadershipPrinciple,
    SessionConfig,
)


def generate_question_id() -> str:
    """Generate a unique question ID."""
    return f"q_{uuid.uuid4().hex[:8]}"


def get_lp_questions_from_db(
    lp: LeadershipPrinciple,
    count: int = 1,
) -> list[InterviewQuestion]:
    """Get pre-defined questions from the LP database."""
    example_questions = get_example_questions(lp)
    selected = random.sample(example_questions, min(count, len(example_questions)))

    return [
        InterviewQuestion(
            id=generate_question_id(),
            question_text=q,
            primary_lp=lp,
            difficulty=3,
            category="behavioral",
            source="database",
        )
        for q in selected
    ]


def generate_personalized_question(
    candidate: Optional[Candidate],
    job_description: Optional[JobDescription],
    lp: LeadershipPrinciple,
    llm_client: Optional[object] = None,
) -> InterviewQuestion:
    """Generate a personalized question based on candidate background and JD.

    If an LLM client is available, uses it to generate a contextual question.
    Otherwise, falls back to database questions with light personalization.
    """
    if llm_client is not None:
        # Use LLM to generate personalized question
        question_text = _generate_with_llm(candidate, job_description, lp, llm_client)
        source = "generated"
    else:
        # Fall back to database question with context
        db_questions = get_example_questions(lp)
        question_text = random.choice(db_questions)

        # Add context from candidate skills if available
        if candidate and candidate.skills:
            relevant_skills = candidate.skills[:3]
            skill_context = ", ".join(relevant_skills)
            # Modify question to reference candidate's background
            if "time when" in question_text.lower():
                question_text = question_text.replace(
                    "Tell me about a time",
                    f"Given your experience with {skill_context}, tell me about a time",
                )
        source = "database"

    return InterviewQuestion(
        id=generate_question_id(),
        question_text=question_text,
        primary_lp=lp,
        difficulty=3,
        category="behavioral",
        source=source,
    )


def _generate_with_llm(
    candidate: Optional[Candidate],
    job_description: Optional[JobDescription],
    lp: LeadershipPrinciple,
    llm_client: object,
) -> str:
    """Generate a question using an LLM client.

    This function expects an OpenAI-compatible client with chat.completions.create().
    """
    lp_info = LEADERSHIP_PRINCIPLES_DB[lp]

    # Build context from candidate and JD
    context_parts = [f"Leadership Principle: {lp.value}", f"Definition: {lp_info.definition}"]

    if candidate:
        context_parts.append(f"Candidate skills: {', '.join(candidate.skills[:5])}")
        if candidate.experience_years:
            context_parts.append(f"Years of experience: {candidate.experience_years}")

    if job_description:
        context_parts.append(f"Target role: {job_description.title}")
        if job_description.requirements:
            context_parts.append(f"Key requirements: {', '.join(job_description.requirements[:3])}")

    context = "\n".join(context_parts)

    prompt = f"""You are an Amazon interviewer. Generate ONE behavioral interview question 
that assesses the candidate on the {lp.value} leadership principle.

Context:
{context}

The question should:
1. Be specific and actionable
2. Allow the candidate to share a concrete example from their experience
3. Be appropriate for their background and the target role
4. Start with "Tell me about a time..." or "Describe a situation where..."

Respond with ONLY the question, no other text."""

    try:
        response = llm_client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        # Fall back to database question on API error
        return random.choice(lp_info.example_questions)


def generate_question_set(
    config: SessionConfig,
    candidate: Optional[Candidate] = None,
    job_description: Optional[JobDescription] = None,
    llm_client: Optional[object] = None,
) -> list[InterviewQuestion]:
    """Generate a complete set of interview questions based on session config.

    Args:
        config: Session configuration with number of questions and focus areas
        candidate: Optional candidate information for personalization
        job_description: Optional job description for targeting
        llm_client: Optional OpenAI-compatible client for LLM generation

    Returns:
        List of interview questions covering specified LPs
    """
    questions: list[InterviewQuestion] = []
    num_questions = config.num_questions

    # Determine which LPs to cover
    if config.focus_lps:
        target_lps = config.focus_lps
    elif job_description and job_description.target_lps:
        target_lps = job_description.target_lps
    else:
        # Default to all LPs
        target_lps = list(LeadershipPrinciple)

    # Distribute questions across LPs
    lp_count = len(target_lps)
    questions_per_lp = max(1, num_questions // lp_count)
    extra_questions = num_questions % lp_count

    # Shuffle LPs to ensure variety
    shuffled_lps = target_lps.copy()
    random.shuffle(shuffled_lps)

    for i, lp in enumerate(shuffled_lps):
        count = questions_per_lp + (1 if i < extra_questions else 0)
        for _ in range(count):
            if len(questions) >= num_questions:
                break
            question = generate_personalized_question(
                candidate, job_description, lp, llm_client
            )
            # Set difficulty based on config
            question.difficulty = config.difficulty_level
            questions.append(question)

    # Shuffle final question order
    random.shuffle(questions)
    return questions[:num_questions]


def generate_technical_question(
    skill: str,
    difficulty: int = 3,
    llm_client: Optional[object] = None,
) -> InterviewQuestion:
    """Generate a technical interview question for a specific skill."""
    if llm_client is not None:
        prompt = f"""Generate one technical interview question about {skill}.
The question should be at difficulty level {difficulty}/5.
Focus on practical application rather than trivia.
Respond with ONLY the question."""

        try:
            response = llm_client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7,
            )
            question_text = response.choices[0].message.content.strip()
        except Exception:
            question_text = f"Describe your experience with {skill} and how you've applied it in a project."
    else:
        question_text = f"Describe your experience with {skill} and how you've applied it in a project."

    return InterviewQuestion(
        id=generate_question_id(),
        question_text=question_text,
        primary_lp=LeadershipPrinciple.DIVE_DEEP,  # Technical questions map to Dive Deep
        difficulty=difficulty,
        category="technical",
        source="generated" if llm_client else "template",
    )
