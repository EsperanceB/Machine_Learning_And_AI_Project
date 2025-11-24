#!/usr/bin/env python3
"""Streamlit web interface for AWS Interview Prep Tool.

Run with: streamlit run aws_interview_prep/streamlit_app.py
"""

from __future__ import annotations

import os
from typing import Optional

import streamlit as st

from .leadership_principles import LEADERSHIP_PRINCIPLES_DB, get_all_lp_definitions
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
        return None


def initialize_session_state() -> None:
    """Initialize Streamlit session state."""
    if "manager" not in st.session_state:
        llm_client = get_llm_client()
        st.session_state.manager = InterviewSessionManager(llm_client=llm_client)
        st.session_state.has_llm = llm_client is not None

    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None

    if "page" not in st.session_state:
        st.session_state.page = "setup"


def render_setup_page() -> None:
    """Render the session setup page."""
    st.title("🎯 AWS Interview Prep Tool")
    st.markdown(
        """
    Practice behavioral interviews with Amazon Leadership Principles feedback.

    This tool will:
    - Generate personalized interview questions based on your background
    - Evaluate your answers against Leadership Principles
    - Provide STAR format improvement suggestions
    - Track your LP performance across questions
    """
    )

    if st.session_state.has_llm:
        st.success("✓ OpenAI API connected - AI features enabled")
    else:
        st.info("ℹ️ Set OPENAI_API_KEY environment variable for AI-powered features")

    st.header("Session Configuration")

    col1, col2 = st.columns(2)

    with col1:
        candidate_name = st.text_input("Your Name", value="Candidate")
        num_questions = st.slider("Number of Questions", 1, 20, 5)
        difficulty = st.slider("Difficulty Level", 1, 5, 3)

    with col2:
        # LP multi-select
        lp_options = [lp.value for lp in LeadershipPrinciple]
        selected_lps = st.multiselect(
            "Focus Leadership Principles (optional)",
            lp_options,
            help="Leave empty to cover all LPs",
        )

    st.header("Your Background (Optional)")

    resume_text = st.text_area(
        "Resume/CV Text",
        height=150,
        placeholder="Paste your resume text here for personalized questions...",
    )

    portfolio_summary = st.text_area(
        "Portfolio/Projects Summary",
        height=100,
        placeholder="Describe key projects you've worked on...",
    )

    st.header("Target Role (Optional)")

    job_title = st.text_input("Job Title", value="Software Development Engineer")

    job_description = st.text_area(
        "Job Description",
        height=150,
        placeholder="Paste the job description here...",
    )

    if st.button("🚀 Start Interview Session", type="primary"):
        # Convert LP names to enums
        focus_lps = [
            lp for lp in LeadershipPrinciple if lp.value in selected_lps
        ]

        # Create session
        session = st.session_state.manager.create_session(
            candidate_name=candidate_name,
            resume_text=resume_text,
            portfolio_summary=portfolio_summary,
            job_description_text=job_description,
            job_title=job_title,
            num_questions=num_questions,
            focus_lps=focus_lps,
            difficulty_level=difficulty,
        )

        st.session_state.manager.start_session(session.id)
        st.session_state.current_session_id = session.id
        st.session_state.page = "interview"
        st.rerun()


def render_interview_page() -> None:
    """Render the interview Q&A page."""
    session_id = st.session_state.current_session_id
    manager = st.session_state.manager

    try:
        session = manager.get_session(session_id)
    except ValueError:
        st.error("Session not found. Please start a new session.")
        st.session_state.page = "setup"
        st.rerun()
        return

    # Header with progress
    st.title("🎯 AWS Interview Session")

    progress = len(session.answers) / len(session.questions)
    st.progress(progress, text=f"Question {len(session.answers) + 1} of {len(session.questions)}")

    # Get current question
    question = manager.get_current_question(session_id)

    if question is None:
        st.session_state.page = "results"
        st.rerun()
        return

    # Display question
    st.subheader(f"Leadership Principle: {question.primary_lp.value}")

    # Show LP definition in expander
    with st.expander("📚 About this Leadership Principle"):
        lp_info = LEADERSHIP_PRINCIPLES_DB[question.primary_lp]
        st.markdown(f"**Definition:** {lp_info.definition}")
        st.markdown("**Behavioral Indicators:**")
        for indicator in lp_info.behavioral_indicators:
            st.markdown(f"- {indicator}")

    st.markdown("---")
    st.markdown(f"### ❓ {question.question_text}")
    st.markdown("---")

    # STAR format tips
    with st.expander("💡 Tips for answering"):
        st.markdown(
            """
        **Use the STAR Format:**
        - **S**ituation: Set the context for your story
        - **T**ask: Describe your specific responsibility
        - **A**ction: Explain the steps YOU took
        - **R**esult: Share the outcome with metrics if possible

        **Best Practices:**
        - Be specific with examples
        - Use "I" not "we" to highlight your contributions
        - Include numbers and metrics when possible
        - Keep your answer to 2-3 minutes when spoken
        """
        )

    # Answer input
    answer_key = f"answer_{question.id}"
    answer = st.text_area(
        "Your Answer",
        height=200,
        key=answer_key,
        placeholder="Type your answer here using the STAR format...",
    )

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("⏭️ Skip Question"):
            # Submit empty answer
            manager.submit_answer(session_id, "(Skipped)")
            st.rerun()

    with col2:
        if st.button("✅ Submit Answer", type="primary", disabled=not answer.strip()):
            evaluation = manager.submit_answer(session_id, answer)

            # Show evaluation in a nice format
            st.markdown("---")
            st.subheader("📊 Evaluation")

            # Score display
            score = evaluation.overall_score or 0
            stars = "⭐" * int(score) + "☆" * (5 - int(score))
            st.markdown(f"### Score: {score:.1f}/5 {stars}")

            # LP Scores
            if evaluation.lp_scores:
                st.markdown("**Leadership Principle Scores:**")
                for lp_score in evaluation.lp_scores:
                    lp_stars = "⭐" * lp_score.score + "☆" * (5 - lp_score.score)
                    st.markdown(f"- {lp_score.principle.value}: {lp_score.score}/5 {lp_stars}")

            # Feedback
            if evaluation.feedback:
                st.markdown("**Feedback:**")
                st.info(evaluation.feedback)

            # Improved answer
            if evaluation.improved_answer:
                with st.expander("📝 Improved STAR Format Answer"):
                    st.markdown(evaluation.improved_answer)

            st.markdown("---")

            if manager.get_current_question(session_id):
                if st.button("➡️ Next Question"):
                    st.rerun()
            else:
                if st.button("📊 View Results"):
                    st.session_state.page = "results"
                    st.rerun()


