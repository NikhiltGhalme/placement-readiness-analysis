import pandas as pd
from pydantic import BaseModel, Field
from typing import Literal

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


class StudentInput(BaseModel):
    name: str
    branch: Literal['Computer Science', 'Information Technology', 'Electronics/E&TC', 'Other']
    year: Literal['3rd Year', '4th Year', 'Graduate (Unplaced)', 'Placed Graduate']
    cgpa: float = Field(ge=0, le=10)
    pct_12: float = Field(ge=0, le=100)
    pct_10: float = Field(ge=0, le=100)
    dsa: int = Field(ge=1, le=5)
    oops: int = Field(ge=1, le=5)
    coding_solved: Literal['0-50', '50-200', '200-500', '500+']
    languages: str
    backend: str
    frontend: str
    database: str
    system_design: Literal['None', 'Basic', 'Intermediate', 'Advanced']
    fullstack_project: Literal['Yes', 'No']
    projects: Literal['0', '1-2', '3-5', '5+']
    internship: Literal['No Internship', '1 Internship', '2+ Internships']
    opensource: Literal['Yes', 'No']
    communication: int = Field(ge=1, le=5)
    english: int = Field(ge=1, le=5)
    confidence: int = Field(ge=1, le=5)
    mock_interviews: Literal['Yes', 'No']
    expected_salary: float = Field(ge=0)
    applying: Literal['Yes', 'No']


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


