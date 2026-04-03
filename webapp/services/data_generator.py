import pandas as pd
import numpy as np
import random
import os
from datetime import datetime


def generate_dataset(n_records: int = 1000, seed: int = 42, output_dir: str = '.') -> tuple:
    random.seed(seed)
    np.random.seed(seed)
    N = n_records

    branch = random.choices(
        ["Computer Science", "Information Technology", "Electronics/E&TC", "Other"],
        weights=[45, 25, 20, 10], k=N)

    status = random.choices(
        ["3rd Year", "4th Year", "Graduate (Unplaced)", "Placed Graduate"],
        weights=[25, 35, 20, 20], k=N)

    cgpa = np.round(np.clip(np.random.normal(7.2, 1.2, N), 4.0, 10.0), 2)
    twelfth_pct = np.round(np.clip(np.random.normal(72, 12, N), 40, 99), 2)
    tenth_pct = np.round(np.clip(np.random.normal(78, 10, N), 45, 99), 2)

    dsa_knowledge = random.choices([1, 2, 3, 4, 5], weights=[8, 20, 35, 25, 12], k=N)
    problems_solved = random.choices(["0-50", "50-200", "200-500", "500+"], weights=[30, 35, 25, 10], k=N)

    all_langs = ["C", "C++", "Java", "Python", "Javascript", "C#"]
    def pick_languages():
        count = random.choices([1, 2, 3, 4, 5], weights=[10, 25, 35, 20, 10])[0]
        return ", ".join(random.sample(all_langs, min(count, len(all_langs))))
    prog_languages = [pick_languages() for _ in range(N)]

    all_backend = ["Node.js", ".NET", "Spring Boot", "Django", "None"]
    def pick_backend():
        if random.random() < 0.25:
            return "None"
        count = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
        opts = [b for b in all_backend if b != "None"]
        return ", ".join(random.sample(opts, min(count, len(opts))))
    backend_tech = [pick_backend() for _ in range(N)]

    all_frontend = ["React", "Angular", "Vue", "Basic HTML/CSS only"]
    def pick_frontend():
        if random.random() < 0.20:
            return "Basic HTML/CSS only"
        count = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
        opts = [f for f in all_frontend if f != "Basic HTML/CSS only"]
        return ", ".join(random.sample(opts, min(count, len(opts))))
    frontend_tech = [pick_frontend() for _ in range(N)]

    all_db = ["MySQL", "PostgreSQL", "MongoDB", "NoSQL basics", "None"]
    def pick_db():
        if random.random() < 0.15:
            return "None"
        count = random.choices([1, 2, 3], weights=[45, 35, 20])[0]
        opts = [d for d in all_db if d != "None"]
        return ", ".join(random.sample(opts, min(count, len(opts))))
    db_knowledge = [pick_db() for _ in range(N)]

    oops_level = random.choices([1, 2, 3, 4, 5], weights=[5, 15, 35, 30, 15], k=N)
    sys_design = random.choices(
        ["None", "Basic (REST APIs, DB design)", "Intermediate", "Advanced"],
        weights=[25, 40, 25, 10], k=N)
    fullstack_project = random.choices(["Yes", "No"], weights=[45, 55], k=N)
    projects_completed = random.choices(["0", "1-2", "3-5", "5+"], weights=[10, 35, 35, 20], k=N)
    internship = random.choices(["No Internship", "1 Internship", "2+ Internships"], weights=[35, 40, 25], k=N)
    opensource = random.choices(["Yes", "No"], weights=[25, 75], k=N)
    communication = random.choices([1, 2, 3, 4, 5], weights=[5, 15, 35, 30, 15], k=N)
    english = random.choices([1, 2, 3, 4, 5], weights=[5, 12, 30, 35, 18], k=N)
    interview_conf = random.choices([1, 2, 3, 4, 5], weights=[10, 20, 35, 25, 10], k=N)
    mock_interview = random.choices(["Yes", "No"], weights=[40, 60], k=N)

    placement_status = []
    salary_package = []
    company_type = []
    expected_salary = []
    actively_applying = []

    for i in range(N):
        score = (
            cgpa[i] * 3 + dsa_knowledge[i] * 4 + oops_level[i] * 2
            + communication[i] * 2 + interview_conf[i] * 2
            + (3 if fullstack_project[i] == "Yes" else 0)
            + (4 if internship[i] == "2+ Internships" else 2 if internship[i] == "1 Internship" else 0)
            + (2 if opensource[i] == "Yes" else 0)
            + (3 if problems_solved[i] == "500+" else 2 if problems_solved[i] == "200-500" else 1 if problems_solved[i] == "50-200" else 0)
            + (3 if sys_design[i] == "Advanced" else 2 if sys_design[i] == "Intermediate" else 1 if sys_design[i] == "Basic (REST APIs, DB design)" else 0)
        )
        norm_score = max(0, min(1, (score - 15) / 55))
        placed_prob = norm_score * 0.85 + 0.05
        is_placed = random.random() < placed_prob

        if status[i] == "Placed Graduate":
            is_placed = True
        elif status[i] == "3rd Year":
            is_placed = random.random() < 0.15

        placement_status.append("Placed" if is_placed else "Unplaced")

        if is_placed:
            if norm_score > 0.75:
                sal = round(random.uniform(8, 25), 2)
                ctype = random.choices(["Product-Based", "Startup", "Service-Based"], weights=[55, 25, 20])[0]
            elif norm_score > 0.5:
                sal = round(random.uniform(4, 12), 2)
                ctype = random.choices(["Product-Based", "Service-Based", "Startup"], weights=[30, 45, 25])[0]
            else:
                sal = round(random.uniform(2.5, 6), 2)
                ctype = random.choices(["Service-Based", "Startup", "Product-Based"], weights=[55, 25, 20])[0]
            salary_package.append(sal)
            company_type.append(ctype)
            actively_applying.append("No")
        else:
            salary_package.append("NA")
            company_type.append("NA")
            actively_applying.append(random.choices(["Yes", "No"], weights=[80, 20])[0])

        if norm_score > 0.7:
            exp = round(random.uniform(8, 25), 2)
        elif norm_score > 0.4:
            exp = round(random.uniform(5, 15), 2)
        else:
            exp = round(random.uniform(3, 8), 2)
        expected_salary.append(exp)

    df = pd.DataFrame({
        "Degree Branch": branch, "Current Status": status,
        "CGPA (Out of 10)": cgpa, "12th Percentage": twelfth_pct, "10th Percentage": tenth_pct,
        "DSA Knowledge (1-5)": dsa_knowledge, "Coding Problems Solved": problems_solved,
        "Programming Languages Known": prog_languages, "Backend Technology": backend_tech,
        "Frontend Technology": frontend_tech, "Database Knowledge": db_knowledge,
        "OOPS Understanding (1-5)": oops_level, "System Design Knowledge": sys_design,
        "Full-Stack Project Built": fullstack_project, "Technical Projects Completed": projects_completed,
        "Internship Experience": internship, "Open Source Contributions": opensource,
        "Communication Skill (1-5)": communication, "English Fluency (1-5)": english,
        "Interview Confidence (1-5)": interview_conf, "Mock Interviews Attended": mock_interview,
        "Placement Status": placement_status, "Salary Package (LPA)": salary_package,
        "Company Type": company_type, "Expected Salary (LPA)": expected_salary,
        "Actively Applying for IT Jobs": actively_applying,
    })

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = os.path.join(output_dir, f'placement_data_{timestamp}.xlsx')
    df.to_excel(filepath, index=False, sheet_name="Placement Data")

    placed_count = int((df['Placement Status'] == 'Placed').sum())
    unplaced_count = int((df['Placement Status'] == 'Unplaced').sum())
    branch_dist = df['Degree Branch'].value_counts().to_dict()

    summary = {
        'total_records': N,
        'placed': placed_count,
        'unplaced': unplaced_count,
        'branch_distribution': branch_dist,
        'filename': os.path.basename(filepath),
        'filepath': filepath,
        'sample_rows': df.head(10).to_dict(orient='records'),
    }
    return filepath, summary
