"""Answer evaluation service with STAR format analysis and LP scoring."""

from __future__ import annotations

import os
import re
from typing import Optional

from .leadership_principles import LEADERSHIP_PRINCIPLES_DB, get_rubric
from .models import (
    CandidateAnswer,
    InterviewQuestion,
    LeadershipPrinciple,
    LPScore,
    STARComponent,
)


def extract_star_components(answer_text: str) -> STARComponent:
    """Extract STAR components from an answer using keyword detection.

    Looks for explicit STAR markers or infers components from structure.
    """
    text = answer_text.strip()

    # Try to find explicit STAR markers
    situation_match = re.search(
        r"(?:situation|context|background)[:\s]*(.*?)(?=task|action|result|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    task_match = re.search(
        r"(?:task|goal|objective|challenge)[:\s]*(.*?)(?=action|result|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    action_match = re.search(
        r"(?:action|approach|steps?|what i did)[:\s]*(.*?)(?=result|outcome|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    result_match = re.search(
        r"(?:result|outcome|impact|conclusion)[:\s]*(.*?)$",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    # If explicit markers found, extract them
    if any([situation_match, task_match, action_match, result_match]):
        return STARComponent(
            situation=situation_match.group(1).strip() if situation_match else "",
            task=task_match.group(1).strip() if task_match else "",
            action=action_match.group(1).strip() if action_match else "",
            result=result_match.group(1).strip() if result_match else "",
        )

    # Fall back to sentence-based splitting
    sentences = re.split(r"(?<=[.!?])\s+", text)
    num_sentences = len(sentences)

    if num_sentences >= 4:
        # Distribute sentences across STAR components
        quarter = num_sentences // 4
        return STARComponent(
            situation=" ".join(sentences[:quarter]),
            task=" ".join(sentences[quarter : quarter * 2]),
            action=" ".join(sentences[quarter * 2 : quarter * 3]),
            result=" ".join(sentences[quarter * 3 :]),
        )

    # For very short answers, put everything in situation
    return STARComponent(
        situation=text,
        task="",
        action="",
        result="",
    )


def score_answer_basic(
    answer_text: str,
    question: InterviewQuestion,
) -> tuple[list[LPScore], float]:
    """Score an answer using basic heuristics without LLM.

    Returns LP scores and overall score (1-5).
    """
    lp = question.primary_lp
    lp_info = LEADERSHIP_PRINCIPLES_DB[lp]
    rubric = lp_info.rubric

    # Basic scoring heuristics
    text_lower = answer_text.lower()
    score = 3  # Default to average

    # Check for presence of STAR components
    star = extract_star_components(answer_text)
    star_completeness = sum(
        1 for component in [star.situation, star.task, star.action, star.result] if component
    )

    # Adjust score based on STAR completeness
    if star_completeness == 4:
        score += 1
    elif star_completeness <= 1:
        score -= 1

    # Check for specificity (numbers, metrics, names)
    specificity_indicators = [
        r"\d+%",  # Percentages
        r"\$\d+",  # Dollar amounts
        r"\d+\s*(?:people|team|members|users|customers)",  # Team/user sizes
        r"\d+\s*(?:weeks?|months?|days?|hours?)",  # Time durations
    ]
    specificity_count = sum(
        1 for pattern in specificity_indicators if re.search(pattern, text_lower)
    )
    if specificity_count >= 2:
        score += 1

    # Check for behavioral indicators related to the LP
    indicator_matches = sum(
        1
        for indicator in lp_info.behavioral_indicators
        if indicator.lower() in text_lower
    )
    if indicator_matches >= 2:
        score += 0.5

    # Clamp score to valid range
    final_score = max(1, min(5, round(score)))

    # Generate feedback based on score
    feedback = rubric.get(final_score, "")

    lp_scores = [
        LPScore(principle=lp, score=final_score, feedback=feedback)
    ]

    # Add secondary LP scores if present
    for secondary_lp in question.secondary_lps[:2]:
        secondary_score = max(1, min(5, final_score + random.choice([-1, 0, 1])))
        lp_scores.append(
            LPScore(
                principle=secondary_lp,
                score=secondary_score,
                feedback=LEADERSHIP_PRINCIPLES_DB[secondary_lp].rubric.get(secondary_score, ""),
            )
        )

    return lp_scores, float(final_score)


import random


def evaluate_answer_with_llm(
    answer_text: str,
    question: InterviewQuestion,
    llm_client: object,
) -> tuple[list[LPScore], float, str, str]:
    """Evaluate an answer using an LLM.

    Returns:
        Tuple of (LP scores, overall score, feedback, improved STAR answer)
    """
    lp = question.primary_lp
    lp_info = LEADERSHIP_PRINCIPLES_DB[lp]

    prompt = f"""You are an Amazon interviewer evaluating a candidate's answer.

Question: {question.question_text}

Leadership Principle being assessed: {lp.value}
Definition: {lp_info.definition}

Behavioral Indicators:
{chr(10).join(f"- {indicator}" for indicator in lp_info.behavioral_indicators)}

Scoring Rubric:
1 - {lp_info.rubric[1]}
2 - {lp_info.rubric[2]}
3 - {lp_info.rubric[3]}
4 - {lp_info.rubric[4]}
5 - {lp_info.rubric[5]}

Candidate's Answer:
{answer_text}

Please provide:
1. SCORE: A score from 1-5 based on the rubric
2. FEEDBACK: Specific, constructive feedback (2-3 sentences)
3. IMPROVED_ANSWER: Rewrite the answer in proper STAR format, enhancing it while maintaining the candidate's original content

Format your response exactly as:
SCORE: [number]
FEEDBACK: [your feedback]
IMPROVED_ANSWER:
SITUATION: [situation]
TASK: [task]
ACTION: [action]
RESULT: [result]"""

    try:
        response = llm_client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3,
        )
        response_text = response.choices[0].message.content

        # Parse the response
        score_match = re.search(r"SCORE:\s*(\d)", response_text)
        feedback_match = re.search(
            r"FEEDBACK:\s*(.*?)(?=IMPROVED_ANSWER|$)", response_text, re.DOTALL
        )
        improved_match = re.search(r"IMPROVED_ANSWER:\s*(.*?)$", response_text, re.DOTALL)

        score = int(score_match.group(1)) if score_match else 3
        score = max(1, min(5, score))

        feedback = feedback_match.group(1).strip() if feedback_match else ""
        improved_answer = improved_match.group(1).strip() if improved_match else ""

        lp_scores = [LPScore(principle=lp, score=score, feedback=feedback)]

        return lp_scores, float(score), feedback, improved_answer

    except Exception as e:
        # Fall back to basic scoring on error
        lp_scores, overall_score = score_answer_basic(answer_text, question)
        return lp_scores, overall_score, f"Evaluation error: {e}", ""


