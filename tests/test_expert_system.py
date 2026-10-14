"""
Basic checks for the CareerPath AI expert system (no Streamlit needed).

Run from the project folder:
    python -m unittest tests.test_expert_system -v
"""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from modules import expert_rules as kb                      # noqa: E402
from modules.agent import CareerAgent                       # noqa: E402
from modules.helpers import extract_skills                  # noqa: E402


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


CAREERS = load("careers.json")
CAREER_INFO = load("career_info.json")
ROADMAPS = load("roadmaps.json")
ALL_SKILLS = set(load("skills.json")["skills"]) | set(kb.SOFT_SKILLS)
for item in CAREERS:
    ALL_SKILLS |= set(item["skills"])

AGENT = CareerAgent(CAREERS, CAREER_INFO, ROADMAPS)

PROGRAMMER = {
    "interests": [kb.I_PROG], "skills": ["Python", "Java", "Git", "SQL", "Data Structures"],
    "subjects": [kb.S_CS, kb.S_MATH], "education": kb.E_UG, "preferences": [kb.P_BUILD],
}
DATA_FAN = {
    "interests": [kb.I_DATA], "skills": ["Excel", "SQL", "Statistics", "Power BI", "Critical Thinking"],
    "subjects": [kb.S_MATH, kb.S_STAT], "education": kb.E_UG, "preferences": [kb.P_DATA],
}
DESIGNER = {
    "interests": [kb.I_DESIGN], "skills": ["Creativity", "Figma", "Typography", "Communication"],
    "subjects": [kb.S_ART], "education": kb.E_HS, "preferences": [kb.P_CREATIVE],
}
HACKER = {
    "interests": [kb.I_SEC], "skills": ["Linux", "Networking", "Python", "Wireshark"],
    "subjects": [kb.S_CS], "education": kb.E_UG, "preferences": [kb.P_SEC],
}
MARKETER = {
    "interests": [kb.I_MKT], "skills": ["SEO", "Copywriting", "Creativity", "Communication"],
    "subjects": [kb.S_ENG, kb.S_BUS], "education": kb.E_UG, "preferences": [kb.P_CREATIVE],
}
HARDWARE = {
    "interests": [kb.I_HW], "skills": ["C", "Microcontrollers", "Electronics"],
    "subjects": [kb.S_PHY, kb.S_ELEC], "education": kb.E_DIP, "preferences": [kb.P_HW],
}
AI_FAN = {
    "interests": [kb.I_AI], "skills": ["Python", "Machine Learning", "TensorFlow", "Deep Learning"],
    "subjects": [kb.S_MATH, kb.S_CS], "education": kb.E_PG, "preferences": [kb.P_DATA],
}


def top_names(raw):
    return [r.career for r in AGENT.run(raw).recommendations]


class KnowledgeBaseTests(unittest.TestCase):
    def test_rule_weights_sum_to_100_per_career(self):
        totals = {}
        for rule in kb.RULES:
            totals[rule["career"]] = totals.get(rule["career"], 0) + rule["weight"]
        for career, total in totals.items():
            self.assertEqual(total, 100, career)

    def test_every_supported_career_has_data(self):
        dataset = {c["career"] for c in CAREERS}
        info = {c["career"] for c in CAREER_INFO}
        for career in kb.SUPPORTED_CAREERS:
            self.assertIn(career, dataset)
            self.assertIn(career, info)
            self.assertIn(career, ROADMAPS)
            self.assertEqual(len(ROADMAPS[career]["stages"]), 4, career)

    def test_rule_values_are_valid_options(self):
        valid = {
            "interests": set(kb.INTERESTS), "subjects": set(kb.SUBJECTS),
            "preferences": set(kb.PREFERENCES), "education": set(kb.EDUCATION_LEVELS),
            "skills": ALL_SKILLS,
        }
        for rule in kb.RULES:
            for group, values in rule["if"].items():
                for value in values:
                    self.assertIn(value, valid[group], f"{rule['id']}: {value}")


