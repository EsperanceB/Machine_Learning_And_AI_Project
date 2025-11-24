"""Document ingestion and parsing services for CV, portfolio, and job descriptions."""

from __future__ import annotations

import re
from typing import Optional

from .models import Candidate, JobDescription, LeadershipPrinciple


def extract_skills_from_text(text: str) -> list[str]:
    """Extract technical skills from resume text using keyword matching."""
    # Common technical skill categories
    skill_patterns = [
        # Programming languages
        r"\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Ruby|Scala|Kotlin|Swift|PHP|R)\b",
        # Cloud platforms
        r"\b(AWS|Azure|GCP|Google Cloud|Amazon Web Services|EC2|S3|Lambda|SageMaker|Bedrock)\b",
        # ML/AI frameworks
        r"\b(TensorFlow|PyTorch|Keras|Scikit-learn|sklearn|Pandas|NumPy|XGBoost|LightGBM)\b",
        # Data tools
        r"\b(SQL|PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch|Spark|Hadoop|Kafka|Airflow)\b",
        # DevOps/Infrastructure
        r"\b(Docker|Kubernetes|K8s|Terraform|CloudFormation|CI/CD|Jenkins|GitHub Actions)\b",
        # Other technical
        r"\b(REST|GraphQL|API|Microservices|Machine Learning|ML|AI|Deep Learning|NLP|LLM)\b",
    ]

    skills = set()
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Normalize case for common acronyms
            normalized = match.upper() if match.upper() in {"AWS", "GCP", "SQL", "API", "ML", "AI", "NLP", "LLM"} else match
            skills.add(normalized)

    return sorted(skills)


def extract_experience_years(text: str) -> Optional[int]:
    """Extract years of experience from resume text."""
    patterns = [
        r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience",
        r"experience[:\s]+(\d+)\+?\s*(?:years?|yrs?)",
        r"(\d+)\+?\s*(?:years?|yrs?)\s*in",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def parse_resume(resume_text: str, name: str = "Candidate") -> Candidate:
    """Parse resume text and extract candidate information."""
    skills = extract_skills_from_text(resume_text)
    experience_years = extract_experience_years(resume_text)

    return Candidate(
        name=name,
        resume_text=resume_text,
        skills=skills,
        experience_years=experience_years,
    )


def extract_requirements(jd_text: str) -> list[str]:
    """Extract job requirements from job description text."""
    requirements = []

    # Look for common requirement section patterns
    req_patterns = [
        r"(?:requirements?|qualifications?|what you(?:'ll)? need)[:\s]*\n((?:[\s\S]*?)(?=\n\n|\Z))",
        r"(?:you have|you bring|must have)[:\s]*\n((?:[\s\S]*?)(?=\n\n|\Z))",
    ]

    for pattern in req_patterns:
        match = re.search(pattern, jd_text, re.IGNORECASE)
        if match:
            section = match.group(1)
            # Extract bullet points or numbered items
            items = re.findall(r"[\•\-\*]\s*(.+?)(?:\n|$)", section)
            if items:
                requirements.extend(items)

    # If no structured requirements found, look for skill mentions
    if not requirements:
        # Extract sentences containing requirement-like language
        sentences = re.split(r"[.!?]\s+", jd_text)
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in ["required", "must have", "experience with", "proficient"]):
                requirements.append(sentence.strip())

    return requirements[:10]  # Limit to top 10 requirements


def map_jd_to_lps(jd_text: str) -> list[LeadershipPrinciple]:
    """Map job description to relevant Leadership Principles based on keywords."""
    lp_keywords = {
        LeadershipPrinciple.CUSTOMER_OBSESSION: ["customer", "client", "user experience", "stakeholder"],
        LeadershipPrinciple.OWNERSHIP: ["ownership", "accountability", "end-to-end", "responsible"],
        LeadershipPrinciple.INVENT_AND_SIMPLIFY: ["innovation", "simplify", "creative", "new solutions"],
        LeadershipPrinciple.ARE_RIGHT_A_LOT: ["judgment", "decision-making", "analytical", "strategic"],
        LeadershipPrinciple.LEARN_AND_BE_CURIOUS: ["learning", "curious", "growth mindset", "continuous improvement"],
        LeadershipPrinciple.HIRE_AND_DEVELOP_THE_BEST: ["mentor", "coach", "develop", "lead team"],
        LeadershipPrinciple.INSIST_ON_HIGHEST_STANDARDS: ["quality", "excellence", "high standards", "best practices"],
        LeadershipPrinciple.THINK_BIG: ["scale", "vision", "ambitious", "large-scale"],
        LeadershipPrinciple.BIAS_FOR_ACTION: ["fast-paced", "agile", "quick", "action-oriented"],
        LeadershipPrinciple.FRUGALITY: ["efficiency", "optimize", "cost-effective", "lean"],
        LeadershipPrinciple.EARN_TRUST: ["collaboration", "trust", "transparency", "communication"],
        LeadershipPrinciple.DIVE_DEEP: ["detail-oriented", "data-driven", "analysis", "investigate"],
        LeadershipPrinciple.HAVE_BACKBONE: ["challenge", "disagree", "conviction", "push back"],
        LeadershipPrinciple.DELIVER_RESULTS: ["deliver", "results", "goals", "metrics", "performance"],
        LeadershipPrinciple.STRIVE_TO_BE_EARTHS_BEST_EMPLOYER: ["inclusive", "diverse", "wellbeing", "culture"],
        LeadershipPrinciple.SUCCESS_AND_SCALE_BRING_BROAD_RESPONSIBILITY: ["impact", "responsibility", "sustainability"],
    }

    text_lower = jd_text.lower()
    matched_lps = []

    for lp, keywords in lp_keywords.items():
        if any(kw in text_lower for kw in keywords):
            matched_lps.append(lp)

    # Always include core behavioral LPs if few matches
    core_lps = [
        LeadershipPrinciple.CUSTOMER_OBSESSION,
        LeadershipPrinciple.OWNERSHIP,
        LeadershipPrinciple.DELIVER_RESULTS,
    ]
    for lp in core_lps:
        if lp not in matched_lps:
            matched_lps.append(lp)

    return matched_lps


def parse_job_description(
    jd_text: str,
    title: str = "Software Development Engineer",
    company: str = "Amazon",
) -> JobDescription:
    """Parse job description text and extract requirements and relevant LPs."""
    requirements = extract_requirements(jd_text)
    target_lps = map_jd_to_lps(jd_text)

    # Extract skills as preferred qualifications
    skills = extract_skills_from_text(jd_text)

    return JobDescription(
        title=title,
        company=company,
        description=jd_text,
        requirements=requirements,
        preferred_qualifications=skills,
        target_lps=target_lps,
    )