def evaluate_answer(
    answer_text: str,
    question: InterviewQuestion,
    llm_client: Optional[object] = None,
) -> CandidateAnswer:
    """Evaluate a candidate's answer and return a complete evaluation.

    Args:
        answer_text: The candidate's raw answer text
        question: The question being answered
        llm_client: Optional OpenAI-compatible client for LLM evaluation

    Returns:
        CandidateAnswer with scores, feedback, and improved STAR format
    """
    star_format = extract_star_components(answer_text)

    if llm_client is not None:
        lp_scores, overall_score, feedback, improved_answer = evaluate_answer_with_llm(
            answer_text, question, llm_client
        )
    else:
        lp_scores, overall_score = score_answer_basic(answer_text, question)
        feedback = generate_basic_feedback(answer_text, star_format, lp_scores[0])
        improved_answer = generate_star_template(answer_text, question)

    return CandidateAnswer(
        question_id=question.id,
        raw_answer=answer_text,
        star_format=star_format,
        lp_scores=lp_scores,
        overall_score=overall_score,
        feedback=feedback,
        improved_answer=improved_answer,
    )


def generate_basic_feedback(
    answer_text: str,
    star: STARComponent,
    lp_score: LPScore,
) -> str:
    """Generate basic feedback without LLM."""
    feedback_parts = []

    # STAR completeness feedback
    missing_components = []
    if not star.situation:
        missing_components.append("Situation")
    if not star.task:
        missing_components.append("Task")
    if not star.action:
        missing_components.append("Action")
    if not star.result:
        missing_components.append("Result")

    if missing_components:
        feedback_parts.append(
            f"Consider adding more detail to: {', '.join(missing_components)}."
        )
    else:
        feedback_parts.append("Good use of the STAR format.")

    # Length feedback
    word_count = len(answer_text.split())
    if word_count < 100:
        feedback_parts.append(
            "Your answer could be more detailed. Aim for 150-250 words."
        )
    elif word_count > 400:
        feedback_parts.append(
            "Consider being more concise. Aim for 150-250 words."
        )

    # LP-specific feedback
    feedback_parts.append(lp_score.feedback)

    return " ".join(feedback_parts)


def generate_star_template(answer_text: str, question: InterviewQuestion) -> str:
    """Generate a STAR format template for improving the answer."""
    lp = question.primary_lp

    template = f"""Here's a suggested STAR format structure for your answer:

**SITUATION:** (Set the scene - when, where, what was the context?)
[Describe the background and circumstances]

**TASK:** (What was your specific responsibility or goal?)
[Explain what you needed to accomplish]

**ACTION:** (What steps did YOU take? Use "I" not "we")
[Detail the specific actions you took, focusing on your individual contribution]

**RESULT:** (What was the outcome? Include metrics if possible)
[Quantify the impact: percentages, time saved, revenue generated, etc.]

This question is assessing {lp.value}: Focus on demonstrating behaviors like:
- {chr(10).join(f'- {ind}' for ind in LEADERSHIP_PRINCIPLES_DB[lp].behavioral_indicators[:3])}
"""
    return template
