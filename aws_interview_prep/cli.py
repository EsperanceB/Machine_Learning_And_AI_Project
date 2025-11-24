#!/usr/bin/env python3
"""Command-line interface for AWS Interview Prep Tool.

This CLI provides an interactive interview session with:
- Session configuration (number of questions, focus areas)
- Interactive Q&A with immediate feedback
- STAR format improvement suggestions
- Session summary with LP scores
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from .models import LeadershipPrinciple
from .session_manager import InterviewSessionManager


def get_llm_client() -> Optional[object]:
    """Initialize OpenAI client if API key is available."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        return OpenAI(api_key=api_key)
    except ImportError:
        print("Note: Install 'openai' package for AI-powered features.")
        return None


def print_separator() -> None:
    """Print a visual separator."""
    print("\n" + "=" * 60 + "\n")


def print_question(question_num: int, total: int, question_text: str, lp: str) -> None:
    """Print a formatted question."""
    print(f"\n📋 Question {question_num}/{total}")
    print(f"Leadership Principle: {lp}")
    print("-" * 40)
    print(f"\n{question_text}\n")


def print_feedback(evaluation) -> None:
    """Print formatted feedback for an answer."""
    print("\n" + "-" * 40)
    print("📊 Evaluation")
    print("-" * 40)

    # Overall score
    score = evaluation.overall_score or 0
    stars = "⭐" * int(score) + "☆" * (5 - int(score))
    print(f"\nOverall Score: {score:.1f}/5 {stars}")

    # LP Scores
    if evaluation.lp_scores:
        print("\nLeadership Principle Scores:")
        for lp_score in evaluation.lp_scores:
            lp_stars = "⭐" * lp_score.score + "☆" * (5 - lp_score.score)
            print(f"  • {lp_score.principle.value}: {lp_score.score}/5 {lp_stars}")

    # Feedback
    if evaluation.feedback:
        print(f"\n💡 Feedback:\n{evaluation.feedback}")

    # STAR format suggestion
    if evaluation.improved_answer:
        print("\n📝 Improved STAR Format Answer:")
        print("-" * 40)
        print(evaluation.improved_answer)


def print_session_summary(summary: dict) -> None:
    """Print formatted session summary."""
    print_separator()
    print("🏆 Session Summary")
    print("=" * 60)

    print(f"\nCandidate: {summary['candidate_name']}")
    print(f"Questions Answered: {summary['questions_answered']}/{summary['questions_total']}")

    if summary["average_score"]:
        avg = summary["average_score"]
        stars = "⭐" * int(round(avg)) + "☆" * (5 - int(round(avg)))
        print(f"Average Score: {avg:.2f}/5 {stars}")

    if summary["lp_summary"]:
        print("\nLeadership Principle Performance:")
        for lp, score in sorted(
            summary["lp_summary"].items(), key=lambda x: x[1], reverse=True
        ):
            lp_stars = "⭐" * int(round(score)) + "☆" * (5 - int(round(score)))
            print(f"  • {lp}: {score:.1f}/5 {lp_stars}")

    print("\n" + "=" * 60)


def get_multiline_input(prompt: str) -> str:
    """Get multi-line input from user."""
    print(prompt)
    print("(Enter your answer. Type 'DONE' on a new line when finished)")
    print("-" * 40)

    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "DONE":
                break
            lines.append(line)
        except EOFError:
            break

    return "\n".join(lines)


def run_interactive_session(
    manager: InterviewSessionManager,
    candidate_name: str,
    resume_text: str,
    job_description: str,
    num_questions: int,
    focus_lps: list[LeadershipPrinciple],
) -> None:
    """Run an interactive interview session."""
    print_separator()
    print("🎯 AWS Interview Prep Tool")
    print("=" * 60)
    print(f"\nWelcome, {candidate_name}!")
    print(f"This session will have {num_questions} questions.")

    if focus_lps:
        print("Focus areas: " + ", ".join(lp.value for lp in focus_lps))

    # Create and start session
    session = manager.create_session(
        candidate_name=candidate_name,
        resume_text=resume_text,
        job_description_text=job_description,
        num_questions=num_questions,
        focus_lps=focus_lps,
    )

    manager.start_session(session.id)

    print("\nSession created! Let's begin.\n")
    print("Tips for answering:")
    print("• Use the STAR format (Situation, Task, Action, Result)")
    print("• Be specific with examples and metrics")
    print("• Focus on YOUR individual contributions")
    print_separator()

    # Question loop
    question_num = 0
    while True:
        question = manager.get_current_question(session.id)
        if question is None:
            break

        question_num += 1
        print_question(
            question_num,
            len(session.questions),
            question.question_text,
            question.primary_lp.value,
        )

        # Get answer
        answer = get_multiline_input("\nYour answer:")

        if not answer.strip():
            print("⚠️  Empty answer skipped.")
            continue

        # Evaluate and show feedback
        evaluation = manager.submit_answer(session.id, answer)
        print_feedback(evaluation)

        # Check if more questions
        if manager.get_current_question(session.id):
            input("\nPress Enter for next question...")

    # Show summary
    summary = manager.get_session_summary(session.id)
    print_session_summary(summary)

    print("\n🎉 Interview session complete!")
    print("Thank you for practicing with AWS Interview Prep Tool.\n")


