"""
=========================================================
  Placement Readiness Checker & Career Suggestion System
=========================================================
  Indira College of Commerce and Science
  S.Y M.Sc. (Comp.Sci) - Sem IV | Academic Year 2025-26
  Team: Nikhil Ghalme (32), Abhijit Bhujbal (01), Saurabh Gawali (94)

  This tool asks students questions about their education,
  skills, and experience, then provides personalized
  placement readiness analysis and career suggestions.
=========================================================
"""

import pandas as pd
import numpy as np
import os

# Load dataset for benchmarking
DATA_PATH = '/home/nikhil/workspace/bytephase/research/placement_readiness_data.xlsx'
df = pd.read_excel(DATA_PATH)
placed = df[df['Placement Status'] == 'Placed']
unplaced = df[df['Placement Status'] == 'Unplaced']

# ============================================================
# BENCHMARK VALUES (derived from dataset analysis)
# ============================================================
BENCHMARKS = {
    'cgpa': {'low': 6.0, 'avg': 7.22, 'good': 7.5, 'excellent': 8.5},
    'pct_12': {'low': 60, 'avg': 72.8, 'good': 80, 'excellent': 90},
    'pct_10': {'low': 65, 'avg': 78.0, 'good': 85, 'excellent': 92},
    'dsa': {'low': 1, 'avg': 3.14, 'good': 4, 'excellent': 5},
    'oops': {'low': 1, 'avg': 3.33, 'good': 4, 'excellent': 5},
    'communication': {'low': 1, 'avg': 3.28, 'good': 4, 'excellent': 5},
    'english': {'low': 1, 'avg': 3.47, 'good': 4, 'excellent': 5},
    'confidence': {'low': 1, 'avg': 3.01, 'good': 4, 'excellent': 5},
    'salary_avg': 14.25,
    'salary_high': 19.75,
}


def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')


def print_header():
    print("\n" + "=" * 62)
    print("    PLACEMENT READINESS CHECKER & CAREER SUGGESTION SYSTEM")
    print("    Indira College of Commerce and Science")
    print("=" * 62)


def print_section(title):
    print(f"\n{'─' * 62}")
    print(f"  {title}")
    print(f"{'─' * 62}")


def get_input(prompt, valid_options=None, input_type='str'):
    while True:
        try:
            value = input(f"  >> {prompt}: ").strip()
            if input_type == 'int':
                value = int(value)
            elif input_type == 'float':
                value = float(value)
            if valid_options and value not in valid_options:
                print(f"     Please enter one of: {valid_options}")
                continue
            return value
        except ValueError:
            print(f"     Invalid input. Please enter a valid {input_type}.")
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Exiting... Goodbye!")
            exit(0)


def get_rating(prompt):
    return get_input(f"{prompt} (1=Beginner, 2=Basic, 3=Intermediate, 4=Good, 5=Expert)",
                     valid_options=[1, 2, 3, 4, 5], input_type='int')


def score_level(value, benchmark_key):
    b = BENCHMARKS[benchmark_key]
    if value >= b['excellent']:
        return 'Excellent', 100
    elif value >= b['good']:
        return 'Good', 75
    elif value >= b['avg']:
        return 'Average', 50
    elif value >= b['low']:
        return 'Below Average', 25
    else:
        return 'Poor', 10


def color_score(score):
    """Return colored score text for terminal."""
    if score >= 80:
        return f"\033[92m{score}%\033[0m"  # Green
    elif score >= 60:
        return f"\033[93m{score}%\033[0m"  # Yellow
    elif score >= 40:
        return f"\033[33m{score}%\033[0m"  # Orange
    else:
        return f"\033[91m{score}%\033[0m"  # Red


def generate_bar(score, width=30):
    filled = int(score / 100 * width)
    bar = "█" * filled + "░" * (width - filled)
    return bar


