"""
Lightweight Agent Controller for CareerPath AI.

Student Input -> Student Profile -> Agent Controller -> Rule-Based Inference
-> Career Recommendation -> Explanation + Skill Gaps + Roadmap

The controller follows a simple perceive -> reason -> act loop. It has no
external dependencies: all knowledge comes from the local rules and JSON data.
"""

from dataclasses import dataclass, field
from typing import List

from modules.expert_rules import MIN_SCORE, RULES, TOP_N
from modules.inference_engine import CareerResult, StudentProfile, infer

KEY_SKILLS_SHOWN = 8       # "relevant skills" listed per career
GAP_SKILLS_SHOWN = 6       # "skills to improve" listed per career


@dataclass
class Recommendation:
    rank: int
    career: str
    score: float
    rule_score: float
    skill_score: float
    summary: str                         # one-line "why recommended"
    fired_rules: list                    # list of FiredRule
    key_skills: List[str]                # relevant skills for the career
    matched_skills: List[str]            # skills the student already has
    skills_to_improve: List[str]         # first few missing skills
    all_missing_skills: List[str]        # full gap list (used for courses)
    difficulty: str
    learning_time: str
    summary_text: str                    # short career description
    typical_education: str
    roadmap: List[dict]                  # [{"stage": ..., "items": [...]}, ...]


@dataclass
class AgentResult:
    profile: StudentProfile
    recommendations: List[Recommendation]
    trace: List[str] = field(default_factory=list)


def _unique(values):
    """Remove duplicates (ignoring case) while keeping the original order."""
    seen, out = set(), []
    for value in values:
        key = str(value).strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(str(value).strip())
    return out


def _count(number, noun):
    """'1 skill' / '3 skills'."""
    return f"{number} {noun}" + ("" if number == 1 else "s")


class CareerAgent:
    def __init__(self, careers_data, career_info_data, roadmaps, top_n=TOP_N):
        self.careers_data = careers_data
        self.career_info = {item["career"]: item for item in career_info_data}
        self.roadmaps = roadmaps
        self.top_n = top_n

    # -- 1. perceive --------------------------------------------------------
    def perceive(self, raw):
        """Turn raw form data into a clean StudentProfile."""
        return StudentProfile(
            interests=_unique(raw.get("interests", [])),
            skills=_unique(raw.get("skills", [])),
            subjects=_unique(raw.get("subjects", [])),
            education=raw.get("education", "") or "",
            preferences=_unique(raw.get("preferences", [])),
        )

    # -- 2. reason ----------------------------------------------------------
    def reason(self, profile):
        """Ask the rule-based inference engine to score all careers."""
        return infer(profile, self.careers_data)

    # -- 3. act -------------------------------------------------------------
    def act(self, results):
        """Build the final top-N recommendations with explanations and roadmaps."""
        recommendations = []
        candidates = [r for r in results if r.score >= MIN_SCORE][: self.top_n]
        for rank, result in enumerate(candidates, start=1):
            info = self.career_info.get(result.career, {})
            plan = self.roadmaps.get(result.career, {})
            recommendations.append(Recommendation(
                rank=rank,
                career=result.career,
                score=result.score,
                rule_score=result.rule_score,
                skill_score=result.skill_score,
                summary=self._why(result),
                fired_rules=result.fired_rules,
                key_skills=result.required_skills[:KEY_SKILLS_SHOWN],
                matched_skills=result.matched_skills,
                skills_to_improve=result.missing_skills[:GAP_SKILLS_SHOWN],
                all_missing_skills=result.missing_skills,
                difficulty=info.get("difficulty", "N/A"),
                learning_time=info.get("learning_time", "N/A"),
                summary_text=plan.get("summary", ""),
                typical_education=plan.get("typical_education", ""),
                roadmap=plan.get("stages", []),
            ))
        return recommendations

    # -- full run -----------------------------------------------------------
    def run(self, raw):
        trace = []
        profile = self.perceive(raw)
        trace.append(
            f"Student profile built: {_count(len(profile.interests), 'interest')}, "
            f"{_count(len(profile.skills), 'skill')}, "
            f"{_count(len(profile.subjects), 'favourite subject')}, "
            f"{_count(len(profile.preferences), 'career preference')}, "
            f"education = {profile.education or 'not given'}."
        )

        # Education alone is not enough information to recommend anything.
        if not (profile.interests or profile.skills or profile.subjects or profile.preferences):
            trace.append("Not enough information to run the inference engine.")
            return AgentResult(profile=profile, recommendations=[], trace=trace)

        results = self.reason(profile)
        fired_total = sum(len(r.fired_rules) for r in results)
        trace.append(
            f"Agent controller passed the profile to the inference engine: "
            f"{len(RULES)} rules checked, {fired_total} rules fired, "
            f"{len(results)} careers scored."
        )

        recommendations = self.act(results)
        if recommendations:
            names = ", ".join(f"{r.career} ({r.score:.0f}%)" for r in recommendations)
            trace.append(
                f"Top {len(recommendations)} careers selected: {names}. "
                f"Explanations, skill gaps and roadmaps attached."
            )
        else:
            trace.append("No career matched the given inputs.")
        return AgentResult(profile=profile, recommendations=recommendations, trace=trace)

    # -- helpers ------------------------------------------------------------
    @staticmethod
    def _why(result: CareerResult):
        """One-sentence reason built from the rules that fired and skills matched."""
        parts = []
        if result.fired_rules:
            best = sorted(result.fired_rules, key=lambda r: -r.points)[:2]
            names = " and ".join(f"'{r.name}'" for r in best)
            parts.append(f"your profile satisfied the rule(s) {names}")
        if result.matched_skills:
            shown = ", ".join(result.matched_skills[:4])
            more = len(result.matched_skills) - 4
            suffix = f" (+{more} more)" if more > 0 else ""
            parts.append(
                f"you already have {len(result.matched_skills)} of its "
                f"{len(result.required_skills)} listed skills: {shown}{suffix}"
            )
        if not parts:
            return "Only a weak match with the information provided."
        return "Recommended because " + ", and ".join(parts) + "."
