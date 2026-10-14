##################################################
#                   IMPORTS                      #
##################################################

# CareerPath AI - AI-Based Career Guidance Expert System
# Built on the open-source CareerRecommendationSystem by Abhinav Jha (MIT License).

from pathlib import Path

import pandas as pd
import streamlit as st

from modules.agent import CareerAgent
from modules.expert_rules import (
    CONDITION_LABELS,
    EDUCATION_LEVELS,
    INTERESTS,
    PREFERENCES,
    RULE_SHARE,
    SKILL_SHARE,
    SKILL_TARGET,
    SOFT_SKILLS,
    SUBJECTS,
    SUPPORTED_CAREERS,
)
from modules.helpers import (
    extract_skills,
    fcourse_recommend,
    load_skills,
    skills_list,
    text_from_pdf,
)

st.set_page_config(
    page_title="CareerPath AI",
    page_icon="🎯",
    layout="wide",
)

# Paths are built from this file's location so the app also starts when it is
# launched from another folder (e.g. `streamlit run path/to/app.py`).
DATA_DIR = Path(__file__).resolve().parent / "data"


@st.cache_data
def load_data():
    careers = load_skills(DATA_DIR / "careers.json")
    career_info = load_skills(DATA_DIR / "career_info.json")
    courses = load_skills(DATA_DIR / "courses.json")
    master_skills = load_skills(DATA_DIR / "skills.json")
    roadmaps = load_skills(DATA_DIR / "roadmaps.json")
    return careers, career_info, courses, master_skills, roadmaps


careers_data, career_info_data, courses_data, master_skills_data, roadmaps_data = load_data()
all_skill_names = skills_list(master_skills_data)

# Technical skills offered in the form = skills required by the supported careers.
_soft = {name.lower() for name in SOFT_SKILLS}
TECH_SKILL_OPTIONS = sorted(
    {
        skill
        for item in careers_data
        if item["career"] in SUPPORTED_CAREERS
        for skill in item["skills"]
        if skill.lower() not in _soft
    },
    key=str.lower,
)

agent = CareerAgent(careers_data, career_info_data, roadmaps_data)


##################################################
#                    SIDEBAR                     #
##################################################

with st.sidebar:
    st.header("About")
    st.write(
        "CareerPath AI is a rule-based **expert system**. It matches a student's "
        "profile against IF-THEN rules and a career-skills dataset, then explains "
        "every recommendation."
    )
    st.write(f"This prototype supports **{len(SUPPORTED_CAREERS)} careers**:")
    for name in SUPPORTED_CAREERS:
        st.markdown(f"- {name}")
    st.caption("Runs fully offline. No API keys or external AI services.")


##################################################
#                     TITLE                      #
##################################################

st.markdown(
    "<h1 style='text-align: center; margin-bottom: 0;'>🎯 CareerPath AI</h1>"
    "<p style='text-align: center; font-size: 1.25rem; margin-top: 0;'>"
    "AI-Based Career Guidance Expert System</p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center;'>Tell us about your interests, skills and subjects. "
    "The system infers the <b>top 3 career paths</b> for you, explains why, "
    "shows your skill gaps and gives a learning roadmap.</p>",
    unsafe_allow_html=True,
)

with st.expander("How does the system work?"):
    st.markdown(
        "**Student Input → Student Profile → Agent Controller → Rule-Based Inference "
        "Engine → Career Recommendation → Explanation + Skill Gaps + Roadmap**"
    )
    st.markdown(
        f"1. Your answers become a *student profile*.\n"
        f"2. The *agent controller* sends the profile to the *inference engine*, which "
        f"checks every IF-THEN rule (for example: *programming interest + coding skills "
        f"→ Software Developer*).\n"
        f"3. Each career gets a **rule score** (fired rules) and a **skill score** "
        f"(overlap with the skills the career needs). Compatibility = "
        f"{RULE_SHARE:.0%} rule score + {SKILL_SHARE:.0%} skill score.\n"
        f"4. The three best careers are shown with reasons, skill gaps and a roadmap."
    )

