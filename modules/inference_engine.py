"""
Rule-based inference engine for CareerPath AI.

The engine is deliberately small:

  1. fire_rules()  - checks every IF-THEN rule in expert_rules.RULES against
                     the student profile and records which ones fired.
  2. infer()       - for each career adds the rule points to a skill-overlap
                     score (from data/careers.json) and ranks the careers.

No randomness and no external services: the same profile always gives the
same result, and every score can be explained by listing the fired rules.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from modules.expert_rules import RULES, RULE_SHARE, SKILL_SHARE, SKILL_TARGET


def normalize(text):
    """Lower-case and tidy spaces so 'python ' and 'Python' compare equal."""
    return " ".join(str(text).lower().split())


@dataclass
class StudentProfile:
    interests: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)       # technical + non-technical
    subjects: List[str] = field(default_factory=list)
    education: str = ""
    preferences: List[str] = field(default_factory=list)

    def facts(self, key):
        """Normalised set of the student's values for one condition group."""
        value = getattr(self, key)
        if isinstance(value, str):
            value = [value] if value else []
        return {normalize(v) for v in value}


@dataclass
class FiredRule:
    rule_id: str
    name: str
    points: int
    matched: Dict[str, List[str]]     # condition group -> values that matched


@dataclass
class CareerResult:
    career: str
    score: float                      # final compatibility, 0-100
    rule_score: float                 # 0-100, from fired rules
    skill_score: float                # 0-100, from skill overlap
    fired_rules: List[FiredRule]
    required_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]


def match_rule(rule, profile):
    """Return {group: matched values} if the rule fires, otherwise None."""
    matched = {}
    for group, wanted_values in rule["if"].items():
        have = profile.facts(group)
        hits = [value for value in wanted_values if normalize(value) in have]
        if not hits:
            return None          # one unsatisfied group -> the rule does not fire
        matched[group] = hits
    return matched


def fire_rules(profile, rules=RULES):
    """Return {career: [FiredRule, ...]} for all rules that fire."""
    fired = {}
    for rule in rules:
        matched = match_rule(rule, profile)
        if matched is not None:
            fired.setdefault(rule["career"], []).append(
                FiredRule(rule["id"], rule["name"], rule["weight"], matched)
            )
    return fired


def rule_maximums(rules=RULES):
    """Total possible rule points per career (designed to be 100)."""
    totals = {}
    for rule in rules:
        totals[rule["career"]] = totals.get(rule["career"], 0) + rule["weight"]
    return totals


def infer(profile, careers_data, rules=RULES):
    """Score every supported career for this profile, best first."""
    required_by_career = {item["career"]: item["skills"] for item in careers_data}
    fired_by_career = fire_rules(profile, rules)
    max_points = rule_maximums(rules)
    student_skills = profile.facts("skills")

    results = []
    for career, max_rule_points in max_points.items():
        required = required_by_career.get(career, [])
        matched = [s for s in required if normalize(s) in student_skills]
        missing = [s for s in required if normalize(s) not in student_skills]

        fired = fired_by_career.get(career, [])
        rule_score = 100.0 * sum(r.points for r in fired) / max_rule_points

        target = min(SKILL_TARGET, len(required)) or 1
        skill_score = 100.0 * min(len(matched), target) / target

        score = RULE_SHARE * rule_score + SKILL_SHARE * skill_score
        results.append(CareerResult(
            career=career,
            score=round(score, 1),
            rule_score=round(rule_score, 1),
            skill_score=round(skill_score, 1),
            fired_rules=fired,
            required_skills=required,
            matched_skills=matched,
            missing_skills=missing,
        ))

    # Best score first; ties broken by number of fired rules, then by name.
    results.sort(key=lambda r: (-r.score, -len(r.fired_rules), r.career))
    return results
