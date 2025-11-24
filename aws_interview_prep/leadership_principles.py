"""Amazon Leadership Principles database with definitions and example questions."""

from __future__ import annotations

from dataclasses import dataclass

from .models import LeadershipPrinciple


@dataclass
class LeadershipPrincipleInfo:
    """Detailed information about a Leadership Principle."""
    principle: LeadershipPrinciple
    definition: str
    behavioral_indicators: list[str]
    example_questions: list[str]
    rubric: dict[int, str]  # Score 1-5 rubric


LEADERSHIP_PRINCIPLES_DB: dict[LeadershipPrinciple, LeadershipPrincipleInfo] = {
    LeadershipPrinciple.CUSTOMER_OBSESSION: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.CUSTOMER_OBSESSION,
        definition="Leaders start with the customer and work backwards. They work vigorously to earn and keep customer trust. Although leaders pay attention to competitors, they obsess over customers.",
        behavioral_indicators=[
            "Prioritizes customer needs over short-term gains",
            "Actively seeks and acts on customer feedback",
            "Makes decisions with customer impact in mind",
            "Goes above and beyond to solve customer problems",
        ],
        example_questions=[
            "Tell me about a time when you had to make a decision that wasn't popular but was right for the customer.",
            "Describe a situation where you went above and beyond for a customer.",
            "Give me an example of when you used customer feedback to improve a product or process.",
            "Tell me about a time when you had to balance customer needs with business constraints.",
        ],
        rubric={
            1: "Shows little consideration for customer needs or impact",
            2: "Considers customers reactively; limited proactive customer focus",
            3: "Regularly considers customer impact; seeks feedback when prompted",
            4: "Actively prioritizes customers; consistently gathers and acts on feedback",
            5: "Obsessively focuses on customers; makes difficult trade-offs in customer favor",
        },
    ),
    LeadershipPrinciple.OWNERSHIP: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.OWNERSHIP,
        definition="Leaders are owners. They think long term and don't sacrifice long-term value for short-term results. They act on behalf of the entire company, beyond just their own team. They never say 'that's not my job.'",
        behavioral_indicators=[
            "Takes responsibility for outcomes beyond immediate scope",
            "Thinks about long-term implications of decisions",
            "Acts without being asked when seeing a problem",
            "Doesn't blame others for failures",
        ],
        example_questions=[
            "Tell me about a time when you took on something significant outside your area of responsibility.",
            "Describe a situation where you had to make a decision that would have long-term implications.",
            "Give me an example of when you saw a problem and took initiative to fix it.",
            "Tell me about a time when something went wrong and you took ownership.",
        ],
        rubric={
            1: "Stays strictly within defined role; avoids responsibility",
            2: "Takes ownership of assigned tasks only",
            3: "Takes ownership of team goals; occasionally steps outside role",
            4: "Consistently owns outcomes beyond immediate scope",
            5: "Acts as true owner; thinks long-term for entire organization",
        },
    ),
    LeadershipPrinciple.INVENT_AND_SIMPLIFY: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.INVENT_AND_SIMPLIFY,
        definition="Leaders expect and require innovation and invention from their teams and always find ways to simplify. They are externally aware, look for new ideas from everywhere, and are not limited by 'not invented here.'",
        behavioral_indicators=[
            "Proposes new ideas and approaches",
            "Simplifies complex processes or systems",
            "Learns from external sources and industries",
            "Questions the status quo",
        ],
        example_questions=[
            "Tell me about a time when you invented something or introduced a significant innovation.",
            "Describe a situation where you simplified a complex process or system.",
            "Give me an example of when you adopted an idea from outside your team or industry.",
            "Tell me about a time when you challenged the way things were done.",
        ],
        rubric={
            1: "Resists change; prefers status quo",
            2: "Accepts change but rarely initiates innovation",
            3: "Occasionally proposes improvements; open to new ideas",
            4: "Regularly innovates and simplifies; seeks external inspiration",
            5: "Drives transformational innovation; relentlessly simplifies",
        },
    ),
    LeadershipPrinciple.ARE_RIGHT_A_LOT: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.ARE_RIGHT_A_LOT,
        definition="Leaders are right a lot. They have strong judgment and good instincts. They seek diverse perspectives and work to disconfirm their beliefs.",
        behavioral_indicators=[
            "Makes well-reasoned decisions",
            "Actively seeks diverse perspectives",
            "Acknowledges and learns from mistakes",
            "Updates views based on new information",
        ],
        example_questions=[
            "Tell me about a time when you made a difficult decision with incomplete information.",
            "Describe a situation where you changed your mind based on new data or perspectives.",
            "Give me an example of when you sought out diverse viewpoints before making a decision.",
            "Tell me about a time when your judgment proved to be correct against opposition.",
        ],
        rubric={
            1: "Makes decisions without analysis; ignores other perspectives",
            2: "Makes adequate decisions; limited perspective seeking",
            3: "Generally makes good decisions; seeks some input",
            4: "Consistently makes sound decisions; actively seeks diverse views",
            5: "Exceptional judgment; systematically disconfirms beliefs",
        },
    ),
    LeadershipPrinciple.LEARN_AND_BE_CURIOUS: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.LEARN_AND_BE_CURIOUS,
        definition="Leaders are never done learning and always seek to improve themselves. They are curious about new possibilities and act to explore them.",
        behavioral_indicators=[
            "Continuously seeks new knowledge and skills",
            "Explores areas outside comfort zone",
            "Asks probing questions",
            "Stays current with industry trends",
        ],
        example_questions=[
            "Tell me about a time when you learned a new skill to solve a problem.",
            "Describe how you stay current with developments in your field.",
            "Give me an example of when curiosity led you to an important discovery or insight.",
            "Tell me about a time when you ventured outside your comfort zone to learn something new.",
        ],
        rubric={
            1: "Shows little interest in learning; sticks to known methods",
            2: "Learns when required; minimal exploration",
            3: "Regularly seeks to learn; shows curiosity",
            4: "Proactively learns; explores diverse topics",
            5: "Insatiable learner; curiosity drives breakthrough insights",
        },
    ),
    LeadershipPrinciple.HIRE_AND_DEVELOP_THE_BEST: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.HIRE_AND_DEVELOP_THE_BEST,
        definition="Leaders raise the performance bar with every hire and promotion. They recognize exceptional talent, and willingly move them throughout the organization. Leaders develop leaders and take seriously their role in coaching others.",
        behavioral_indicators=[
            "Sets high hiring standards",
            "Invests in developing team members",
            "Provides constructive feedback",
            "Recognizes and promotes talent",
        ],
        example_questions=[
            "Tell me about a time when you mentored or developed someone.",
            "Describe your approach to hiring and what you look for in candidates.",
            "Give me an example of when you gave difficult feedback that helped someone improve.",
            "Tell me about a time when you recognized exceptional talent and helped advance their career.",
        ],
        rubric={
            1: "Little investment in team development; hires without raising bar",
            2: "Occasional mentoring; meets basic hiring standards",
            3: "Regularly develops team; maintains hiring bar",
            4: "Actively develops others; raises the bar in hiring",
            5: "Transforms team capability; exceptional talent developer",
        },
    ),
    LeadershipPrinciple.INSIST_ON_HIGHEST_STANDARDS: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.INSIST_ON_HIGHEST_STANDARDS,
        definition="Leaders have relentlessly high standards — many people may think these standards are unreasonably high. Leaders are continually raising the bar and drive their teams to deliver high quality products, services, and processes.",
        behavioral_indicators=[
            "Sets and maintains high quality standards",
            "Doesn't accept mediocre work",
            "Continuously raises the bar",
            "Pays attention to details",
        ],
        example_questions=[
            "Tell me about a time when you refused to compromise on quality.",
            "Describe a situation where you raised the bar for your team or organization.",
            "Give me an example of when attention to detail made a significant difference.",
            "Tell me about a time when you had to push back on something that didn't meet your standards.",
        ],
        rubric={
            1: "Accepts mediocre quality; low standards",
            2: "Maintains basic quality standards",
            3: "Sets good standards; usually delivers quality",
            4: "High standards; consistently raises the bar",
            5: "Relentlessly high standards; inspires excellence in others",
        },
    ),
    LeadershipPrinciple.THINK_BIG: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.THINK_BIG,
        definition="Thinking small is a self-fulfilling prophecy. Leaders create and communicate a bold direction that inspires results. They think differently and look around corners for ways to serve customers.",
        behavioral_indicators=[
            "Sets ambitious goals",
            "Envisions large-scale impact",
            "Challenges conventional thinking",
            "Inspires others with vision",
        ],
        example_questions=[
            "Tell me about a time when you proposed a bold or unconventional idea.",
            "Describe your biggest professional accomplishment and its impact.",
            "Give me an example of when you thought beyond your immediate scope to achieve greater impact.",
            "Tell me about a time when you inspired others with a compelling vision.",
        ],
        rubric={
            1: "Thinks incrementally; limits scope",
            2: "Occasionally thinks beyond immediate scope",
            3: "Sets ambitious goals; sometimes thinks big",
            4: "Regularly proposes bold ideas; inspires others",
            5: "Consistently thinks at scale; transforms perspectives",
        },
    ),
    LeadershipPrinciple.BIAS_FOR_ACTION: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.BIAS_FOR_ACTION,
        definition="Speed matters in business. Many decisions and actions are reversible and do not need extensive study. We value calculated risk taking.",
        behavioral_indicators=[
            "Acts decisively",
            "Doesn't wait for perfect information",
            "Takes calculated risks",
            "Values speed appropriately",
        ],
        example_questions=[
            "Tell me about a time when you had to make a quick decision.",
            "Describe a situation where you took a calculated risk.",
            "Give me an example of when you moved forward without complete information.",
            "Tell me about a time when speed was critical and how you handled it.",
        ],
        rubric={
            1: "Overly cautious; analysis paralysis",
            2: "Slow to act; prefers extensive analysis",
            3: "Generally timely decisions; some calculated risks",
            4: "Decisive action; effectively manages risk",
            5: "Optimal speed/quality balance; inspires action in others",
        },
    ),
    LeadershipPrinciple.FRUGALITY: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.FRUGALITY,
        definition="Accomplish more with less. Constraints breed resourcefulness, self-sufficiency, and invention. There are no extra points for growing headcount, budget size, or fixed expense.",
        behavioral_indicators=[
            "Maximizes resources efficiently",
            "Finds creative low-cost solutions",
            "Avoids unnecessary spending",
            "Delivers results within constraints",
        ],
        example_questions=[
            "Tell me about a time when you accomplished something with limited resources.",
            "Describe a situation where you found a creative solution to reduce costs.",
            "Give me an example of when you had to do more with less.",
            "Tell me about a time when constraints led you to a better solution.",
        ],
        rubric={
            1: "Wasteful of resources; seeks excess budget",
            2: "Basic resource management",
            3: "Generally efficient; works within constraints",
            4: "Consistently frugal; finds creative low-cost solutions",
            5: "Exemplary resourcefulness; constraints drive innovation",
        },
    ),
    LeadershipPrinciple.EARN_TRUST: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.EARN_TRUST,
        definition="Leaders listen attentively, speak candidly, and treat others respectfully. They are vocally self-critical, even when doing so is awkward or embarrassing.",
        behavioral_indicators=[
            "Listens actively to others",
            "Communicates honestly and directly",
            "Admits mistakes openly",
            "Treats everyone with respect",
        ],
        example_questions=[
            "Tell me about a time when you had to deliver difficult feedback.",
            "Describe a situation where you admitted a mistake publicly.",
            "Give me an example of how you built trust with a skeptical stakeholder.",
            "Tell me about a time when you had to be vocally self-critical.",
        ],
        rubric={
            1: "Defensive; poor listener; lacks transparency",
            2: "Occasionally transparent; basic respectful behavior",
            3: "Generally trustworthy; admits mistakes when pressed",
            4: "Proactively transparent; actively builds trust",
            5: "Exemplary trust-builder; vocally self-critical",
        },
    ),
    LeadershipPrinciple.DIVE_DEEP: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.DIVE_DEEP,
        definition="Leaders operate at all levels, stay connected to the details, audit frequently, and are skeptical when metrics and anecdote differ. No task is beneath them.",
        behavioral_indicators=[
            "Understands details behind decisions",
            "Verifies data and assumptions",
            "Operates at multiple levels",
            "Stays connected to front-line work",
        ],
        example_questions=[
            "Tell me about a time when you dug deep into data to find a root cause.",
            "Describe a situation where you discovered something important by diving into details.",
            "Give me an example of when you found a discrepancy between metrics and reality.",
            "Tell me about a time when understanding the details helped you make a better decision.",
        ],
        rubric={
            1: "Stays high-level; avoids details",
            2: "Occasional deep dives when required",
            3: "Regularly reviews details; verifies key data",
            4: "Systematically dives deep; catches discrepancies",
            5: "Masters details at all levels; data-driven skeptic",
        },
    ),
    LeadershipPrinciple.HAVE_BACKBONE: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.HAVE_BACKBONE,
        definition="Leaders are obligated to respectfully challenge decisions when they disagree, even when doing so is uncomfortable or exhausting. Leaders have conviction and are tenacious. They do not compromise for the sake of social cohesion. Once a decision is determined, they commit wholly.",
        behavioral_indicators=[
            "Speaks up when disagreeing",
            "Challenges decisions respectfully",
            "Commits fully once decided",
            "Doesn't compromise principles for harmony",
        ],
        example_questions=[
            "Tell me about a time when you disagreed with a decision and how you handled it.",
            "Describe a situation where you pushed back on something you believed was wrong.",
            "Give me an example of when you committed fully to a decision you initially disagreed with.",
            "Tell me about a time when you had to stand firm against opposition.",
        ],
        rubric={
            1: "Avoids conflict; goes along to get along",
            2: "Occasionally voices disagreement",
            3: "Speaks up when stakes are high; commits once decided",
            4: "Regularly challenges respectfully; strong commitment",
            5: "Principled challenger; exemplary disagree-and-commit",
        },
    ),
    LeadershipPrinciple.DELIVER_RESULTS: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.DELIVER_RESULTS,
        definition="Leaders focus on the key inputs for their business and deliver them with the right quality and in a timely fashion. Despite setbacks, they rise to the occasion and never settle.",
        behavioral_indicators=[
            "Achieves goals consistently",
            "Overcomes obstacles",
            "Focuses on key inputs",
            "Delivers quality on time",
        ],
        example_questions=[
            "Tell me about a time when you had to deliver results despite significant obstacles.",
            "Describe your most challenging project and how you delivered it.",
            "Give me an example of when you had to prioritize to meet a critical deadline.",
            "Tell me about a time when you turned around a failing project.",
        ],
        rubric={
            1: "Frequently misses goals; gives up easily",
            2: "Delivers some results; struggles with obstacles",
            3: "Generally delivers; overcomes most obstacles",
            4: "Consistently delivers quality; resilient",
            5: "Exceptional track record; inspires results in others",
        },
    ),
    LeadershipPrinciple.STRIVE_TO_BE_EARTHS_BEST_EMPLOYER: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.STRIVE_TO_BE_EARTHS_BEST_EMPLOYER,
        definition="Leaders work every day to create a safer, more productive, higher performing, more diverse, and more just work environment. They lead with empathy, have fun at work, and make it easy for others to have fun.",
        behavioral_indicators=[
            "Creates inclusive environment",
            "Prioritizes team wellbeing",
            "Promotes diversity and belonging",
            "Makes work enjoyable",
        ],
        example_questions=[
            "Tell me about a time when you improved the work environment for your team.",
            "Describe how you've promoted diversity or inclusion in your workplace.",
            "Give me an example of when you prioritized team wellbeing over productivity.",
            "Tell me about a time when you helped create a more fun or engaging work environment.",
        ],
        rubric={
            1: "Ignores team environment; focuses only on output",
            2: "Basic attention to work environment",
            3: "Supports team wellbeing; promotes inclusion",
            4: "Actively improves environment; champions diversity",
            5: "Transforms workplace culture; exemplary employer",
        },
    ),
    LeadershipPrinciple.SUCCESS_AND_SCALE_BRING_BROAD_RESPONSIBILITY: LeadershipPrincipleInfo(
        principle=LeadershipPrinciple.SUCCESS_AND_SCALE_BRING_BROAD_RESPONSIBILITY,
        definition="We started in a garage, but we're not there anymore. We are big, we impact the world, and we are far from perfect. We must be humble and thoughtful about even the secondary effects of our actions.",
        behavioral_indicators=[
            "Considers broader impact of decisions",
            "Thinks about secondary effects",
            "Acts responsibly at scale",
            "Shows humility about limitations",
        ],
        example_questions=[
            "Tell me about a time when you considered the broader impact of your work.",
            "Describe a situation where you had to think about secondary effects of a decision.",
            "Give me an example of when you showed humility about your limitations.",
            "Tell me about a time when you balanced business goals with broader responsibilities.",
        ],
        rubric={
            1: "Ignores broader impact; narrow focus",
            2: "Occasional consideration of wider effects",
            3: "Regularly considers broader impact",
            4: "Systematically evaluates secondary effects",
            5: "Exemplary stewardship; humble despite success",
        },
    ),
}


def get_lp_info(principle: LeadershipPrinciple) -> LeadershipPrincipleInfo:
    """Get detailed information for a Leadership Principle."""
    return LEADERSHIP_PRINCIPLES_DB[principle]


def get_all_lp_definitions() -> dict[str, str]:
    """Get all LP names and definitions."""
    return {lp.value: info.definition for lp, info in LEADERSHIP_PRINCIPLES_DB.items()}


def get_example_questions(principle: LeadershipPrinciple) -> list[str]:
    """Get example questions for a specific LP."""
    return LEADERSHIP_PRINCIPLES_DB[principle].example_questions


def get_rubric(principle: LeadershipPrinciple) -> dict[int, str]:
    """Get scoring rubric for a specific LP."""
    return LEADERSHIP_PRINCIPLES_DB[principle].rubric