st.divider()


##################################################
#               STUDENT PROFILE FORM             #
##################################################

st.header("1. Student profile")

with st.form("student_profile"):
    left, right = st.columns(2)

    with left:
        education = st.selectbox("Current education level", EDUCATION_LEVELS, index=2)
        interests = st.multiselect("Interests", INTERESTS, placeholder="Choose one or more")
        subjects = st.multiselect("Favourite subjects", SUBJECTS, placeholder="Choose one or more")
        preferences = st.multiselect(
            "Career preferences (what kind of work do you want to do?)",
            PREFERENCES,
            placeholder="Choose one or more",
        )

    with right:
        tech_skills = st.multiselect(
            "Technical skills", TECH_SKILL_OPTIONS, placeholder="Search and choose your skills"
        )
        soft_skills = st.multiselect(
            "Non-technical skills", SOFT_SKILLS, placeholder="Choose one or more"
        )
        extra_skills = st.text_input(
            "Other skills (optional, comma-separated)", placeholder="e.g. Tableau, Docker"
        )
        resume = st.file_uploader("Resume (optional, PDF)", type=["pdf"])
        st.caption("If you upload a resume, skills found in it are added to the ones above.")

    submitted = st.form_submit_button("Get career recommendations", type="primary")

if submitted:
    skills = list(tech_skills) + list(soft_skills)
    skills += [item.strip() for item in extra_skills.split(",") if item.strip()]

    resume_skills = []
    if resume is not None:
        try:
            resume_skills = extract_skills(text_from_pdf(resume), all_skill_names)
        except Exception:
            st.warning(
                "The resume could not be read, so only the skills you selected are used. "
                "(Scanned or image-only PDFs cannot be parsed.)"
            )
    skills += resume_skills

    if not (interests or skills or subjects or preferences):
        st.session_state.pop("result", None)
        st.warning("Please choose at least one interest, skill, subject or preference.")
    else:
        st.session_state["result"] = agent.run(
            {
                "interests": interests,
                "skills": skills,
                "subjects": subjects,
                "education": education,
                "preferences": preferences,
            }
        )
        st.session_state["resume_skills"] = resume_skills


##################################################
#                    RESULTS                     #
##################################################

result = st.session_state.get("result")

if result is None:
    st.info("Fill in the profile above and click **Get career recommendations**.")
elif not result.recommendations:
    st.warning("No career matched the given inputs. Try adding more interests or skills.")