def analyze_student(student: dict) -> dict:
    analysis = {
        'scores': {},
        'strengths': [],
        'weaknesses': [],
        'suggestions': [],
        'overall_score': 0,
        'predicted_placement': '',
        'salary_estimate': ''
    }

    # Compute num_languages from languages string
    student['num_languages'] = len([l.strip() for l in student['languages'].split(',') if l.strip()])

    # Academics (25% weight)
    cgpa_label, cgpa_score = score_level(student['cgpa'], 'cgpa')
    pct12_label, pct12_score = score_level(student['pct_12'], 'pct_12')
    pct10_label, pct10_score = score_level(student['pct_10'], 'pct_10')
    academic_score = int(cgpa_score * 0.5 + pct12_score * 0.25 + pct10_score * 0.25)
    analysis['scores']['Academics'] = {
        'score': academic_score,
        'details': {
            'CGPA': {'value': student['cgpa'], 'label': cgpa_label, 'score': cgpa_score},
            '12th %': {'value': student['pct_12'], 'label': pct12_label, 'score': pct12_score},
            '10th %': {'value': student['pct_10'], 'label': pct10_label, 'score': pct10_score},
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
            'DSA': {'value': student['dsa'], 'label': dsa_label, 'score': dsa_score},
            'OOPS': {'value': student['oops'], 'label': oops_label, 'score': oops_score},
            'Coding Problems': {'value': student['coding_solved'], 'label': '', 'score': coding_score},
            'Languages Known': {'value': student['num_languages'], 'label': '', 'score': lang_score},
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
            'Projects': {'value': student['projects'], 'label': '', 'score': proj_score},
            'Full-Stack': {'value': student['fullstack_project'], 'label': '', 'score': fullstack_score},
            'Internships': {'value': student['internship'], 'label': '', 'score': intern_score},
            'Open Source': {'value': student['opensource'], 'label': '', 'score': os_score},
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
            'Communication': {'value': student['communication'], 'label': comm_label, 'score': comm_score},
            'English': {'value': student['english'], 'label': eng_label, 'score': eng_score},
            'Confidence': {'value': student['confidence'], 'label': conf_label, 'score': conf_score},
            'Mock Interviews': {'value': student['mock_interviews'], 'label': '', 'score': mock_score},
        }
    }

    # Overall Score
    overall = int(academic_score * 0.25 + tech_score * 0.30 +
                  experience_score * 0.25 + soft_score * 0.20)
    analysis['overall_score'] = overall

    # Placement Prediction
    if overall >= 75:
        analysis['predicted_placement'] = 'HIGH'
    elif overall >= 55:
        analysis['predicted_placement'] = 'MODERATE'
    elif overall >= 35:
        analysis['predicted_placement'] = 'LOW'
    else:
        analysis['predicted_placement'] = 'VERY LOW'

    # Salary Estimate
    salary_factor = overall / 100
    estimated_min = round(BENCHMARKS['salary_avg'] * salary_factor * 0.6, 2)
    estimated_max = round(BENCHMARKS['salary_high'] * salary_factor * 1.1, 2)
    estimated_min = max(3.0, estimated_min)
    estimated_max = max(estimated_min + 2, estimated_max)
    analysis['salary_range'] = [estimated_min, estimated_max]

    # Strengths
    if student['cgpa'] >= 8.0:
        analysis['strengths'].append("Strong academic record (CGPA >= 8.0)")
    if student['dsa'] >= 4:
        analysis['strengths'].append("Good DSA knowledge - a key factor in technical interviews")
    if student['coding_solved'] in ['200-500', '500+']:
        analysis['strengths'].append(f"Good coding practice ({student['coding_solved']} problems solved)")
    if student['internship'] in ['1 Internship', '2+ Internships']:
        analysis['strengths'].append("Industry experience through internship(s)")
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

    # Weaknesses & Suggestions
    if student['cgpa'] < 6.5:
        analysis['weaknesses'].append(f"Low CGPA ({student['cgpa']}) - many companies have 6.5+ cutoff")
        analysis['suggestions'].append({
            'title': 'ACADEMICS',
            'text': 'Focus on improving your CGPA. Many companies have a minimum cutoff of 6.5-7.0. Prioritize core subjects, attend classes regularly, and aim for at least 7.0+ CGPA in remaining semesters.'
        })
    elif student['cgpa'] < 7.5:
        analysis['suggestions'].append({
            'title': 'ACADEMICS',
            'text': 'Your CGPA is decent but try to push it above 7.5 for better opportunities. Focus on scoring well in upcoming exams.'
        })

    if student['dsa'] <= 2:
        analysis['weaknesses'].append(f"Weak DSA skills (rated {student['dsa']}/5)")
        analysis['suggestions'].append({
            'title': 'DSA (CRITICAL)',
            'text': 'DSA is the #1 factor in technical interviews. Start with Arrays, Strings, Linked Lists, Stacks, Queues (Week 1-4). Then Trees, Graphs, Hashing, Sorting (Week 5-8). Then DP, Greedy, Backtracking (Week 9-12). Practice on LeetCode/GeeksforGeeks daily. Target 2-3 problems/day. Follow Striver\'s SDE Sheet or NeetCode 150.'
        })
    elif student['dsa'] == 3:
        analysis['suggestions'].append({
            'title': 'DSA',
            'text': 'You have intermediate DSA knowledge. Focus on Dynamic Programming, Graphs, and advanced Tree problems. Solve medium/hard LeetCode problems. Target 200+ total problems. Practice timed contests on Codeforces/LeetCode weekly.'
        })

    if student['coding_solved'] == '0-50':
        analysis['weaknesses'].append("Very few coding problems solved (0-50)")
        analysis['suggestions'].append({
            'title': 'CODING PRACTICE (URGENT)',
            'text': 'You need to solve more problems. Data shows students with 200+ problems solved have significantly higher placement rates. Start with easy problems on LeetCode/HackerRank (2-3 per day). Target: 200+ problems in next 3 months.'
        })
    elif student['coding_solved'] == '50-200':
        analysis['suggestions'].append({
            'title': 'CODING PRACTICE',
            'text': 'Good start! Push towards 300+ problems. Focus on medium-level problems now. Practice company-specific questions from LeetCode premium.'
        })

    if student['oops'] <= 2:
        analysis['weaknesses'].append(f"Weak OOPS understanding (rated {student['oops']}/5)")
        analysis['suggestions'].append({
            'title': 'OOPS',
            'text': 'Object-Oriented Programming is asked in almost every interview. Master: Encapsulation, Inheritance, Polymorphism, Abstraction. Learn SOLID principles, Design Patterns (Singleton, Factory, Observer). Pick Java or C++ and master OOPS in it.'
        })

    if student['num_languages'] < 2:
        analysis['weaknesses'].append("Knowledge of only 1 programming language")
        analysis['suggestions'].append({
            'title': 'LANGUAGES',
            'text': 'Learn at least 2-3 languages. Recommended: Python (versatile, ML, scripting), Java/C++ (core CS, competitive programming), JavaScript (web development, full-stack).'
        })

    if student['backend'].lower() == 'none':
        analysis['weaknesses'].append("No backend technology knowledge")
        analysis['suggestions'].append({
            'title': 'BACKEND DEVELOPMENT',
            'text': 'Backend skills are essential for most IT roles. Start with one: Django(Python), Spring Boot(Java), or Node.js/Express(JS). Build REST APIs, learn authentication, database integration. Create at least 2 backend projects.'
        })

    if 'html' in student['frontend'].lower() or student['frontend'].lower() == 'none':
        analysis['suggestions'].append({
            'title': 'FRONTEND',
            'text': 'Move beyond basic HTML/CSS. Learn React.js (most in-demand) or Angular. Build responsive web apps with modern frameworks. Learn state management (Redux/Context API).'
        })

    if student['database'].lower() == 'none':
        analysis['weaknesses'].append("No database knowledge")
        analysis['suggestions'].append({
            'title': 'DATABASE',
            'text': 'Database knowledge is fundamental. Learn SQL (MySQL/PostgreSQL) - practice joins, subqueries, indexing. Learn one NoSQL database (MongoDB). Understand database design and normalization.'
        })

    if student['system_design'] == 'None':
        analysis['suggestions'].append({
            'title': 'SYSTEM DESIGN',
            'text': 'Start learning basics of system design. Learn REST APIs, database design, caching, load balancing. Study URL shortener, chat system, notification service designs.'
        })

    if student['projects'] in ['0', '1-2']:
        analysis['weaknesses'].append(f"Too few projects ({student['projects']})")
        analysis['suggestions'].append({
            'title': 'PROJECTS (IMPORTANT)',
            'text': 'Build 3-5 meaningful projects: E-commerce app (Full-stack), Chat application (WebSocket), ML-based project, API-based project, Portfolio website. Deploy on GitHub with proper READMEs. Host live demos.'
        })

    if student['fullstack_project'] == 'No':
        analysis['suggestions'].append({
            'title': 'FULL-STACK PROJECT',
            'text': 'Build at least one complete full-stack project. Frontend (React/Angular) + Backend (Node/Django) + Database (MongoDB/MySQL). Include user auth, CRUD operations, API integration, deployment.'
        })

    if student['internship'] == 'No Internship':
        analysis['weaknesses'].append("No internship experience")
        analysis['suggestions'].append({
            'title': 'INTERNSHIP (HIGH PRIORITY)',
            'text': 'Students with internships have 15-25% higher placement rates and salary offers. Apply on Internshala, LinkedIn, AngelList, company career pages. Even a 2-month remote internship adds value.'
        })

    if student['opensource'] == 'No':
        analysis['suggestions'].append({
            'title': 'OPEN SOURCE',
            'text': 'Contributing to open source shows initiative and collaboration. Start with "good first issue" labels on GitHub. Even documentation fixes count as contributions.'
        })

    if student['communication'] <= 2:
        analysis['weaknesses'].append(f"Weak communication skills (rated {student['communication']}/5)")
        analysis['suggestions'].append({
            'title': 'COMMUNICATION (CRITICAL)',
            'text': 'Practice explaining technical concepts to non-tech friends. Join speaking clubs or group discussions. Record yourself answering interview questions and review.'
        })

    if student['english'] <= 2:
        analysis['weaknesses'].append(f"Low English fluency (rated {student['english']}/5)")
        analysis['suggestions'].append({
            'title': 'ENGLISH FLUENCY',
            'text': 'Read English articles/blogs daily (30 mins). Listen to English podcasts/news. Practice speaking in English with peers.'
        })

    if student['confidence'] <= 2:
        analysis['weaknesses'].append(f"Low interview confidence (rated {student['confidence']}/5)")
        analysis['suggestions'].append({
            'title': 'INTERVIEW CONFIDENCE',
            'text': 'Practice mock interviews (use Pramp, InterviewBit, or peers). Prepare answers for common HR questions. Practice the STAR method for behavioral questions.'
        })

    if student['mock_interviews'] == 'No':
        analysis['suggestions'].append({
            'title': 'MOCK INTERVIEWS',
            'text': 'Attend mock interviews to build confidence. Use platforms: Pramp (free), InterviewBit, peer mock sessions. Practice both technical and HR rounds.'
        })

    if student['applying'] == 'No' and student['year'] in ['4th Year', 'Graduate (Unplaced)']:
        analysis['suggestions'].append({
            'title': 'JOB APPLICATIONS',
            'text': 'You should be actively applying! Create profiles on LinkedIn, Naukri, Indeed, AngelList. Apply to at least 5-10 companies per week. Tailor your resume for each application.'
        })

    if student['expected_salary'] > analysis['salary_range'][1] + 5:
        analysis['suggestions'].append({
            'title': 'SALARY EXPECTATIONS',
            'text': f'Your expected salary ({student["expected_salary"]} LPA) may be higher than realistic based on your current profile. The dataset average is ~14.25 LPA for placed students. Focus on building skills first.'
        })

    # Priority actions (top 3)
    analysis['priorities'] = [s['title'] for s in analysis['suggestions'][:3]]

    return analysis