class RecommendationTests(unittest.TestCase):
    def test_expected_top_career_per_profile(self):
        expected = {
            "Software Developer": PROGRAMMER,
            "Data Analyst": DATA_FAN,
            "UI UX Designer": DESIGNER,
            "Cyber Security Analyst": HACKER,
            "Digital Marketing Specialist": MARKETER,
            "Embedded Systems Engineer": HARDWARE,
        }
        for career, raw in expected.items():
            self.assertEqual(top_names(raw)[0], career, career)

    def test_ai_profile_ranks_ml_or_data_science_first(self):
        self.assertIn(top_names(AI_FAN)[0], {"ML Engineer", "Data Scientist"})

    def test_different_inputs_give_different_results(self):
        lists = [tuple(top_names(p)) for p in
                 (PROGRAMMER, DATA_FAN, DESIGNER, HACKER, MARKETER, HARDWARE, AI_FAN)]
        self.assertEqual(len(set(lists)), len(lists))

    def test_always_three_results_for_normal_input_and_sorted(self):
        recs = AGENT.run(PROGRAMMER).recommendations
        self.assertEqual(len(recs), 3)
        scores = [r.score for r in recs]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertTrue(all(0 < s <= 100 for s in scores))

    def test_deterministic(self):
        self.assertEqual(top_names(DATA_FAN), top_names(DATA_FAN))

    def test_empty_input_gives_no_recommendations(self):
        self.assertEqual(AGENT.run({}).recommendations, [])

    def test_education_alone_gives_no_recommendations(self):
        self.assertEqual(AGENT.run({"education": kb.E_UG}).recommendations, [])

    def test_narrow_input_never_pads_with_weak_matches(self):
        recs = AGENT.run(HARDWARE).recommendations
        self.assertGreaterEqual(len(recs), 1)
        self.assertLessEqual(len(recs), 3)
        self.assertTrue(all(r.score >= kb.MIN_SCORE for r in recs))

    def test_education_level_alone_cannot_trigger_a_recommendation(self):
        # Hardware-only student: Data Scientist / Business Analyst would only
        # score from the generic "degree-level study" rule, so they must not appear.
        narrow = {"interests": [kb.I_HW], "skills": ["C", "Microcontrollers"], "education": kb.E_UG}
        names = top_names(narrow)
        self.assertEqual(names[0], "Embedded Systems Engineer")
        self.assertNotIn("Data Scientist", names)
        self.assertNotIn("Business Analyst", names)

    def test_case_and_spacing_of_skills_do_not_matter(self):
        messy = dict(PROGRAMMER, skills=["  python", "JAVA ", "git", "sql", "data  structures"])
        self.assertEqual(top_names(messy), top_names(PROGRAMMER))

    def test_adding_skills_raises_score_and_removes_gap(self):
        base = dict(DATA_FAN, skills=["Excel"])
        more = dict(DATA_FAN, skills=["Excel", "SQL", "Statistics", "Python", "Tableau"])
        a = next(r for r in AGENT.run(base).recommendations if r.career == "Data Analyst")
        b = next(r for r in AGENT.run(more).recommendations if r.career == "Data Analyst")
        self.assertGreater(b.score, a.score)
        self.assertNotIn("Tableau", b.all_missing_skills)
        self.assertIn("Tableau", a.all_missing_skills)

    def test_recommendation_has_all_display_fields(self):
        for rec in AGENT.run(DESIGNER).recommendations:
            self.assertTrue(rec.summary)
            self.assertTrue(rec.key_skills)
            self.assertTrue(rec.skills_to_improve)
            self.assertEqual(len(rec.roadmap), 4)
            self.assertNotEqual(rec.difficulty, "N/A")
            self.assertTrue(rec.fired_rules)

    def test_example_rules_from_the_brief_fire(self):
        def fired_ids(raw, career):
            rec = next(r for r in AGENT.run(raw).recommendations if r.career == career)
            return {f.rule_id for f in rec.fired_rules}
        self.assertIn("SD1", fired_ids(PROGRAMMER, "Software Developer"))
        self.assertIn("DA1", fired_ids(DATA_FAN, "Data Analyst"))
        self.assertIn("UX1", fired_ids(DESIGNER, "UI UX Designer"))


class ResumeExtractionTests(unittest.TestCase):
    def test_whole_word_matching(self):
        text = "Worked at Google on a project. Skills: Python, C++, JavaScript and SQL."
        found = extract_skills(text, ["Python", "C++", "C", "Java", "JavaScript", "Go", "R", "SQL"])
        self.assertEqual(found, ["Python", "C++", "JavaScript", "SQL"])


if __name__ == "__main__":
    unittest.main()