else:
    recs = result.recommendations

    st.divider()
    st.header("2. Your top career recommendations")

    resume_found = st.session_state.get("resume_skills", [])
    if resume_found:
        st.caption(f"Skills detected from your resume: {', '.join(resume_found[:25])}"
                   + (" ..." if len(resume_found) > 25 else ""))

    if len(recs) < 3:
        st.info(
            f"Only {len(recs)} career(s) matched your inputs. "
            "Add more interests, subjects or skills to get more suggestions."
        )

    # ---- recommendation cards ------------------------------------------------
    columns = st.columns(len(recs))
    for column, rec in zip(columns, recs):
        with column:
            with st.container(border=True):
                st.caption(f"RANK #{rec.rank}")
                st.subheader(rec.career)
                st.metric("Compatibility", f"{rec.score:.0f}%")
                st.progress(min(max(rec.score / 100.0, 0.0), 1.0))
                st.caption(
                    f"Difficulty: {rec.difficulty}  |  Typical learning time: {rec.learning_time}"
                )
                if rec.summary_text:
                    st.write(rec.summary_text)

                st.markdown("**Why recommended**")
                st.write(rec.summary)

                st.markdown("**Relevant skills for this career**")
                st.write(", ".join(rec.key_skills))

                st.markdown("**Skills you already have**")
                st.write(", ".join(rec.matched_skills) if rec.matched_skills else "None yet")

                st.markdown("**Skills to improve**")
                st.write(", ".join(rec.skills_to_improve) if rec.skills_to_improve else "None - great match!")

    # ---- explainable results -------------------------------------------------
    st.divider()
    st.header("3. Why were these careers selected?")
    st.caption(
        f"Compatibility = {RULE_SHARE:.0%} x rule score + {SKILL_SHARE:.0%} x skill score. "
        f"Rule score = points of the IF-THEN rules that fired (max 100). "
        f"Skill score = how many of the career's required skills you have "
        f"({SKILL_TARGET} or more = 100)."
    )

    for rec in recs:
        with st.expander(f"#{rec.rank} {rec.career} - {rec.score:.0f}% match", expanded=(rec.rank == 1)):
            st.markdown(
                f"**Score breakdown:** rule score {rec.rule_score:.0f}/100 x {RULE_SHARE:.0%} "
                f"+ skill score {rec.skill_score:.0f}/100 x {SKILL_SHARE:.0%} "
                f"= **{rec.score:.0f}%**"
            )

            if rec.fired_rules:
                st.markdown("**Rules that fired for this career**")
                rows = []
                for fired in rec.fired_rules:
                    matched_text = "; ".join(
                        f"{CONDITION_LABELS[group]}: {', '.join(values)}"
                        for group, values in fired.matched.items()
                    )
                    rows.append(
                        {
                            "Rule": fired.rule_id,
                            "Meaning": fired.name,
                            "Your inputs that matched": matched_text,
                            "Points": fired.points,
                        }
                    )
                st.dataframe(pd.DataFrame(rows), hide_index=True)
            else:
                st.write("No IF-THEN rule fired for this career; it was ranked on skill overlap only.")

            total_required = len(rec.matched_skills) + len(rec.all_missing_skills)
            st.markdown(
                f"**Skills matched:** {len(rec.matched_skills)} of {total_required} skills "
                f"listed for this career"
                + (f" ({', '.join(rec.matched_skills)})" if rec.matched_skills else "")
            )

    with st.expander("Agent activity log"):
        for number, line in enumerate(result.trace, start=1):
            st.write(f"{number}. {line}")

    # ---- roadmap, skill gaps and courses -------------------------------------
    st.divider()
    st.header("4. Learning roadmap")
    st.caption("Open a tab to see the roadmap, skill gaps and courses for that career.")

    tabs = st.tabs([rec.career for rec in recs])
    for tab, rec in zip(tabs, recs):
        with tab:
            if rec.typical_education:
                st.write(
                    f"**Typical entry route:** {rec.typical_education}  \n"
                    f"**Your current level:** {result.profile.education or 'not given'}"
                )

            stage_columns = st.columns(4)
            for stage_column, stage in zip(stage_columns, rec.roadmap):
                with stage_column:
                    with st.container(border=True):
                        st.markdown(f"**{stage['stage']}**")
                        for item in stage["items"]:
                            st.markdown(f"- {item}")

            if rec.all_missing_skills:
                st.info(
                    "Skill gaps to close first: "
                    + ", ".join(rec.all_missing_skills[:6])
                )

            courses = fcourse_recommend(rec.all_missing_skills, courses_data)
            if courses:
                st.markdown("**Recommended courses for your skill gaps**")
                st.dataframe(
                    pd.DataFrame(courses, columns=["Skill", "Course", "Provider", "Link"]),
                    hide_index=True,
                    column_config={
                        "Link": st.column_config.LinkColumn("Course Link", display_text="Open Course 🔗")
                    },
                )
            else:
                st.caption("No courses in the local catalogue match these gap skills yet.")


##################################################
#                     FOOTER                     #
##################################################

st.divider()
st.caption(
    "CareerPath AI is a prototype for academic demonstration. Recommendations come from "
    "simple rules and a local dataset and are not professional career advice. "
    "Built on the open-source CareerRecommendationSystem by Abhinav Jha (MIT License)."
)