def render_results_page() -> None:
    """Render the session results page."""
    session_id = st.session_state.current_session_id
    manager = st.session_state.manager

    try:
        summary = manager.get_session_summary(session_id)
    except ValueError:
        st.error("Session not found.")
        st.session_state.page = "setup"
        st.rerun()
        return

    st.title("🏆 Session Results")

    # Overall stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Questions Answered", f"{summary['questions_answered']}/{summary['questions_total']}")

    with col2:
        avg_score = summary["average_score"] or 0
        st.metric("Average Score", f"{avg_score:.2f}/5")

    with col3:
        if summary["lp_summary"]:
            best_lp = max(summary["lp_summary"].items(), key=lambda x: x[1])
            st.metric("Strongest LP", best_lp[0][:20] + "...")

    st.markdown("---")

    # LP Performance chart
    if summary["lp_summary"]:
        st.subheader("Leadership Principle Performance")

        # Create a simple bar visualization
        for lp, score in sorted(
            summary["lp_summary"].items(), key=lambda x: x[1], reverse=True
        ):
            st.markdown(f"**{lp}**")
            st.progress(score / 5, text=f"{score:.1f}/5")

    st.markdown("---")

    # Individual question results
    st.subheader("Question-by-Question Results")

    for i, answer in enumerate(summary["answers"], 1):
        with st.expander(f"Question {i}: {answer['question'][:50]}..."):
            score = answer["score"] or 0
            stars = "⭐" * int(score) + "☆" * (5 - int(score))
            st.markdown(f"**Score:** {score:.1f}/5 {stars}")
            if answer["feedback"]:
                st.markdown(f"**Feedback:** {answer['feedback']}")

    st.markdown("---")

    # Actions
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Start New Session"):
            st.session_state.current_session_id = None
            st.session_state.page = "setup"
            st.rerun()

    with col2:
        if st.button("📚 Learn About Leadership Principles"):
            st.session_state.page = "learn"
            st.rerun()


def render_learn_page() -> None:
    """Render the LP learning page."""
    st.title("📚 Amazon Leadership Principles")

    st.markdown(
        """
    Amazon's 16 Leadership Principles guide decision-making and behavior at all levels.
    Understanding these principles is essential for AWS/Amazon interviews.
    """
    )

    # LP selector
    lp_options = {lp.value: lp for lp in LeadershipPrinciple}
    selected_lp_name = st.selectbox("Select a Leadership Principle", list(lp_options.keys()))

    if selected_lp_name:
        lp = lp_options[selected_lp_name]
        lp_info = LEADERSHIP_PRINCIPLES_DB[lp]

        st.markdown("---")
        st.header(lp.value)

        st.markdown(f"**Definition:** {lp_info.definition}")

        st.subheader("Behavioral Indicators")
        for indicator in lp_info.behavioral_indicators:
            st.markdown(f"- {indicator}")

        st.subheader("Sample Interview Questions")
        for q in lp_info.example_questions:
            st.markdown(f"- {q}")

        st.subheader("Scoring Rubric")
        for score, desc in lp_info.rubric.items():
            st.markdown(f"**{score}/5:** {desc}")

    st.markdown("---")
    if st.button("⬅️ Back to Results"):
        st.session_state.page = "results"
        st.rerun()


def main() -> None:
    """Main entry point for Streamlit app."""
    st.set_page_config(
        page_title="AWS Interview Prep",
        page_icon="🎯",
        layout="wide",
    )

    initialize_session_state()

    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")

        if st.button("🏠 New Session"):
            st.session_state.current_session_id = None
            st.session_state.page = "setup"
            st.rerun()

        if st.button("📚 Leadership Principles"):
            st.session_state.page = "learn"
            st.rerun()

        st.markdown("---")
        st.markdown("**Current Session:**")
        if st.session_state.current_session_id:
            st.markdown(f"ID: `{st.session_state.current_session_id[:12]}...`")
        else:
            st.markdown("No active session")

    # Route to appropriate page
    if st.session_state.page == "setup":
        render_setup_page()
    elif st.session_state.page == "interview":
        render_interview_page()
    elif st.session_state.page == "results":
        render_results_page()
    elif st.session_state.page == "learn":
        render_learn_page()


if __name__ == "__main__":
    main()
