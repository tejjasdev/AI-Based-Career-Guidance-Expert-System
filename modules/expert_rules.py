"""
Knowledge base for the CareerPath AI expert system.

Everything the inference engine "knows" lives in this one file so it is easy
to read, explain and edit during a demonstration:

  1. The answer options shown in the student profile form.
  2. The scoring settings.
  3. The IF-THEN rules (RULES) that link student inputs to careers.

HOW A RULE WORKS
----------------
Each rule has an "if" part with one or more condition groups
(interests, skills, subjects, preferences, education).

* A group is satisfied when the student has AT LEAST ONE of the listed values.
* A rule FIRES only when ALL of its groups are satisfied.
* A fired rule adds its "weight" points to its career.
* The weights of all rules of one career add up to 100.

Example (the first example from the project brief):
    "Programming interest + coding skills -> Software Developer"
    = interest 'Programming & software development'
      AND at least one coding skill (Python, Java, C++ ...)
"""

# ---------------------------------------------------------------------------
# 1. Options shown in the student profile form
# ---------------------------------------------------------------------------

I_PROG = "Programming & software development"
I_DATA = "Data analysis & statistics"
I_AI = "Artificial intelligence & machine learning"
I_DESIGN = "Design & creativity"
I_WEB = "Web & mobile apps"
I_SEC = "Cybersecurity & ethical hacking"
I_CLOUD = "Cloud & infrastructure"
I_BIZ = "Business & management"
I_MKT = "Marketing & content"
I_HW = "Electronics & hardware"

INTERESTS = [I_PROG, I_DATA, I_AI, I_DESIGN, I_WEB, I_SEC, I_CLOUD, I_BIZ, I_MKT, I_HW]

S_MATH = "Mathematics"
S_STAT = "Statistics"
S_CS = "Computer Science"
S_PHY = "Physics"
S_ECO = "Economics"
S_BUS = "Business Studies"
S_ENG = "English / Communication"
S_ART = "Art & Design"
S_ELEC = "Electronics"

SUBJECTS = [S_MATH, S_STAT, S_CS, S_PHY, S_ECO, S_BUS, S_ENG, S_ART, S_ELEC]

E_HS = "High School"
E_DIP = "Diploma"
E_UG = "Undergraduate"
E_PG = "Postgraduate"

EDUCATION_LEVELS = [E_HS, E_DIP, E_UG, E_PG]

P_BUILD = "Building apps & software"
P_DATA = "Working with data"
P_CREATIVE = "Creative & visual work"
P_LEAD = "Leading & communicating with people"
P_SEC = "Protecting systems & solving puzzles"
P_HW = "Working with hardware & devices"

PREFERENCES = [P_BUILD, P_DATA, P_CREATIVE, P_LEAD, P_SEC, P_HW]

# Non-technical (soft) skills offered in the form.
SOFT_SKILLS = [
    "Communication",
    "Creativity",
    "Problem Solving",
    "Critical Thinking",
    "Teamwork",
    "Leadership",
    "Attention to Detail",
    "Curiosity",
]

# ---------------------------------------------------------------------------
# 2. Scoring settings
# ---------------------------------------------------------------------------
# Compatibility % = RULE_SHARE * (rule score, 0-100) + SKILL_SHARE * (skill score, 0-100)
#
# * rule score  = points of the fired rules of that career (max 100)
# * skill score = how many of the career's required skills (data/careers.json)
#                 the student already has. Having SKILL_TARGET or more of them
#                 gives the full 100.

RULE_SHARE = 0.6
SKILL_SHARE = 0.4
SKILL_TARGET = 8
TOP_N = 3
# Careers scoring below this are not recommended. This stops a career being
# suggested only because of a weak, generic signal such as the education level.
MIN_SCORE = 10.0

# Names used in explanations for each condition group.
CONDITION_LABELS = {
    "interests": "interest",
    "skills": "skill",
    "subjects": "favourite subject",
    "preferences": "career preference",
    "education": "education level",
}

# ---------------------------------------------------------------------------
# 3. The rules
# ---------------------------------------------------------------------------