def compare_with_dataset(student: dict, data_path: str) -> dict:
    df = pd.read_excel(data_path)
    placed = df[df['Placement Status'] == 'Placed']

    comparison = {
        'cgpa': {
            'yours': student['cgpa'],
            'placed_avg': round(placed['CGPA (Out of 10)'].mean(), 2),
            'status': 'Above' if student['cgpa'] >= placed['CGPA (Out of 10)'].mean() else 'Below'
        },
        'dsa': {
            'yours': student['dsa'],
            'placed_avg': round(placed['DSA Knowledge (1-5)'].mean(), 1),
            'status': 'Above' if student['dsa'] >= placed['DSA Knowledge (1-5)'].mean() else 'Below'
        },
        'communication': {
            'yours': student['communication'],
            'placed_avg': round(placed['Communication Skill (1-5)'].mean(), 1),
            'status': 'Above' if student['communication'] >= placed['Communication Skill (1-5)'].mean() else 'Below'
        },
        'confidence': {
            'yours': student['confidence'],
            'placed_avg': round(placed['Interview Confidence (1-5)'].mean(), 1),
            'status': 'Above' if student['confidence'] >= placed['Interview Confidence (1-5)'].mean() else 'Below'
        },
        'expected_salary': {
            'yours': student['expected_salary'],
            'placed_avg': round(placed['Salary Package (LPA)'].mean(), 2),
        },
        'total_students': len(df),
        'placed_count': len(placed),
        'unplaced_count': len(df) - len(placed),
    }
    return comparison