# ============================================================
# MAIN QUESTIONNAIRE
# ============================================================
def ask_questions():
    student = {}

    print_header()
    print("\n  Welcome! This tool will assess your placement readiness")
    print("  and provide personalized suggestions to improve your")
    print("  chances of getting placed with a good salary package.\n")
    input("  Press Enter to start the assessment...")

    # ── SECTION 1: Personal & Academic ──
    print_section("SECTION 1: PERSONAL & ACADEMIC INFORMATION")

    student['name'] = get_input("Enter your full name")
    student['branch'] = get_input("Your degree branch",
                                  valid_options=['Computer Science', 'Information Technology',
                                                'Electronics/E&TC', 'Other'])
    student['year'] = get_input("Current academic status",
                                valid_options=['3rd Year', '4th Year', 'Graduate (Unplaced)', 'Placed Graduate'])

    student['cgpa'] = get_input("Your current CGPA (out of 10)", input_type='float')
    while student['cgpa'] < 0 or student['cgpa'] > 10:
        print("     CGPA must be between 0 and 10")
        student['cgpa'] = get_input("Your current CGPA (out of 10)", input_type='float')

    student['pct_12'] = get_input("Your 12th percentage", input_type='float')
    student['pct_10'] = get_input("Your 10th percentage", input_type='float')

    # ── SECTION 2: Technical Skills ──
    print_section("SECTION 2: TECHNICAL SKILLS ASSESSMENT")

    student['dsa'] = get_rating("Rate your DSA (Data Structures & Algorithms) knowledge")
    student['oops'] = get_rating("Rate your Object-Oriented Programming understanding")

    student['coding_solved'] = get_input(
        "How many coding problems have you solved? (0-50 / 50-200 / 200-500 / 500+)",
        valid_options=['0-50', '50-200', '200-500', '500+'])

    student['languages'] = get_input("Programming languages you know (comma-separated, e.g., Python, Java, C++)")
    student['num_languages'] = len([l.strip() for l in student['languages'].split(',') if l.strip()])

    student['backend'] = get_input("Backend technology you know (e.g., Django, Spring Boot, Node.js, Express, Flask, None)")
    student['frontend'] = get_input("Frontend technology you know (e.g., React, Angular, Vue, Basic HTML/CSS only)")

    student['database'] = get_input("Database knowledge (e.g., MySQL, MongoDB, PostgreSQL, None)")

    student['system_design'] = get_input("System Design knowledge level",
                                         valid_options=['None', 'Basic', 'Intermediate', 'Advanced'])

    # ── SECTION 3: Projects & Experience ──
    print_section("SECTION 3: PROJECTS & EXPERIENCE")

    student['fullstack_project'] = get_input("Have you built a Full-Stack project? (Yes/No)",
                                              valid_options=['Yes', 'No'])
    student['projects'] = get_input("How many technical projects completed? (0 / 1-2 / 3-5 / 5+)",
                                     valid_options=['0', '1-2', '3-5', '5+'])
    student['internship'] = get_input("Internship experience",
                                       valid_options=['No Internship', '1 Internship', '2+ Internships'])
    student['opensource'] = get_input("Open source contributions? (Yes/No)",
                                      valid_options=['Yes', 'No'])

    # ── SECTION 4: Soft Skills ──
    print_section("SECTION 4: SOFT SKILLS & INTERVIEW READINESS")

    student['communication'] = get_rating("Rate your Communication Skills")
    student['english'] = get_rating("Rate your English Fluency")
    student['confidence'] = get_rating("Rate your Interview Confidence")
    student['mock_interviews'] = get_input("Have you attended mock interviews? (Yes/No)",
                                            valid_options=['Yes', 'No'])

    # ── SECTION 5: Career Goals ──
    print_section("SECTION 5: CAREER GOALS")

    student['expected_salary'] = get_input("Your expected salary package (in LPA)", input_type='float')
    student['applying'] = get_input("Are you actively applying for IT jobs? (Yes/No)",
                                     valid_options=['Yes', 'No'])

    return student