RULES = [
    # ---- Software Developer -------------------------------------------------
    {"id": "SD1", "career": "Software Developer", "weight": 40,
     "name": "Programming interest + coding skills",
     "if": {"interests": [I_PROG],
            "skills": ["Python", "Java", "C++", "C", "JavaScript"]}},
    {"id": "SD2", "career": "Software Developer", "weight": 20,
     "name": "Core computer-science skills",
     "if": {"skills": ["Data Structures", "Algorithms", "Object-Oriented Programming", "Git"]}},
    {"id": "SD3", "career": "Software Developer", "weight": 20,
     "name": "Strong computer science / maths subjects",
     "if": {"subjects": [S_CS, S_MATH]}},
    {"id": "SD4", "career": "Software Developer", "weight": 20,
     "name": "Prefers building software",
     "if": {"preferences": [P_BUILD]}},

    # ---- Frontend Developer -------------------------------------------------
    {"id": "FE1", "career": "Frontend Developer", "weight": 40,
     "name": "Web interest + front-end skills",
     "if": {"interests": [I_WEB],
            "skills": ["HTML", "CSS", "JavaScript", "React", "TypeScript"]}},
    {"id": "FE2", "career": "Frontend Developer", "weight": 20,
     "name": "Knows front-end frameworks or tooling",
     "if": {"skills": ["React", "Redux", "Vue.js", "Next.js", "Tailwind CSS", "Responsive Design"]}},
    {"id": "FE3", "career": "Frontend Developer", "weight": 20,
     "name": "Design interest + visual work preference",
     "if": {"interests": [I_DESIGN], "preferences": [P_CREATIVE]}},
    {"id": "FE4", "career": "Frontend Developer", "weight": 20,
     "name": "Prefers building software",
     "if": {"preferences": [P_BUILD]}},

    # ---- Backend Developer --------------------------------------------------
    {"id": "BE1", "career": "Backend Developer", "weight": 40,
     "name": "Programming / infrastructure interest + server-side languages",
     "if": {"interests": [I_PROG, I_CLOUD],
            "skills": ["Python", "Java", "Node.js", "Go", "Django", "FastAPI", "Spring Boot"]}},
    {"id": "BE2", "career": "Backend Developer", "weight": 25,
     "name": "Database skills",
     "if": {"skills": ["SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Databases"]}},
    {"id": "BE3", "career": "Backend Developer", "weight": 10,
     "name": "Computer science subject",
     "if": {"subjects": [S_CS]}},
    {"id": "BE4", "career": "Backend Developer", "weight": 15,
     "name": "Prefers building software",
     "if": {"preferences": [P_BUILD]}},
    {"id": "BE5", "career": "Backend Developer", "weight": 10,
     "name": "Back-end tooling skills",
     "if": {"skills": ["REST APIs", "APIs", "Docker", "Linux", "Authentication", "Django",
                       "FastAPI", "Spring Boot", "Node.js"]}},

    # ---- Mobile App Developer -----------------------------------------------
    {"id": "MA1", "career": "Mobile App Developer", "weight": 45,
     "name": "Web & mobile interest + mobile development skills",
     "if": {"interests": [I_WEB],
            "skills": ["Kotlin", "Swift", "Flutter", "Dart", "React Native", "Android", "iOS", "Java"]}},
    {"id": "MA2", "career": "Mobile App Developer", "weight": 20,
     "name": "Programming interest + app languages",
     "if": {"interests": [I_PROG],
            "skills": ["Java", "Kotlin", "Swift", "Dart", "JavaScript"]}},
    {"id": "MA3", "career": "Mobile App Developer", "weight": 20,
     "name": "Wants to build or create apps",
     "if": {"preferences": [P_BUILD, P_CREATIVE]}},
    {"id": "MA4", "career": "Mobile App Developer", "weight": 15,
     "name": "Computer science subject",
     "if": {"subjects": [S_CS]}},

    # ---- Data Analyst -------------------------------------------------------
    {"id": "DA1", "career": "Data Analyst", "weight": 40,
     "name": "Data analysis interest + mathematics",
     "if": {"interests": [I_DATA], "subjects": [S_MATH, S_STAT]}},
    {"id": "DA2", "career": "Data Analyst", "weight": 30,
     "name": "Analytics tool skills",
     "if": {"skills": ["Excel", "SQL", "Power BI", "Tableau", "Statistics", "Pandas",
                       "Data Visualization"]}},
    {"id": "DA3", "career": "Data Analyst", "weight": 20,
     "name": "Prefers working with data",
     "if": {"preferences": [P_DATA]}},
    {"id": "DA4", "career": "Data Analyst", "weight": 10,
     "name": "Analytical soft skills",
     "if": {"skills": ["Critical Thinking", "Attention to Detail", "Problem Solving"]}},

    # ---- Data Scientist -----------------------------------------------------
    {"id": "DS1", "career": "Data Scientist", "weight": 30,
     "name": "Data / AI interest + maths or statistics",
     "if": {"interests": [I_DATA, I_AI], "subjects": [S_MATH, S_STAT]}},
    {"id": "DS2", "career": "Data Scientist", "weight": 30,
     "name": "Data science tool skills",
     "if": {"skills": ["Python", "R", "Machine Learning", "Scikit-learn", "Pandas",
                       "Statistics", "Probability"]}},
    {"id": "DS3", "career": "Data Scientist", "weight": 15,
     "name": "Prefers working with data",
     "if": {"preferences": [P_DATA]}},
    {"id": "DS4", "career": "Data Scientist", "weight": 10,
     "name": "Degree-level study (maths-heavy path)",
     "if": {"education": [E_UG, E_PG]}},
    {"id": "DS5", "career": "Data Scientist", "weight": 15,
     "name": "Curious, analytical mindset",
     "if": {"skills": ["Critical Thinking", "Problem Solving", "Curiosity"]}},

    # ---- ML Engineer --------------------------------------------------------
    {"id": "ML1", "career": "ML Engineer", "weight": 40,
     "name": "AI interest + machine-learning skills",
     "if": {"interests": [I_AI],
            "skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
                       "Scikit-learn"]}},
    {"id": "ML2", "career": "ML Engineer", "weight": 20,
     "name": "Programming interest + engineering skills",
     "if": {"interests": [I_PROG],
            "skills": ["Python", "Docker", "REST APIs", "FastAPI", "Git"]}},
    {"id": "ML3", "career": "ML Engineer", "weight": 20,
     "name": "Maths, statistics or computer science subjects",
     "if": {"subjects": [S_MATH, S_STAT, S_CS]}},
    {"id": "ML4", "career": "ML Engineer", "weight": 10,
     "name": "Degree-level study",
     "if": {"education": [E_UG, E_PG]}},
    {"id": "ML5", "career": "ML Engineer", "weight": 10,
     "name": "Prefers building things with data",
     "if": {"preferences": [P_BUILD, P_DATA]}},

    # ---- UI UX Designer -----------------------------------------------------
    {"id": "UX1", "career": "UI UX Designer", "weight": 40,
     "name": "Creativity + design interest",
     "if": {"interests": [I_DESIGN],
            "skills": ["Creativity", "Figma", "Wireframing", "Prototyping", "Color Theory",
                       "Typography"]}},
    {"id": "UX2", "career": "UI UX Designer", "weight": 15,
     "name": "Art & design subject",
     "if": {"subjects": [S_ART]}},
    {"id": "UX3", "career": "UI UX Designer", "weight": 20,
     "name": "Prefers creative and visual work",
     "if": {"preferences": [P_CREATIVE]}},
    {"id": "UX4", "career": "UI UX Designer", "weight": 15,
     "name": "Design tool skills",
     "if": {"skills": ["Figma", "Wireframing", "Prototyping", "User Research", "Usability Testing",
                       "Design Systems", "Typography", "Color Theory"]}},
    {"id": "UX5", "career": "UI UX Designer", "weight": 10,
     "name": "Collaboration and detail skills",
     "if": {"skills": ["Communication", "Teamwork", "Attention to Detail"]}},

    # ---- Cyber Security Analyst ---------------------------------------------
    {"id": "CS1", "career": "Cyber Security Analyst", "weight": 40,
     "name": "Security interest + systems / security skills",
     "if": {"interests": [I_SEC],
            "skills": ["Linux", "Networking", "Network Security", "Python", "Wireshark", "Firewalls",
                       "Encryption", "Penetration Testing"]}},
    {"id": "CS2", "career": "Cyber Security Analyst", "weight": 20,
     "name": "Likes protecting systems and solving puzzles",
     "if": {"preferences": [P_SEC]}},
    {"id": "CS3", "career": "Cyber Security Analyst", "weight": 10,
     "name": "Computer science subject",
     "if": {"subjects": [S_CS]}},
    {"id": "CS4", "career": "Cyber Security Analyst", "weight": 15,
     "name": "Analytical soft skills",
     "if": {"skills": ["Critical Thinking", "Problem Solving", "Attention to Detail"]}},
    {"id": "CS5", "career": "Cyber Security Analyst", "weight": 15,
     "name": "Infrastructure interest + Linux / networking",
     "if": {"interests": [I_CLOUD], "skills": ["Linux", "Networking"]}},

    # ---- Cloud Engineer -----------------------------------------------------
    {"id": "CL1", "career": "Cloud Engineer", "weight": 45,
     "name": "Cloud interest + cloud / DevOps skills",
     "if": {"interests": [I_CLOUD],
            "skills": ["AWS", "Azure", "Google Cloud Platform", "Docker", "Kubernetes", "Terraform",
                       "Linux"]}},
    {"id": "CL2", "career": "Cloud Engineer", "weight": 20,
     "name": "Infrastructure skills",
     "if": {"skills": ["Linux", "Networking", "CI/CD", "Infrastructure as Code", "Ansible"]}},
    {"id": "CL3", "career": "Cloud Engineer", "weight": 15,
     "name": "Computer science subject",
     "if": {"subjects": [S_CS]}},
    {"id": "CL4", "career": "Cloud Engineer", "weight": 20,
     "name": "Programming interest + automation scripting",
     "if": {"interests": [I_PROG], "skills": ["Python", "Go"]}},

    # ---- Business Analyst ---------------------------------------------------
    {"id": "BA1", "career": "Business Analyst", "weight": 35,
     "name": "Business / data interest + analysis tools",
     "if": {"interests": [I_BIZ, I_DATA],
            "skills": ["Excel", "SQL", "Power BI", "Tableau", "Data Analysis"]}},
    {"id": "BA2", "career": "Business Analyst", "weight": 25,
     "name": "Communication and documentation skills",
     "if": {"skills": ["Communication", "Documentation", "Stakeholder Management",
                       "Requirements Gathering", "Process Mapping"]}},
    {"id": "BA3", "career": "Business Analyst", "weight": 15,
     "name": "Business or economics subject",
     "if": {"subjects": [S_BUS, S_ECO]}},
    {"id": "BA4", "career": "Business Analyst", "weight": 15,
     "name": "Likes leading people or working with data",
     "if": {"preferences": [P_LEAD, P_DATA]}},
    {"id": "BA5", "career": "Business Analyst", "weight": 10,
     "name": "Degree-level study",
     "if": {"education": [E_UG, E_PG]}},

    # ---- Digital Marketing Specialist ---------------------------------------
    {"id": "DM1", "career": "Digital Marketing Specialist", "weight": 40,
     "name": "Marketing interest + marketing skills",
     "if": {"interests": [I_MKT],
            "skills": ["SEO", "Copywriting", "Social Media Marketing", "Content Marketing",
                       "Google Analytics", "Email Marketing", "Ads"]}},
    {"id": "DM2", "career": "Digital Marketing Specialist", "weight": 20,
     "name": "Creative and communication skills",
     "if": {"skills": ["Creativity", "Communication"]}},
    {"id": "DM3", "career": "Digital Marketing Specialist", "weight": 15,
     "name": "English or business subject",
     "if": {"subjects": [S_ENG, S_BUS]}},
    {"id": "DM4", "career": "Digital Marketing Specialist", "weight": 15,
     "name": "Prefers creative work or working with people",
     "if": {"preferences": [P_CREATIVE, P_LEAD]}},
    {"id": "DM5", "career": "Digital Marketing Specialist", "weight": 10,
     "name": "Business or design interest",
     "if": {"interests": [I_BIZ, I_DESIGN]}},

    # ---- Product Manager ----------------------------------------------------
    {"id": "PM1", "career": "Product Manager", "weight": 35,
     "name": "Business interest + product / leadership skills",
     "if": {"interests": [I_BIZ],
            "skills": ["Communication", "Leadership", "Stakeholder Management", "Agile",
                       "Product Strategy", "Market Research"]}},
    {"id": "PM2", "career": "Product Manager", "weight": 25,
     "name": "Likes leading and communicating with people",
     "if": {"preferences": [P_LEAD]}},
    {"id": "PM3", "career": "Product Manager", "weight": 15,
     "name": "Interest in technology, data or design",
     "if": {"interests": [I_PROG, I_DATA, I_DESIGN, I_WEB]}},
    {"id": "PM4", "career": "Product Manager", "weight": 15,
     "name": "Analysis and planning skills",
     "if": {"skills": ["Data Analysis", "SQL", "Excel", "JIRA", "Prioritization Frameworks"]}},
    {"id": "PM5", "career": "Product Manager", "weight": 10,
     "name": "Business, economics or communication subject",
     "if": {"subjects": [S_BUS, S_ECO, S_ENG]}},

    # ---- Embedded Systems Engineer ------------------------------------------
    {"id": "ES1", "career": "Embedded Systems Engineer", "weight": 40,
     "name": "Hardware interest + embedded skills",
     "if": {"interests": [I_HW],
            "skills": ["C", "C++", "Microcontrollers", "Electronics", "RTOS",
                       "Firmware Development"]}},
    {"id": "ES2", "career": "Embedded Systems Engineer", "weight": 20,
     "name": "Electronics or physics subject",
     "if": {"subjects": [S_ELEC, S_PHY]}},
    {"id": "ES3", "career": "Embedded Systems Engineer", "weight": 20,
     "name": "Prefers working with hardware and devices",
     "if": {"preferences": [P_HW]}},
    {"id": "ES4", "career": "Embedded Systems Engineer", "weight": 10,
     "name": "Programming interest + low-level languages",
     "if": {"interests": [I_PROG], "skills": ["C", "C++"]}},
    {"id": "ES5", "career": "Embedded Systems Engineer", "weight": 10,
     "name": "Diploma or degree-level study",
     "if": {"education": [E_DIP, E_UG, E_PG]}},
]

SUPPORTED_CAREERS = sorted({rule["career"] for rule in RULES})
