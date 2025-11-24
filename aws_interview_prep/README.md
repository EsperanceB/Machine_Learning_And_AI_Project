# AWS Interview Prep Tool

A comprehensive tool for practicing AWS/Amazon behavioral interviews with Leadership Principles (LP) feedback and STAR format coaching.

## Features

✅ **Inputs**
- Candidate CV/resume text parsing
- Portfolio/project summaries
- Job description analysis
- Amazon Leadership Principles database
- Past interview questions database

✅ **Question Generation**
- Personalized questions based on candidate background
- User-configurable number of questions (1-20)
- Focus on specific Leadership Principles
- Adjustable difficulty levels
- Questions tagged with primary/secondary LPs

✅ **Answer Evaluation**
- STAR format (Situation, Task, Action, Result) analysis
- LP scoring (1-5 scale) with detailed rubrics
- Specific, actionable feedback
- AI-powered answer improvement suggestions
- STAR format rewriting for better answers

✅ **Session Management**
- Interactive interview sessions
- Progress tracking
- Session summaries with LP performance
- Question-by-question feedback history

## Installation

```bash
cd aws_interview_prep
pip install -r requirements.txt
```

### Optional: Enable AI Features

For AI-powered question generation and feedback, set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Command Line Interface

```bash
# Basic usage with 5 questions
python -m aws_interview_prep.cli --name "John Doe" --questions 5

# With resume and job description files
python -m aws_interview_prep.cli --name "Jane" --resume resume.txt --jd job.txt

# Focus on specific Leadership Principles
python -m aws_interview_prep.cli --name "Test" --focus "ownership,customer_obsession"

# List all Leadership Principles
python -m aws_interview_prep.cli --list-lps
```

### Web Interface (Streamlit)

```bash
streamlit run aws_interview_prep/streamlit_app.py
```

Then open http://localhost:8501 in your browser.

### Programmatic Usage

```python
from aws_interview_prep.session_manager import InterviewSessionManager
from aws_interview_prep.models import LeadershipPrinciple

# Initialize manager (optionally with OpenAI client)
manager = InterviewSessionManager()

# Create a session
session = manager.create_session(
    candidate_name="John Doe",
    resume_text="5 years experience in Python, AWS, Machine Learning...",
    job_description_text="We are looking for an SDE...",
    num_questions=5,
    focus_lps=[LeadershipPrinciple.OWNERSHIP, LeadershipPrinciple.CUSTOMER_OBSESSION],
)

# Start the session
manager.start_session(session.id)

# Get questions and submit answers
while True:
    question = manager.get_current_question(session.id)
    if not question:
        break
    
    print(f"Q: {question.question_text}")
    answer = input("Your answer: ")
    
    evaluation = manager.submit_answer(session.id, answer)
    print(f"Score: {evaluation.overall_score}/5")
    print(f"Feedback: {evaluation.feedback}")

# Get session summary
summary = manager.get_session_summary(session.id)
print(f"Average Score: {summary['average_score']}")
print(f"LP Performance: {summary['lp_summary']}")
```

## Amazon Leadership Principles

The tool covers all 16 Amazon Leadership Principles:

1. **Customer Obsession** - Start with the customer and work backwards
2. **Ownership** - Think long term, act on behalf of the entire company
3. **Invent and Simplify** - Expect and require innovation
4. **Are Right, A Lot** - Strong judgment and good instincts
5. **Learn and Be Curious** - Never done learning, always seeking improvement
6. **Hire and Develop the Best** - Raise the performance bar
7. **Insist on the Highest Standards** - Relentlessly high standards
8. **Think Big** - Create bold direction that inspires results
9. **Bias for Action** - Speed matters, value calculated risk taking
10. **Frugality** - Accomplish more with less
11. **Earn Trust** - Listen attentively, speak candidly
12. **Dive Deep** - Operate at all levels, stay connected to details
13. **Have Backbone; Disagree and Commit** - Challenge decisions respectfully
14. **Deliver Results** - Focus on key inputs, deliver with quality
15. **Strive to be Earth's Best Employer** - Create safe, productive environment
16. **Success and Scale Bring Broad Responsibility** - Be humble about impact

## STAR Format

The tool helps you structure answers using the STAR method:

- **S**ituation: Set the context for your story
- **T**ask: Describe what was required of you
- **A**ction: Explain what steps YOU took (use "I", not "we")
- **R**esult: Share outcomes with metrics when possible

## Project Structure

```
aws_interview_prep/
├── __init__.py              # Package initialization
├── models.py                # Pydantic data models
├── leadership_principles.py # LP database with definitions and rubrics
├── document_ingestion.py    # CV/JD parsing services
├── question_generator.py    # Question generation engine
├── answer_evaluator.py      # Answer evaluation with STAR analysis
├── session_manager.py       # Interview session management
├── cli.py                   # Command-line interface
├── streamlit_app.py         # Web interface
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interfaces                          │
│                 CLI    │    Streamlit Web                   │
└──────────────────────┬─────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────┐
│                 Session Manager                             │
│    (Creates sessions, manages Q&A flow, tracks progress)   │
└──────────────────────┬─────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
┌──────▼─────┐  ┌──────▼─────┐  ┌──────▼─────┐
│  Document  │  │  Question  │  │   Answer   │
│  Ingestion │  │  Generator │  │  Evaluator │
└──────┬─────┘  └──────┬─────┘  └──────┬─────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────┐
│              Leadership Principles Database                 │
│    (Definitions, Rubrics, Example Questions)               │
└────────────────────────────────────────────────────────────┘
```

## Contributing

Contributions are welcome! Areas for enhancement:

- [ ] RAG implementation with pgvector for semantic search
- [ ] File upload support (PDF, DOCX) for resumes
- [ ] Persistent storage with PostgreSQL
- [ ] Voice-based interview practice
- [ ] Mock interview scheduler
- [ ] Progress tracking across multiple sessions

## License

MIT License - See repository root for details.