# ============================================================
# ANALYSIS ENGINE
# ============================================================
def analyze_student(student):
    analysis = {
        'scores': {},
        'strengths': [],
        'weaknesses': [],
        'suggestions': [],
        'overall_score': 0,
        'predicted_placement': '',
        'salary_estimate': ''
    }

    # ── Score each area ──
    # Academics (25% weight)
    cgpa_label, cgpa_score = score_level(student['cgpa'], 'cgpa')
    pct12_label, pct12_score = score_level(student['pct_12'], 'pct_12')
    pct10_label, pct10_score = score_level(student['pct_10'], 'pct_10')
    academic_score = int(cgpa_score * 0.5 + pct12_score * 0.25 + pct10_score * 0.25)
    analysis['scores']['Academics'] = {
        'score': academic_score,
        'details': {
            'CGPA': (student['cgpa'], cgpa_label, cgpa_score),
            '12th %': (student['pct_12'], pct12_label, pct12_score),
            '10th %': (student['pct_10'], pct10_label, pct10_score),
        }
    }

    # Technical Skills (30% weight)
    dsa_label, dsa_score = score_level(student['dsa'], 'dsa')
    oops_label, oops_score = score_level(student['oops'], 'oops')

    coding_scores = {'0-50': 15, '50-200': 40, '200-500': 70, '500+': 100}
    coding_score = coding_scores[student['coding_solved']]

    lang_score = min(100, student['num_languages'] * 20)

    backend_score = 0 if student['backend'].lower() == 'none' else 70
    frontend_score = 20 if 'html' in student['frontend'].lower() else 70
    db_score = 0 if student['database'].lower() == 'none' else 70

    sys_design_scores = {'None': 0, 'Basic': 40, 'Intermediate': 70, 'Advanced': 100}
    sd_score = sys_design_scores[student['system_design']]

    tech_score = int(dsa_score * 0.25 + oops_score * 0.15 + coding_score * 0.25 +
                     lang_score * 0.1 + backend_score * 0.08 + frontend_score * 0.07 +
                     db_score * 0.05 + sd_score * 0.05)
    analysis['scores']['Technical Skills'] = {
        'score': tech_score,
        'details': {
            'DSA': (student['dsa'], dsa_label, dsa_score),
            'OOPS': (student['oops'], oops_label, oops_score),
            'Coding Problems': (student['coding_solved'], '', coding_score),
            'Languages Known': (student['num_languages'], '', lang_score),
        }
    }

    # Projects & Experience (25% weight)
    project_scores = {'0': 0, '1-2': 40, '3-5': 75, '5+': 100}
    proj_score = project_scores[student['projects']]
    fullstack_score = 80 if student['fullstack_project'] == 'Yes' else 0
    intern_scores = {'No Internship': 0, '1 Internship': 60, '2+ Internships': 100}
    intern_score = intern_scores[student['internship']]
    os_score = 70 if student['opensource'] == 'Yes' else 0

    experience_score = int(proj_score * 0.3 + fullstack_score * 0.25 +
                           intern_score * 0.3 + os_score * 0.15)
    analysis['scores']['Projects & Experience'] = {
        'score': experience_score,
        'details': {
            'Projects': (student['projects'], '', proj_score),
            'Full-Stack': (student['fullstack_project'], '', fullstack_score),
            'Internships': (student['internship'], '', intern_score),
            'Open Source': (student['opensource'], '', os_score),
        }
    }

    # Soft Skills (20% weight)
    comm_label, comm_score = score_level(student['communication'], 'communication')
    eng_label, eng_score = score_level(student['english'], 'english')
    conf_label, conf_score = score_level(student['confidence'], 'confidence')
    mock_score = 70 if student['mock_interviews'] == 'Yes' else 10

    soft_score = int(comm_score * 0.3 + eng_score * 0.25 + conf_score * 0.3 + mock_score * 0.15)
    analysis['scores']['Soft Skills'] = {
        'score': soft_score,
        'details': {
            'Communication': (student['communication'], comm_label, comm_score),
            'English': (student['english'], eng_label, eng_score),
            'Confidence': (student['confidence'], conf_label, conf_score),
            'Mock Interviews': (student['mock_interviews'], '', mock_score),
        }
    }

    # ── Overall Score ──
    overall = int(academic_score * 0.25 + tech_score * 0.30 +
                  experience_score * 0.25 + soft_score * 0.20)
    analysis['overall_score'] = overall

    # ── Placement Prediction ──
    if overall >= 75:
        analysis['predicted_placement'] = 'HIGH CHANCE of Placement'
        analysis['placement_color'] = '\033[92m'  # Green
    elif overall >= 55:
        analysis['predicted_placement'] = 'MODERATE CHANCE of Placement'
        analysis['placement_color'] = '\033[93m'  # Yellow
    elif overall >= 35:
        analysis['predicted_placement'] = 'LOW CHANCE - Needs Improvement'
        analysis['placement_color'] = '\033[33m'  # Orange
    else:
        analysis['predicted_placement'] = 'VERY LOW CHANCE - Significant Improvement Needed'
        analysis['placement_color'] = '\033[91m'  # Red

    # ── Salary Estimate ──
    salary_factor = overall / 100
    estimated_min = round(BENCHMARKS['salary_avg'] * salary_factor * 0.6, 2)
    estimated_max = round(BENCHMARKS['salary_high'] * salary_factor * 1.1, 2)
    estimated_min = max(3.0, estimated_min)
    estimated_max = max(estimated_min + 2, estimated_max)
    analysis['salary_range'] = (estimated_min, estimated_max)

    # ── Identify Strengths ──
    if student['cgpa'] >= 8.0:
        analysis['strengths'].append("Strong academic record (CGPA >= 8.0)")
    if student['dsa'] >= 4:
        analysis['strengths'].append("Good DSA knowledge - a key factor in technical interviews")
    if student['coding_solved'] in ['200-500', '500+']:
        analysis['strengths'].append(f"Good coding practice ({student['coding_solved']} problems solved)")
    if student['internship'] in ['1 Internship', '2+ Internships']:
        analysis['strengths'].append(f"Industry experience through internship(s)")
    if student['fullstack_project'] == 'Yes':
        analysis['strengths'].append("Full-stack project experience - valuable for placements")
    if student['projects'] in ['3-5', '5+']:
        analysis['strengths'].append(f"Multiple projects ({student['projects']}) showcase practical skills")
    if student['communication'] >= 4:
        analysis['strengths'].append("Strong communication skills")
    if student['confidence'] >= 4:
        analysis['strengths'].append("Good interview confidence")
    if student['num_languages'] >= 3:
        analysis['strengths'].append(f"Knowledge of {student['num_languages']} programming languages")
    if student['opensource'] == 'Yes':
        analysis['strengths'].append("Open source contributions demonstrate community involvement")
    if student['system_design'] in ['Intermediate', 'Advanced']:
        analysis['strengths'].append(f"System design knowledge ({student['system_design']}) is highly valued")

    # ── Identify Weaknesses & Generate Suggestions ──

    # Academics
    if student['cgpa'] < 6.5:
        analysis['weaknesses'].append(f"Low CGPA ({student['cgpa']}) - many companies have 6.5+ cutoff")
        analysis['suggestions'].append(
            "ACADEMICS: Focus on improving your CGPA. Many companies have a minimum cutoff of 6.5-7.0. "
            "Prioritize core subjects, attend classes regularly, and aim for at least 7.0+ CGPA in remaining semesters.")
    elif student['cgpa'] < 7.5:
        analysis['suggestions'].append(
            "ACADEMICS: Your CGPA is decent but try to push it above 7.5 for better opportunities. "
            "Focus on scoring well in upcoming exams.")

    # DSA
    if student['dsa'] <= 2:
        analysis['weaknesses'].append(f"Weak DSA skills (rated {student['dsa']}/5)")
        analysis['suggestions'].append(
            "DSA (CRITICAL): DSA is the #1 factor in technical interviews. Start with:\n"
            "     - Learn Arrays, Strings, Linked Lists, Stacks, Queues (Week 1-4)\n"
            "     - Trees, Graphs, Hashing, Sorting algorithms (Week 5-8)\n"
            "     - Dynamic Programming, Greedy, Backtracking (Week 9-12)\n"
            "     - Practice on LeetCode/GeeksforGeeks daily. Target 2-3 problems/day.\n"
            "     - Follow Striver's SDE Sheet or NeetCode 150 for structured prep.")
    elif student['dsa'] == 3:
        analysis['suggestions'].append(
            "DSA: You have intermediate DSA knowledge. To level up:\n"
            "     - Focus on Dynamic Programming, Graphs, and advanced Tree problems.\n"
            "     - Solve medium/hard LeetCode problems. Target 200+ total problems.\n"
            "     - Practice timed contests on Codeforces/LeetCode weekly.")

    # Coding Practice
    if student['coding_solved'] == '0-50':
        analysis['weaknesses'].append("Very few coding problems solved (0-50)")
        analysis['suggestions'].append(
            "CODING PRACTICE (URGENT): You need to solve more problems. Data shows students\n"
            "     with 200+ problems solved have significantly higher placement rates.\n"
            "     - Start with easy problems on LeetCode/HackerRank (2-3 per day)\n"
            "     - Gradually move to medium problems\n"
            "     - Target: 200+ problems in next 3 months\n"
            "     - Topic-wise: Arrays(30), Strings(20), LinkedList(15), Trees(20),\n"
            "       DP(25), Graphs(20), Binary Search(15), others(55+)")
    elif student['coding_solved'] == '50-200':
        analysis['suggestions'].append(
            "CODING PRACTICE: Good start! Push towards 300+ problems.\n"
            "     - Focus on medium-level problems now.\n"
            "     - Practice company-specific questions from LeetCode premium.")

    # OOPS
    if student['oops'] <= 2:
        analysis['weaknesses'].append(f"Weak OOPS understanding (rated {student['oops']}/5)")
        analysis['suggestions'].append(
            "OOPS: Object-Oriented Programming is asked in almost every interview.\n"
            "     - Master: Encapsulation, Inheritance, Polymorphism, Abstraction\n"
            "     - Learn: SOLID principles, Design Patterns (Singleton, Factory, Observer)\n"
            "     - Practice: Implement real-world examples (Library System, ATM Machine)\n"
            "     - Language: Pick Java or C++ and master OOPS concepts in it.")

    # Programming Languages
    if student['num_languages'] < 2:
        analysis['weaknesses'].append("Knowledge of only 1 programming language")
        analysis['suggestions'].append(
            "LANGUAGES: Learn at least 2-3 languages. Recommended:\n"
            "     - Python (versatile, ML, scripting, automation)\n"
            "     - Java/C++ (core CS, competitive programming, enterprise)\n"
            "     - JavaScript (web development, full-stack)")

    # Backend
    if student['backend'].lower() == 'none':
        analysis['weaknesses'].append("No backend technology knowledge")
        analysis['suggestions'].append(
            "BACKEND DEVELOPMENT: Backend skills are essential for most IT roles.\n"
            "     - Start with one: Django(Python), Spring Boot(Java), or Node.js/Express(JS)\n"
            "     - Build REST APIs, learn authentication, database integration\n"
            "     - Create at least 2 backend projects for your resume.")

    # Frontend
    if 'html' in student['frontend'].lower() or student['frontend'].lower() == 'none':
        analysis['suggestions'].append(
            "FRONTEND: Move beyond basic HTML/CSS.\n"
            "     - Learn React.js (most in-demand) or Angular\n"
            "     - Build responsive web apps with modern frameworks\n"
            "     - Learn state management (Redux/Context API).")

    # Database
    if student['database'].lower() == 'none':
        analysis['weaknesses'].append("No database knowledge")
        analysis['suggestions'].append(
            "DATABASE: Database knowledge is fundamental.\n"
            "     - Learn SQL (MySQL/PostgreSQL) - practice joins, subqueries, indexing\n"
            "     - Learn one NoSQL database (MongoDB)\n"
            "     - Understand database design and normalization.")

    # System Design
    if student['system_design'] == 'None':
        analysis['suggestions'].append(
            "SYSTEM DESIGN: Start learning basics of system design.\n"
            "     - Learn: REST APIs, database design, caching, load balancing\n"
            "     - Study: URL shortener, chat system, notification service designs\n"
            "     - Resources: 'System Design Interview' book, Gaurav Sen YouTube channel.")

    # Projects
    if student['projects'] in ['0', '1-2']:
        analysis['weaknesses'].append(f"Too few projects ({student['projects']})")
        analysis['suggestions'].append(
            "PROJECTS (IMPORTANT): Projects are what make your resume stand out.\n"
            "     - Build 3-5 meaningful projects. Suggested ideas:\n"
            "       1. E-commerce/Food Delivery app (Full-stack)\n"
            "       2. Chat application with real-time messaging (WebSocket)\n"
            "       3. ML-based project (Prediction/Classification system)\n"
            "       4. API-based project (Weather app, News aggregator)\n"
            "       5. Portfolio website showcasing all your projects\n"
            "     - Deploy projects on GitHub with proper README files.\n"
            "     - Host live demos on Vercel/Netlify/Heroku.")

    # Full-Stack
    if student['fullstack_project'] == 'No':
        analysis['suggestions'].append(
            "FULL-STACK PROJECT: Build at least one complete full-stack project.\n"
            "     - Frontend (React/Angular) + Backend (Node/Django) + Database (MongoDB/MySQL)\n"
            "     - Include: User auth, CRUD operations, API integration, deployment\n"
            "     - This single project can be your strongest resume point.")

    # Internship
    if student['internship'] == 'No Internship':
        analysis['weaknesses'].append("No internship experience")
        analysis['suggestions'].append(
            "INTERNSHIP (HIGH PRIORITY): Students with internships have 15-25% higher\n"
            "     placement rates and salary offers.\n"
            "     - Apply on: Internshala, LinkedIn, AngelList, company career pages\n"
            "     - Even a 2-month remote internship adds value\n"
            "     - Target: At least 1 internship before final placement season\n"
            "     - Alternatively: Freelance projects can also count as experience.")

    # Open Source
    if student['opensource'] == 'No':
        analysis['suggestions'].append(
            "OPEN SOURCE: Contributing to open source shows initiative and collaboration.\n"
            "     - Start with 'good first issue' labels on GitHub\n"
            "     - Contribute to popular projects in your tech stack\n"
            "     - Even documentation fixes count as contributions.")

    # Communication
    if student['communication'] <= 2:
        analysis['weaknesses'].append(f"Weak communication skills (rated {student['communication']}/5)")
        analysis['suggestions'].append(
            "COMMUNICATION (CRITICAL FOR INTERVIEWS):\n"
            "     - Practice explaining technical concepts to non-tech friends\n"
            "     - Join speaking clubs or group discussions\n"
            "     - Record yourself answering interview questions and review\n"
            "     - Watch YouTube videos on 'how to explain projects in interviews'.")

    # English
    if student['english'] <= 2:
        analysis['weaknesses'].append(f"Low English fluency (rated {student['english']}/5)")
        analysis['suggestions'].append(
            "ENGLISH FLUENCY: Important for professional communication.\n"
            "     - Read English articles/blogs daily (30 mins)\n"
            "     - Listen to English podcasts/news\n"
            "     - Practice speaking in English with peers\n"
            "     - Use apps like Duolingo or watch English content with subtitles.")

    # Interview Confidence
    if student['confidence'] <= 2:
        analysis['weaknesses'].append(f"Low interview confidence (rated {student['confidence']}/5)")
        analysis['suggestions'].append(
            "INTERVIEW CONFIDENCE:\n"
            "     - Practice mock interviews (use Pramp, InterviewBit, or peers)\n"
            "     - Prepare answers for common HR questions (Tell me about yourself, etc.)\n"
            "     - Practice the STAR method for behavioral questions\n"
            "     - Research companies before interviews.")

    # Mock Interviews
    if student['mock_interviews'] == 'No':
        analysis['suggestions'].append(
            "MOCK INTERVIEWS: Attend mock interviews to build confidence.\n"
            "     - Use platforms: Pramp (free), InterviewBit, peer mock sessions\n"
            "     - Practice both technical and HR rounds\n"
            "     - Get feedback and improve on weak areas.")

    # Not actively applying
    if student['applying'] == 'No' and student['year'] in ['4th Year', 'Graduate (Unplaced)']:
        analysis['suggestions'].append(
            "JOB APPLICATIONS: You should be actively applying!\n"
            "     - Create profiles on: LinkedIn, Naukri, Indeed, AngelList\n"
            "     - Apply to at least 5-10 companies per week\n"
            "     - Tailor your resume for each application\n"
            "     - Follow up on applications after 1 week.")

    # Salary expectation check
    if student['expected_salary'] > analysis['salary_range'][1] + 5:
        analysis['suggestions'].append(
            f"SALARY EXPECTATIONS: Your expected salary ({student['expected_salary']} LPA) may be\n"
            f"     higher than realistic based on your current profile. The dataset average\n"
            f"     is ~14.25 LPA for placed students. Focus on building skills first\n"
            f"     and the salary will follow. For higher packages, target product-based companies.")

    return analysis