def parse_lp_list(lp_string: str) -> list[LeadershipPrinciple]:
    """Parse comma-separated LP names into LeadershipPrinciple enums."""
    if not lp_string:
        return []

    lp_map = {lp.value.lower().replace(" ", "_"): lp for lp in LeadershipPrinciple}

    result = []
    for name in lp_string.split(","):
        clean_name = name.strip().lower().replace(" ", "_")
        if clean_name in lp_map:
            result.append(lp_map[clean_name])
        else:
            # Try partial match
            for key, lp in lp_map.items():
                if clean_name in key:
                    result.append(lp)
                    break

    return result


def main() -> None:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="AWS Interview Prep Tool - Practice behavioral interviews with LP feedback",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m aws_interview_prep.cli --name "John Doe" --questions 5
  python -m aws_interview_prep.cli --name "Jane" --resume resume.txt --jd job.txt
  python -m aws_interview_prep.cli --name "Test" --focus "ownership,customer_obsession"

Environment Variables:
  OPENAI_API_KEY    Set this for AI-powered question generation and feedback
        """,
    )

    parser.add_argument(
        "--name",
        "-n",
        default="Candidate",
        help="Your name (default: Candidate)",
    )
    parser.add_argument(
        "--resume",
        "-r",
        type=str,
        help="Path to resume/CV text file",
    )
    parser.add_argument(
        "--jd",
        "-j",
        type=str,
        help="Path to job description text file",
    )
    parser.add_argument(
        "--questions",
        "-q",
        type=int,
        default=5,
        help="Number of questions (default: 5, max: 20)",
    )
    parser.add_argument(
        "--focus",
        "-f",
        type=str,
        default="",
        help="Comma-separated Leadership Principles to focus on",
    )
    parser.add_argument(
        "--list-lps",
        action="store_true",
        help="List all Leadership Principles and exit",
    )

    args = parser.parse_args()

    # Handle --list-lps
    if args.list_lps:
        print("\nAmazon Leadership Principles:")
        print("-" * 40)
        for i, lp in enumerate(LeadershipPrinciple, 1):
            print(f"{i:2}. {lp.value}")
        print()
        sys.exit(0)

    # Validate questions
    num_questions = max(1, min(20, args.questions))

    # Load resume if provided
    resume_text = ""
    if args.resume:
        try:
            with open(args.resume, "r", encoding="utf-8") as f:
                resume_text = f.read()
            print(f"✓ Loaded resume from {args.resume}")
        except FileNotFoundError:
            print(f"⚠️  Resume file not found: {args.resume}")

    # Load JD if provided
    job_description = ""
    if args.jd:
        try:
            with open(args.jd, "r", encoding="utf-8") as f:
                job_description = f.read()
            print(f"✓ Loaded job description from {args.jd}")
        except FileNotFoundError:
            print(f"⚠️  Job description file not found: {args.jd}")

    # Parse focus LPs
    focus_lps = parse_lp_list(args.focus)

    # Initialize manager
    llm_client = get_llm_client()
    if llm_client:
        print("✓ OpenAI API connected - AI features enabled")
    else:
        print("ℹ️  Running without OpenAI - using basic features")

    manager = InterviewSessionManager(llm_client=llm_client)

    # Run session
    try:
        run_interactive_session(
            manager=manager,
            candidate_name=args.name,
            resume_text=resume_text,
            job_description=job_description,
            num_questions=num_questions,
            focus_lps=focus_lps,
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Session interrupted. Goodbye!")
        sys.exit(1)


if __name__ == "__main__":
    main()
