# 🎯 CareerPath AI — AI-Based Career Guidance Expert System

A small, offline prototype that recommends suitable career paths to students from their **interests, skills, favourite subjects, education level and career preferences**, and explains every recommendation.

> Built on the open-source [CareerRecommendationSystem](https://github.com/abhinavxjha/CareerRecommendationSystem) by **Abhinav Jha** (MIT License). Its career, skill, career-info and course datasets and its resume-parsing helpers are reused. See [License](#license).

---

## Overview

The student fills in a profile form. A lightweight **agent controller** passes the profile to a **rule-based inference engine**, which scores 14 supported careers and returns the top 3 with reasons, skill gaps and a learning roadmap.

```
Student Input → Student Profile → Agent Controller → Rule-Based Inference Engine
              → Career Recommendation → Explanation + Skill Gaps + Roadmap
```

Everything runs locally. **No API keys, no paid services, no external AI.**

## Main features

- **Student profile form** — education level, interests, favourite subjects, career preferences, technical and non-technical skills, optional extra skills and optional PDF resume (skills are detected automatically).
- **Top 3 career recommendations** — each with a compatibility percentage, why it was recommended, relevant skills, skills you already have and skills to improve.
- **Expert system** — IF-THEN rules kept in one readable file (`modules/expert_rules.py`).
- **Explainable results** — for every career, the rules that fired, which of your inputs matched them, and the exact score breakdown.
- **Learning roadmap** — four stages per career (Fundamentals → Core skills → Projects and practice → Portfolio and job preparation), plus recommended courses for your skill gaps.

## Technologies used

Python · Streamlit · Pandas / NumPy · pdfplumber (resume parsing) · JSON datasets

## Install

Python 3.11 or newer is recommended (the project's devcontainer uses 3.11).

```bash
git clone https://github.com/abhinavxjha/CareerRecommendationSystem.git
cd CareerRecommendationSystem
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

The app opens at <http://localhost:8501>.

## Project structure

```
app.py                       Streamlit interface
modules/
  expert_rules.py            Form options, scoring settings and the IF-THEN rules
  inference_engine.py        Rule-based inference engine (fires rules, scores careers)
  agent.py                   Agent controller: perceive -> reason -> act
  helpers.py                 Original helpers (data loading, resume parsing, courses)
data/
  careers.json               Careers and their required skills (original dataset)
  career_info.json           Difficulty and learning time (original dataset)
  courses.json               Course catalogue per skill (original dataset)
  skills.json                Master skill list for resume parsing (original dataset)
  roadmaps.json              4-stage roadmaps for the 14 supported careers (new)
tests/test_expert_system.py  Automated checks for the expert system
```

## How the expert system makes recommendations

1. **Rules.** Each rule has conditions on interests, skills, subjects, preferences or education. A condition is met if the student has *at least one* of the listed values; a rule **fires** only if *all* its conditions are met. Example:

   | Rule | IF | THEN |
   |---|---|---|
   | SD1 | interest *Programming & software development* **and** a coding skill (Python, Java, C++ …) | + 40 points for **Software Developer** |
   | DA1 | interest *Data analysis & statistics* **and** subject *Mathematics* or *Statistics* | + 40 points for **Data Analyst** |
   | UX1 | interest *Design & creativity* **and** a design skill (Creativity, Figma …) | + 40 points for **UI UX Designer** |

   The rules of each career add up to 100 points.
2. **Skill overlap.** The student's skills are compared with the skills the career needs in `data/careers.json` (matching ignores upper/lower case). Having 8 or more of them gives the full skill score.
3. **Compatibility** = 60 % × rule score + 40 % × skill score. Careers below 10 % are not recommended, and the best three are shown.
4. **Explanation.** The app lists the fired rules, the student inputs that triggered them, the score breakdown, and the missing skills (the skill gaps).

The same input always gives the same result — nothing is random.

## Demo scenarios

Choose these in the form (education level: Undergraduate unless stated):

| Profile | Inputs | Top result |
|---|---|---|
| Aspiring developer | Interest: Programming; subjects: Computer Science, Mathematics; preference: Building apps; skills: Python, Java, Git, SQL, Data Structures | Software Developer (85 %) |
| Data enthusiast | Interest: Data analysis; subjects: Mathematics, Statistics; preference: Working with data; skills: Excel, SQL, Statistics, Power BI, Critical Thinking | Data Analyst (85 %) |
| Creative designer (High School) | Interest: Design & creativity; subject: Art & Design; preference: Creative & visual work; skills: Figma, Typography, Creativity, Communication | UI UX Designer (70 %) |

Changing the inputs changes the ranking, the explanation and the roadmap.

## Run the tests

```bash
python -m unittest tests.test_expert_system -v
```

These checks need only Python, pandas, numpy and pdfplumber (not Streamlit). They verify the rule base, that different profiles give different and sensible rankings, and the resume skill extraction.

## Current prototype limitations

- Only **14 careers** are supported by the rules and roadmaps (the other careers in `data/careers.json` are not used yet).
- Rules and weights are hand-written examples, not learned from real student data, and are not professional career advice.
- Skill matching is by exact skill name (ignoring case); synonyms are not understood.
- Resume parsing works only for text PDFs (not scanned images) and uses keyword matching.
- Roadmaps are generic per career; only the course suggestions depend on your skill gaps.
- No login, database, chatbot or deployment.

**Future scope:** extend the rules to all 188 careers, learn rule weights from data, an AI mentor chatbot, downloadable PDF career report, saved profiles.

---

## Author

Original project: **Abhinav Jha** — B.Tech Computer Science & Engineering, Jaypee University of Information Technology, Solan.

<a id="license"></a>
## License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 Abhinav Jha

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