# ============================================================
# DISPLAY RESULTS
# ============================================================
def display_results(student, analysis):
    clear_screen()

    print("\n" + "=" * 62)
    print("         PLACEMENT READINESS ANALYSIS REPORT")
    print("=" * 62)
    print(f"\n  Student: {student['name']}")
    print(f"  Branch:  {student['branch']} | Status: {student['year']}")
    print(f"  CGPA:    {student['cgpa']} | 12th: {student['pct_12']}% | 10th: {student['pct_10']}%")

    # ── Overall Score ──
    print_section("OVERALL PLACEMENT READINESS SCORE")
    score = analysis['overall_score']
    bar = generate_bar(score, 40)
    print(f"\n  {bar}  {color_score(score)}")
    print(f"\n  Prediction: {analysis['placement_color']}{analysis['predicted_placement']}\033[0m")
    print(f"  Estimated Salary Range: {analysis['salary_range'][0]:.1f} - {analysis['salary_range'][1]:.1f} LPA")

    # ── Category-wise Scores ──
    print_section("CATEGORY-WISE BREAKDOWN")
    for category, data in analysis['scores'].items():
        bar = generate_bar(data['score'], 25)
        print(f"\n  {category}: {bar} {color_score(data['score'])}")
        for detail_name, (value, label, sc) in data['details'].items():
            status = f"({label})" if label else ""
            print(f"    - {detail_name}: {value} {status}")

    # ── Strengths ──
    if analysis['strengths']:
        print_section("YOUR STRENGTHS")
        for i, s in enumerate(analysis['strengths'], 1):
            print(f"  {i}. {s}")

    # ── Weaknesses ──
    if analysis['weaknesses']:
        print_section("AREAS OF CONCERN")
        for i, w in enumerate(analysis['weaknesses'], 1):
            print(f"  {i}. {w}")

    # ── Suggestions ──
    print_section("PERSONALIZED SUGGESTIONS & ACTION PLAN")
    if analysis['suggestions']:
        for i, s in enumerate(analysis['suggestions'], 1):
            print(f"\n  [{i}] {s}")
    else:
        print("\n  Great job! You're well-prepared. Keep practicing and stay consistent.")
        print("  Focus on applying to companies and attending interviews.")

    # ── Priority Action Items ──
    print_section("TOP 3 PRIORITY ACTIONS")
    priorities = analysis['suggestions'][:3] if analysis['suggestions'] else []
    if priorities:
        for i, p in enumerate(priorities, 1):
            action = p.split(':')[0] if ':' in p else p[:40]
            print(f"  {i}. Focus on: {action}")
    else:
        print("  You're on the right track! Keep going.")

    # ── Comparison with Dataset ──
    print_section("HOW YOU COMPARE (vs 1000 students in dataset)")
    placed_cgpa = placed['CGPA (Out of 10)'].mean()
    print(f"  Your CGPA ({student['cgpa']}) vs Placed Avg ({placed_cgpa:.2f}):  "
          f"{'Above' if student['cgpa'] >= placed_cgpa else 'Below'} average")
    print(f"  Your DSA ({student['dsa']}/5) vs Placed Avg ({placed['DSA Knowledge (1-5)'].mean():.1f}/5):  "
          f"{'Above' if student['dsa'] >= placed['DSA Knowledge (1-5)'].mean() else 'Below'} average")
    print(f"  Your Communication ({student['communication']}/5) vs Placed Avg ({placed['Communication Skill (1-5)'].mean():.1f}/5):  "
          f"{'Above' if student['communication'] >= placed['Communication Skill (1-5)'].mean() else 'Below'} average")
    print(f"  Your Expected Salary ({student['expected_salary']} LPA) vs Actual Avg ({placed['Salary Package (LPA)'].mean():.2f} LPA)")

    print("\n" + "=" * 62)
    print("  Thank you for using the Placement Readiness Checker!")
    print("  Work on the suggestions above and reassess in 30 days.")
    print("=" * 62 + "\n")


# ============================================================
# RUN
# ============================================================
if __name__ == '__main__':
    try:
        student_data = ask_questions()
        analysis_result = analyze_student(student_data)
        display_results(student_data, analysis_result)
    except (EOFError, KeyboardInterrupt):
        print("\n\n  Exiting... Goodbye!\n")
