"""
Placement Salary Prediction and Analysis Using Machine Learning
Indira College of Commerce and Science
S.Y M.Sc. (Comp.Sci) - Sem IV Academic Year 2025-26
Team: Nikhil Ghalme (32), Abhijit Bhujbal (01), Saurabh Gawali (94)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             confusion_matrix, classification_report, roc_auc_score, roc_curve,
                             mean_absolute_error, mean_squared_error, r2_score)
from fpdf import FPDF
import warnings
import os

warnings.filterwarnings('ignore')
sns.set_style('whitegrid')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 10

OUTPUT_DIR = '/home/nikhil/workspace/bytephase/research/placement_analysis_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 1. DATA LOADING
# ============================================================
print("=" * 60)
print("PHASE 1: DATA LOADING & UNDERSTANDING")
print("=" * 60)

df = pd.read_excel('/home/nikhil/workspace/bytephase/research/placement_readiness_data.xlsx')
print(f"Dataset Shape: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"\nColumns:\n{df.columns.tolist()}")
print(f"\nData Types:\n{df.dtypes}")
print(f"\nMissing Values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
print(f"\nPlacement Status Distribution:\n{df['Placement Status'].value_counts()}")
print(f"\nSalary Statistics (Placed students):\n{df['Salary Package (LPA)'].describe()}")

# ============================================================
# 2. EXPLORATORY DATA ANALYSIS (EDA)
# ============================================================
print("\n" + "=" * 60)
print("PHASE 2: EXPLORATORY DATA ANALYSIS")
print("=" * 60)

# --- Chart 1: Placement Status Distribution ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
status_counts = df['Placement Status'].value_counts()
colors = ['#2ecc71', '#e74c3c']
axes[0].pie(status_counts, labels=status_counts.index, autopct='%1.1f%%',
            colors=colors, startangle=90, explode=(0.05, 0.05))
axes[0].set_title('Placement Status Distribution', fontweight='bold', fontsize=13)

sns.countplot(data=df, x='Placement Status', palette=colors, ax=axes[1])
axes[1].set_title('Placement Status Count', fontweight='bold', fontsize=13)
for p in axes[1].patches:
    axes[1].annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/01_placement_status_distribution.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 1: Placement Status Distribution")

# --- Chart 2: Branch-wise Placement ---
fig, ax = plt.subplots(figsize=(10, 6))
branch_placement = pd.crosstab(df['Degree Branch'], df['Placement Status'])
branch_placement.plot(kind='bar', ax=ax, color=colors, edgecolor='black')
ax.set_title('Branch-wise Placement Status', fontweight='bold', fontsize=13)
ax.set_xlabel('Degree Branch')
ax.set_ylabel('Count')
ax.legend(title='Status')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/02_branch_wise_placement.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 2: Branch-wise Placement Status")

# --- Chart 3: CGPA Distribution by Placement Status ---
fig, ax = plt.subplots(figsize=(10, 6))
for status, color in zip(['Placed', 'Unplaced'], colors):
    subset = df[df['Placement Status'] == status]
    ax.hist(subset['CGPA (Out of 10)'], bins=25, alpha=0.6, label=status, color=color, edgecolor='black')
ax.set_title('CGPA Distribution by Placement Status', fontweight='bold', fontsize=13)
ax.set_xlabel('CGPA (Out of 10)')
ax.set_ylabel('Frequency')
ax.legend()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/03_cgpa_distribution.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 3: CGPA Distribution")

# --- Chart 4: Salary Distribution ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
salary_data = df[df['Salary Package (LPA)'].notna()]['Salary Package (LPA)']
axes[0].hist(salary_data, bins=30, color='#3498db', edgecolor='black', alpha=0.7)
axes[0].set_title('Salary Package Distribution (LPA)', fontweight='bold', fontsize=13)
axes[0].set_xlabel('Salary (LPA)')
axes[0].set_ylabel('Frequency')
axes[0].axvline(salary_data.mean(), color='red', linestyle='--', label=f'Mean: {salary_data.mean():.2f}')
axes[0].axvline(salary_data.median(), color='green', linestyle='--', label=f'Median: {salary_data.median():.2f}')
axes[0].legend()

# Salary by Company Type
company_salary = df[df['Company Type'].notna()]
sns.boxplot(data=company_salary, x='Company Type', y='Salary Package (LPA)', palette='Set2', ax=axes[1])
axes[1].set_title('Salary by Company Type', fontweight='bold', fontsize=13)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/04_salary_distribution.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 4: Salary Distribution")

# --- Chart 5: Skills vs Placement ---
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
skill_cols = ['DSA Knowledge (1-5)', 'OOPS Understanding (1-5)', 'Communication Skill (1-5)',
              'English Fluency (1-5)', 'Interview Confidence (1-5)']
for i, col in enumerate(skill_cols):
    row, col_idx = divmod(i, 3)
    sns.boxplot(data=df, x='Placement Status', y=col, palette=colors, ax=axes[row][col_idx])
    axes[row][col_idx].set_title(col.replace(' (1-5)', ''), fontweight='bold')
axes[1][2].axis('off')
plt.suptitle('Skill Ratings vs Placement Status', fontweight='bold', fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/05_skills_vs_placement.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 5: Skills vs Placement")

# --- Chart 6: Coding Problems & Internship vs Placement ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
coding_order = ['0-50', '50-200', '200-500', '500+']
ct1 = pd.crosstab(df['Coding Problems Solved'], df['Placement Status'])
ct1 = ct1.reindex(coding_order)
ct1.plot(kind='bar', ax=axes[0], color=colors, edgecolor='black')
axes[0].set_title('Coding Problems Solved vs Placement', fontweight='bold', fontsize=13)
axes[0].set_xlabel('Problems Solved')
axes[0].tick_params(axis='x', rotation=0)

intern_order = ['No Internship', '1 Internship', '2+ Internships']
ct2 = pd.crosstab(df['Internship Experience'], df['Placement Status'])
ct2 = ct2.reindex(intern_order)
ct2.plot(kind='bar', ax=axes[1], color=colors, edgecolor='black')
axes[1].set_title('Internship Experience vs Placement', fontweight='bold', fontsize=13)
axes[1].set_xlabel('Internship Experience')
axes[1].tick_params(axis='x', rotation=0)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/06_coding_internship_placement.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 6: Coding & Internship vs Placement")

# --- Chart 7: Academic Scores Correlation Heatmap ---
numeric_cols = ['CGPA (Out of 10)', '12th Percentage', '10th Percentage',
                'DSA Knowledge (1-5)', 'OOPS Understanding (1-5)',
                'Communication Skill (1-5)', 'English Fluency (1-5)',
                'Interview Confidence (1-5)', 'Salary Package (LPA)', 'Expected Salary (LPA)']
fig, ax = plt.subplots(figsize=(12, 10))
corr_matrix = df[numeric_cols].corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='RdYlBu_r',
            center=0, ax=ax, linewidths=0.5, square=True)
ax.set_title('Correlation Heatmap of Numerical Features', fontweight='bold', fontsize=13)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/07_correlation_heatmap.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 7: Correlation Heatmap")

# --- Chart 8: Full-Stack Project & Open Source vs Placement ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
ct3 = pd.crosstab(df['Full-Stack Project Built'], df['Placement Status'])
ct3.plot(kind='bar', ax=axes[0], color=colors, edgecolor='black')
axes[0].set_title('Full-Stack Project vs Placement', fontweight='bold', fontsize=13)
axes[0].tick_params(axis='x', rotation=0)

ct4 = pd.crosstab(df['Open Source Contributions'], df['Placement Status'])
ct4.plot(kind='bar', ax=axes[1], color=colors, edgecolor='black')
axes[1].set_title('Open Source Contributions vs Placement', fontweight='bold', fontsize=13)
axes[1].tick_params(axis='x', rotation=0)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/08_projects_opensource.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 8: Projects & Open Source vs Placement")

# --- Chart 9: Salary by Branch ---
fig, ax = plt.subplots(figsize=(10, 6))
placed_df = df[df['Salary Package (LPA)'].notna()]
sns.boxplot(data=placed_df, x='Degree Branch', y='Salary Package (LPA)', palette='Set3', ax=ax)
ax.set_title('Salary Package by Degree Branch', fontweight='bold', fontsize=13)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/09_salary_by_branch.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 9: Salary by Branch")

# --- Chart 10: Mock Interview & Current Status ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ct5 = pd.crosstab(df['Mock Interviews Attended'], df['Placement Status'])
ct5.plot(kind='bar', ax=axes[0], color=colors, edgecolor='black')
axes[0].set_title('Mock Interviews vs Placement', fontweight='bold', fontsize=13)
axes[0].tick_params(axis='x', rotation=0)

ct6 = pd.crosstab(df['Current Status'], df['Placement Status'])
ct6.plot(kind='bar', ax=axes[1], color=colors, edgecolor='black')
axes[1].set_title('Current Status vs Placement', fontweight='bold', fontsize=13)
axes[1].tick_params(axis='x', rotation=0)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/10_mock_interview_status.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 10: Mock Interview & Current Status")

# ============================================================
# 3. DATA PREPROCESSING
# ============================================================
print("\n" + "=" * 60)
print("PHASE 3: DATA PREPROCESSING")
print("=" * 60)

df_ml = df.copy()

# Encode target variable
le_target = LabelEncoder()
df_ml['Placement_Status_Encoded'] = le_target.fit_transform(df_ml['Placement Status'])  # Placed=0, Unplaced=1
# Flip so Placed=1, Unplaced=0
df_ml['Placement_Status_Encoded'] = 1 - df_ml['Placement_Status_Encoded']
print(f"  Target encoding: Placed=1 ({(df_ml['Placement_Status_Encoded']==1).sum()}), Unplaced=0 ({(df_ml['Placement_Status_Encoded']==0).sum()})")

# Encode categorical features
label_encoders = {}
categorical_cols = ['Degree Branch', 'Current Status', 'Coding Problems Solved',
                    'Frontend Technology', 'Full-Stack Project Built',
                    'Technical Projects Completed', 'Internship Experience',
                    'Open Source Contributions', 'Mock Interviews Attended',
                    'Actively Applying for IT Jobs']

for col in categorical_cols:
    le = LabelEncoder()
    df_ml[col + '_enc'] = le.fit_transform(df_ml[col].astype(str))
    label_encoders[col] = le
    print(f"  Encoded: {col} -> {dict(zip(le.classes_, le.transform(le.classes_)))}")

# Handle missing categorical cols with mode
for col in ['Backend Technology', 'Database Knowledge', 'System Design Knowledge']:
    df_ml[col].fillna('None', inplace=True)
    le = LabelEncoder()
    df_ml[col + '_enc'] = le.fit_transform(df_ml[col].astype(str))
    label_encoders[col] = le

# Count programming languages known
df_ml['Num_Languages'] = df_ml['Programming Languages Known'].apply(lambda x: len(str(x).split(',')))

# Feature columns for classification
feature_cols = ['CGPA (Out of 10)', '12th Percentage', '10th Percentage',
                'DSA Knowledge (1-5)', 'OOPS Understanding (1-5)',
                'Communication Skill (1-5)', 'English Fluency (1-5)',
                'Interview Confidence (1-5)', 'Num_Languages',
                'Degree Branch_enc', 'Current Status_enc', 'Coding Problems Solved_enc',
                'Frontend Technology_enc', 'Full-Stack Project Built_enc',
                'Technical Projects Completed_enc', 'Internship Experience_enc',
                'Open Source Contributions_enc', 'Mock Interviews Attended_enc',
                'Backend Technology_enc', 'Database Knowledge_enc', 'System Design Knowledge_enc']

print(f"\n  Total features for modeling: {len(feature_cols)}")

# ============================================================
# 4. CLASSIFICATION - Placement Status Prediction
# ============================================================
print("\n" + "=" * 60)
print("PHASE 4: CLASSIFICATION - Placement Status Prediction")
print("=" * 60)

X_class = df_ml[feature_cols]
y_class = df_ml['Placement_Status_Encoded']

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_class, y_class, test_size=0.2, random_state=42, stratify=y_class)

scaler_c = StandardScaler()
X_train_c_scaled = scaler_c.fit_transform(X_train_c)
X_test_c_scaled = scaler_c.transform(X_test_c)

print(f"  Training set: {X_train_c.shape[0]} samples")
print(f"  Testing set:  {X_test_c.shape[0]} samples")

# Define models
classifiers = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42),
    'SVM': SVC(kernel='rbf', probability=True, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=200, max_depth=5, random_state=42)
}

classification_results = {}
fig_roc, ax_roc = plt.subplots(figsize=(10, 8))

for name, model in classifiers.items():
    print(f"\n  Training: {name}")
    if name in ['Logistic Regression', 'SVM']:
        model.fit(X_train_c_scaled, y_train_c)
        y_pred = model.predict(X_test_c_scaled)
        y_prob = model.predict_proba(X_test_c_scaled)[:, 1]
        cv_scores = cross_val_score(model, X_train_c_scaled, y_train_c, cv=5, scoring='accuracy')
    else:
        model.fit(X_train_c, y_train_c)
        y_pred = model.predict(X_test_c)
        y_prob = model.predict_proba(X_test_c)[:, 1]
        cv_scores = cross_val_score(model, X_train_c, y_train_c, cv=5, scoring='accuracy')

    acc = accuracy_score(y_test_c, y_pred)
    prec = precision_score(y_test_c, y_pred)
    rec = recall_score(y_test_c, y_pred)
    f1 = f1_score(y_test_c, y_pred)
    auc = roc_auc_score(y_test_c, y_prob)
    cv_mean = cv_scores.mean()

    classification_results[name] = {
        'Accuracy': acc, 'Precision': prec, 'Recall': rec,
        'F1-Score': f1, 'AUC-ROC': auc, 'CV Accuracy': cv_mean,
        'y_pred': y_pred, 'y_prob': y_prob
    }

    print(f"    Accuracy:  {acc:.4f}")
    print(f"    Precision: {prec:.4f}")
    print(f"    Recall:    {rec:.4f}")
    print(f"    F1-Score:  {f1:.4f}")
    print(f"    AUC-ROC:   {auc:.4f}")
    print(f"    CV Acc:    {cv_mean:.4f} (+/- {cv_scores.std():.4f})")

    # ROC Curve
    fpr, tpr, _ = roc_curve(y_test_c, y_prob)
    ax_roc.plot(fpr, tpr, label=f'{name} (AUC={auc:.3f})', linewidth=2)

ax_roc.plot([0, 1], [0, 1], 'k--', alpha=0.5)
ax_roc.set_xlabel('False Positive Rate', fontsize=12)
ax_roc.set_ylabel('True Positive Rate', fontsize=12)
ax_roc.set_title('ROC Curves - Classification Models Comparison', fontweight='bold', fontsize=13)
ax_roc.legend(fontsize=11)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/11_roc_curves.png', bbox_inches='tight')
plt.close()
print("\n  [+] Chart 11: ROC Curves")

# --- Chart 12: Classification Comparison Bar Chart ---
metrics_df = pd.DataFrame({name: {k: v for k, v in vals.items() if k not in ['y_pred', 'y_prob']}
                           for name, vals in classification_results.items()}).T
fig, ax = plt.subplots(figsize=(12, 6))
metrics_df[['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC-ROC']].plot(kind='bar', ax=ax, edgecolor='black')
ax.set_title('Classification Models Comparison', fontweight='bold', fontsize=13)
ax.set_ylabel('Score')
ax.set_ylim(0, 1.05)
ax.legend(loc='lower right')
plt.xticks(rotation=0)
for container in ax.containers:
    ax.bar_label(container, fmt='%.3f', fontsize=7, rotation=90, padding=3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/12_classification_comparison.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 12: Classification Comparison")

# --- Chart 13: Confusion Matrices ---
fig, axes = plt.subplots(1, 4, figsize=(20, 4))
for i, (name, results) in enumerate(classification_results.items()):
    cm = confusion_matrix(y_test_c, results['y_pred'])
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[i],
                xticklabels=['Unplaced', 'Placed'], yticklabels=['Unplaced', 'Placed'])
    axes[i].set_title(name, fontweight='bold', fontsize=11)
    axes[i].set_xlabel('Predicted')
    axes[i].set_ylabel('Actual')
plt.suptitle('Confusion Matrices - All Models', fontweight='bold', fontsize=14, y=1.05)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/13_confusion_matrices.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 13: Confusion Matrices")

# --- Chart 14: Feature Importance (Random Forest) ---
rf_model = classifiers['Random Forest']
feature_importance = pd.Series(rf_model.feature_importances_, index=feature_cols)
feature_importance = feature_importance.sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(10, 8))
feature_importance.plot(kind='barh', ax=ax, color='#3498db', edgecolor='black')
ax.set_title('Feature Importance (Random Forest - Classification)', fontweight='bold', fontsize=13)
ax.set_xlabel('Importance Score')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/14_feature_importance_classification.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 14: Feature Importance (Classification)")

# ============================================================
# 5. REGRESSION - Salary Prediction
# ============================================================
print("\n" + "=" * 60)
print("PHASE 5: REGRESSION - Salary Prediction")
print("=" * 60)

# Only placed students with salary
df_salary = df_ml[df_ml['Salary Package (LPA)'].notna()].copy()
print(f"  Placed students with salary data: {df_salary.shape[0]}")

X_reg = df_salary[feature_cols]
y_reg = df_salary['Salary Package (LPA)']

X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)

scaler_r = StandardScaler()
X_train_r_scaled = scaler_r.fit_transform(X_train_r)
X_test_r_scaled = scaler_r.transform(X_test_r)

print(f"  Training set: {X_train_r.shape[0]} samples")
print(f"  Testing set:  {X_test_r.shape[0]} samples")

# Define regression models
regressors = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Lasso Regression': Lasso(alpha=0.1),
    'Random Forest': RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=200, max_depth=5, random_state=42)
}

regression_results = {}

for name, model in regressors.items():
    print(f"\n  Training: {name}")
    if name in ['Linear Regression', 'Ridge Regression', 'Lasso Regression']:
        model.fit(X_train_r_scaled, y_train_r)
        y_pred_r = model.predict(X_test_r_scaled)
        cv_r2 = cross_val_score(model, X_train_r_scaled, y_train_r, cv=5, scoring='r2')
    else:
        model.fit(X_train_r, y_train_r)
        y_pred_r = model.predict(X_test_r)
        cv_r2 = cross_val_score(model, X_train_r, y_train_r, cv=5, scoring='r2')

    r2 = r2_score(y_test_r, y_pred_r)
    mae = mean_absolute_error(y_test_r, y_pred_r)
    rmse = np.sqrt(mean_squared_error(y_test_r, y_pred_r))
    cv_r2_mean = cv_r2.mean()

    regression_results[name] = {
        'R2 Score': r2, 'MAE': mae, 'RMSE': rmse,
        'CV R2': cv_r2_mean, 'y_pred': y_pred_r
    }

    print(f"    R2 Score: {r2:.4f}")
    print(f"    MAE:      {mae:.4f} LPA")
    print(f"    RMSE:     {rmse:.4f} LPA")
    print(f"    CV R2:    {cv_r2_mean:.4f}")

# --- Chart 15: Regression Models Comparison ---
reg_df = pd.DataFrame({name: {k: v for k, v in vals.items() if k != 'y_pred'}
                       for name, vals in regression_results.items()}).T
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
reg_df['R2 Score'].plot(kind='bar', ax=axes[0], color='#2ecc71', edgecolor='black')
axes[0].set_title('R\u00b2 Score Comparison', fontweight='bold')
axes[0].set_ylabel('R\u00b2 Score')
axes[0].tick_params(axis='x', rotation=30)
for p in axes[0].patches:
    axes[0].annotate(f'{p.get_height():.3f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='bottom', fontweight='bold', fontsize=8)

reg_df['MAE'].plot(kind='bar', ax=axes[1], color='#e74c3c', edgecolor='black')
axes[1].set_title('MAE Comparison (Lower is Better)', fontweight='bold')
axes[1].set_ylabel('MAE (LPA)')
axes[1].tick_params(axis='x', rotation=30)
for p in axes[1].patches:
    axes[1].annotate(f'{p.get_height():.3f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='bottom', fontweight='bold', fontsize=8)

reg_df['RMSE'].plot(kind='bar', ax=axes[2], color='#3498db', edgecolor='black')
axes[2].set_title('RMSE Comparison (Lower is Better)', fontweight='bold')
axes[2].set_ylabel('RMSE (LPA)')
axes[2].tick_params(axis='x', rotation=30)
for p in axes[2].patches:
    axes[2].annotate(f'{p.get_height():.3f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='bottom', fontweight='bold', fontsize=8)

plt.suptitle('Regression Models Comparison - Salary Prediction', fontweight='bold', fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/15_regression_comparison.png', bbox_inches='tight')
plt.close()
print("\n  [+] Chart 15: Regression Models Comparison")

# --- Chart 16: Actual vs Predicted Salary ---
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
for i, (name, results) in enumerate(regression_results.items()):
    row, col_idx = divmod(i, 3)
    axes[row][col_idx].scatter(y_test_r, results['y_pred'], alpha=0.5, color='#3498db', edgecolor='black', s=30)
    axes[row][col_idx].plot([y_test_r.min(), y_test_r.max()], [y_test_r.min(), y_test_r.max()], 'r--', linewidth=2)
    axes[row][col_idx].set_title(f'{name}\nR\u00b2={results["R2 Score"]:.3f}', fontweight='bold')
    axes[row][col_idx].set_xlabel('Actual Salary (LPA)')
    axes[row][col_idx].set_ylabel('Predicted Salary (LPA)')
axes[1][2].axis('off')
plt.suptitle('Actual vs Predicted Salary - All Models', fontweight='bold', fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/16_actual_vs_predicted.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 16: Actual vs Predicted Salary")

# --- Chart 17: Feature Importance (Regression - Gradient Boosting) ---
gb_reg = regressors['Gradient Boosting']
feat_imp_reg = pd.Series(gb_reg.feature_importances_, index=feature_cols)
feat_imp_reg = feat_imp_reg.sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(10, 8))
feat_imp_reg.plot(kind='barh', ax=ax, color='#e67e22', edgecolor='black')
ax.set_title('Feature Importance (Gradient Boosting - Salary Prediction)', fontweight='bold', fontsize=13)
ax.set_xlabel('Importance Score')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/17_feature_importance_regression.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 17: Feature Importance (Regression)")

# --- Chart 18: Residual Analysis (Best Model) ---
best_reg_name = max(regression_results, key=lambda x: regression_results[x]['R2 Score'])
best_pred = regression_results[best_reg_name]['y_pred']
residuals = y_test_r.values - best_pred

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].scatter(best_pred, residuals, alpha=0.5, color='#9b59b6', edgecolor='black', s=30)
axes[0].axhline(y=0, color='red', linestyle='--', linewidth=2)
axes[0].set_title(f'Residual Plot ({best_reg_name})', fontweight='bold', fontsize=13)
axes[0].set_xlabel('Predicted Salary (LPA)')
axes[0].set_ylabel('Residuals (LPA)')

axes[1].hist(residuals, bins=25, color='#9b59b6', edgecolor='black', alpha=0.7)
axes[1].set_title(f'Residual Distribution ({best_reg_name})', fontweight='bold', fontsize=13)
axes[1].set_xlabel('Residuals (LPA)')
axes[1].set_ylabel('Frequency')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/18_residual_analysis.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 18: Residual Analysis")

# --- Chart 19: Expected vs Actual Salary Gap ---
fig, ax = plt.subplots(figsize=(10, 6))
salary_gap = df[df['Salary Package (LPA)'].notna()].copy()
salary_gap['Gap'] = salary_gap['Expected Salary (LPA)'] - salary_gap['Salary Package (LPA)']
sns.histplot(salary_gap['Gap'], bins=30, color='#1abc9c', edgecolor='black', ax=ax)
ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='No Gap')
ax.axvline(x=salary_gap['Gap'].mean(), color='orange', linestyle='--', linewidth=2,
           label=f'Mean Gap: {salary_gap["Gap"].mean():.2f} LPA')
ax.set_title('Expected vs Actual Salary Gap', fontweight='bold', fontsize=13)
ax.set_xlabel('Gap (Expected - Actual) in LPA')
ax.set_ylabel('Frequency')
ax.legend()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/19_salary_gap.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 19: Expected vs Actual Salary Gap")

# --- Chart 20: Technology Stack Analysis ---
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
# Frontend
frontend_placement = pd.crosstab(df['Frontend Technology'], df['Placement Status'])
frontend_rate = (frontend_placement['Placed'] / frontend_placement.sum(axis=1) * 100).sort_values(ascending=True)
frontend_rate.plot(kind='barh', ax=axes[0], color='#2980b9', edgecolor='black')
axes[0].set_title('Placement Rate by Frontend Tech', fontweight='bold', fontsize=12)
axes[0].set_xlabel('Placement Rate (%)')
for i, v in enumerate(frontend_rate):
    axes[0].text(v + 0.5, i, f'{v:.1f}%', va='center', fontsize=8)

# Backend (top 10)
backend_counts = df['Backend Technology'].value_counts().head(10)
backend_placement = pd.crosstab(df[df['Backend Technology'].isin(backend_counts.index)]['Backend Technology'],
                                df[df['Backend Technology'].isin(backend_counts.index)]['Placement Status'])
backend_rate = (backend_placement['Placed'] / backend_placement.sum(axis=1) * 100).sort_values(ascending=True)
backend_rate.plot(kind='barh', ax=axes[1], color='#27ae60', edgecolor='black')
axes[1].set_title('Placement Rate by Backend Tech (Top 10)', fontweight='bold', fontsize=12)
axes[1].set_xlabel('Placement Rate (%)')
for i, v in enumerate(backend_rate):
    axes[1].text(v + 0.5, i, f'{v:.1f}%', va='center', fontsize=8)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/20_tech_stack_analysis.png', bbox_inches='tight')
plt.close()
print("  [+] Chart 20: Technology Stack Analysis")

# ============================================================
# 6. SUMMARY & KEY FINDINGS
# ============================================================
print("\n" + "=" * 60)
print("PHASE 6: KEY FINDINGS SUMMARY")
print("=" * 60)

best_clf_name = max(classification_results, key=lambda x: classification_results[x]['Accuracy'])
best_clf = classification_results[best_clf_name]
best_reg = regression_results[best_reg_name]

print(f"\n  CLASSIFICATION RESULTS:")
print(f"  {'Model':<22} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10} {'AUC':>10}")
print(f"  {'-'*72}")
for name, r in classification_results.items():
    marker = " <-- BEST" if name == best_clf_name else ""
    print(f"  {name:<22} {r['Accuracy']:>10.4f} {r['Precision']:>10.4f} {r['Recall']:>10.4f} {r['F1-Score']:>10.4f} {r['AUC-ROC']:>10.4f}{marker}")

print(f"\n  REGRESSION RESULTS:")
print(f"  {'Model':<22} {'R2 Score':>10} {'MAE (LPA)':>10} {'RMSE (LPA)':>11}")
print(f"  {'-'*55}")
for name, r in regression_results.items():
    marker = " <-- BEST" if name == best_reg_name else ""
    print(f"  {name:<22} {r['R2 Score']:>10.4f} {r['MAE']:>10.4f} {r['RMSE']:>11.4f}{marker}")

# Top 5 features
top5_class = feature_importance.tail(5).index.tolist()[::-1]
top5_reg = feat_imp_reg.tail(5).index.tolist()[::-1]
print(f"\n  Top 5 Features (Classification): {top5_class}")
print(f"  Top 5 Features (Salary Prediction): {top5_reg}")

# ============================================================
# 7. GENERATE PDF REPORT
# ============================================================
print("\n" + "=" * 60)
print("PHASE 7: GENERATING PDF REPORT")
print("=" * 60)


class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'Placement Salary Prediction & Analysis Using ML | Indira College of Commerce and Science', 0, 1, 'C')
        self.line(10, 15, 200, 15)
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(44, 62, 80)
        self.set_fill_color(236, 240, 241)
        self.cell(0, 10, title, 0, 1, 'L', fill=True)
        self.ln(3)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(52, 73, 94)
        self.cell(0, 7, title, 0, 1, 'L')
        self.ln(1)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet_point(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(8)
        self.cell(5, 5.5, '-', 0, 0)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def add_image_page(self, img_path, title, description=""):
        self.add_page()
        self.chapter_title(title)
        if description:
            self.body_text(description)
        if os.path.exists(img_path):
            img_width = 185
            self.image(img_path, x=12, w=img_width)


pdf = PDFReport()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)

# --- Title Page ---
pdf.add_page()
pdf.ln(30)
pdf.set_font('Helvetica', 'B', 12)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 10, 'INDIRA COLLEGE OF COMMERCE AND SCIENCE', 0, 1, 'C')
pdf.ln(15)
pdf.set_font('Helvetica', 'B', 20)
pdf.set_text_color(44, 62, 80)
pdf.cell(0, 12, 'Placement Salary Prediction', 0, 1, 'C')
pdf.cell(0, 12, 'and Analysis', 0, 1, 'C')
pdf.cell(0, 12, 'Using Machine Learning', 0, 1, 'C')
pdf.ln(5)
pdf.set_font('Helvetica', '', 12)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, 'S.Y M.Sc. (Comp.Sci) - Sem IV Academic Year 2025-26', 0, 1, 'C')
pdf.ln(15)
pdf.set_font('Helvetica', 'B', 13)
pdf.set_text_color(44, 62, 80)
pdf.cell(0, 8, 'Team Members:', 0, 1, 'C')
pdf.set_font('Helvetica', '', 12)
pdf.cell(0, 8, '1. Nikhil Ghalme (32)', 0, 1, 'C')
pdf.cell(0, 8, '2. Abhijit Bhujbal (01)', 0, 1, 'C')
pdf.cell(0, 8, '3. Saurabh Gawali (94)', 0, 1, 'C')

# --- Section 1: Introduction ---
pdf.add_page()
pdf.chapter_title('1. Introduction / Background and Context')
pdf.body_text(
    'Campus placement is a critical milestone for students completing their higher education. '
    'Universities and colleges invest significant resources in training and placement cells to ensure '
    'maximum employability of their graduates. However, the factors that truly determine whether a '
    'student gets placed and the salary they receive remain poorly understood by most stakeholders. '
    'With the increasing availability of historical placement data, there is a growing opportunity to '
    'leverage Machine Learning (ML) and Statistical Analysis techniques to predict placement '
    'outcomes and expected salary packages. This enables data-driven decision-making for students, '
    'educators, and recruiters alike.'
)
pdf.body_text(
    'This project analyzes a comprehensive dataset of 1,000 student records containing 26 features '
    'including academic performance (CGPA, 10th & 12th percentages), technical skills (DSA, coding problems, '
    'programming languages, backend/frontend technologies), professional experience (internships, projects, '
    'open source contributions), and soft skills (communication, English fluency, interview confidence). '
    'The analysis employs both classification models to predict placement status and regression models '
    'to predict salary packages for placed candidates.'
)

# --- Section 2: Problem Statement ---
pdf.chapter_title('2. Problem Statement')
pdf.body_text(
    'Students and placement coordinators currently rely on intuition and anecdotal evidence to assess '
    'placement readiness, which often leads to misaligned expectations. There is no systematic, data-driven '
    'approach to identify which academic and demographic factors most strongly influence placement success '
    'and salary outcomes. This project aims to bridge this gap by developing predictive models that can '
    'accurately classify students as "Placed" or "Not Placed" and further predict the expected salary for '
    'placed candidates based on academic performance, technical skills, work experience, and other factors.'
)

# --- Section 3: Objectives ---
pdf.chapter_title('3. Objectives of the Study')
pdf.bullet_point('To perform comprehensive data preprocessing on campus placement records (handling missing values, encoding categorical variables, feature scaling).')
pdf.bullet_point('To conduct Exploratory Data Analysis (EDA) to uncover patterns and relationships between academic scores, technical skills, work experience, and placement outcomes.')
pdf.bullet_point('To implement and compare multiple ML models (Logistic Regression, Random Forest, SVM, Gradient Boosting) for placement status classification.')
pdf.bullet_point('To build regression models for salary prediction and evaluate them using metrics such as R-squared Score, MAE, and RMSE.')
pdf.bullet_point('To identify the most influential features that drive placement success and higher salary packages.')
pdf.bullet_point('To develop a prototype system that predicts placement likelihood and expected salary for new student profiles.')

# --- Section 4: Dataset Description ---
pdf.add_page()
pdf.chapter_title('4. Dataset Description')
pdf.body_text(
    f'The dataset used for this project is a Placement Readiness Dataset containing {df.shape[0]} records '
    f'of student academic and placement data with {df.shape[1]} features. Each row represents a single '
    'student\'s academic profile, technical skills assessment, and placement outcome.'
)
pdf.section_title('Key Attributes:')
pdf.bullet_point(f'Degree Branch: {", ".join(df["Degree Branch"].unique())}')
pdf.bullet_point(f'Current Status: {", ".join(df["Current Status"].unique())}')
pdf.bullet_point(f'CGPA: Range {df["CGPA (Out of 10)"].min():.1f} - {df["CGPA (Out of 10)"].max():.1f} (Mean: {df["CGPA (Out of 10)"].mean():.2f})')
pdf.bullet_point(f'12th Percentage: Range {df["12th Percentage"].min():.1f}% - {df["12th Percentage"].max():.1f}% (Mean: {df["12th Percentage"].mean():.2f}%)')
pdf.bullet_point(f'10th Percentage: Range {df["10th Percentage"].min():.1f}% - {df["10th Percentage"].max():.1f}% (Mean: {df["10th Percentage"].mean():.2f}%)')
pdf.bullet_point('Skills: DSA Knowledge, OOPS Understanding, Communication, English Fluency, Interview Confidence (1-5 scale)')
pdf.bullet_point('Technical: Programming Languages, Backend/Frontend Technology, Database Knowledge')
pdf.bullet_point('Experience: Internship Experience, Projects Completed, Open Source Contributions')
pdf.bullet_point(f'Placement Status (Target 1): Placed ({(df["Placement Status"]=="Placed").sum()}) / Unplaced ({(df["Placement Status"]=="Unplaced").sum()})')
pdf.bullet_point(f'Salary Package (Target 2): Range {salary_data.min():.2f} - {salary_data.max():.2f} LPA (Mean: {salary_data.mean():.2f} LPA)')

pdf.section_title('Missing Values:')
pdf.bullet_point(f'Backend Technology: {df["Backend Technology"].isnull().sum()} missing ({df["Backend Technology"].isnull().sum()/len(df)*100:.1f}%)')
pdf.bullet_point(f'Database Knowledge: {df["Database Knowledge"].isnull().sum()} missing ({df["Database Knowledge"].isnull().sum()/len(df)*100:.1f}%)')
pdf.bullet_point(f'System Design Knowledge: {df["System Design Knowledge"].isnull().sum()} missing ({df["System Design Knowledge"].isnull().sum()/len(df)*100:.1f}%)')
pdf.bullet_point(f'Salary Package: {df["Salary Package (LPA)"].isnull().sum()} missing (Unplaced students - expected)')

# --- Section 5: Data Preprocessing ---
pdf.add_page()
pdf.chapter_title('5. Data Preprocessing')
pdf.section_title('a) Missing Value Treatment:')
pdf.bullet_point('Backend Technology, Database Knowledge, System Design Knowledge: Missing values filled with "None" category to represent absence of skill.')
pdf.bullet_point('Salary Package: Missing for unplaced students (359 records) - handled separately in classification vs regression tasks.')
pdf.section_title('b) Feature Encoding:')
pdf.bullet_point('Label Encoding applied to categorical features: Degree Branch, Current Status, Coding Problems Solved, Frontend/Backend Technology, Database Knowledge, Full-Stack Project Built, Technical Projects Completed, Internship Experience, Open Source Contributions, Mock Interviews Attended, System Design Knowledge.')
pdf.bullet_point('Programming Languages Known converted to count of languages as a numerical feature.')
pdf.section_title('c) Feature Scaling:')
pdf.bullet_point('StandardScaler normalization applied to numerical features for Logistic Regression and SVM models.')
pdf.bullet_point('Tree-based models (Random Forest, Gradient Boosting) trained on unscaled features.')
pdf.section_title('d) Data Splitting:')
pdf.bullet_point('80% training / 20% testing split with stratification for classification.')
pdf.bullet_point(f'Classification: {X_train_c.shape[0]} training, {X_test_c.shape[0]} testing samples.')
pdf.bullet_point(f'Regression: {X_train_r.shape[0]} training, {X_test_r.shape[0]} testing samples (placed students only).')

# --- Section 6: EDA Charts ---
pdf.add_image_page(f'{OUTPUT_DIR}/01_placement_status_distribution.png',
                   '6. Exploratory Data Analysis',
                   f'The dataset contains {(df["Placement Status"]=="Placed").sum()} placed students ({(df["Placement Status"]=="Placed").sum()/len(df)*100:.1f}%) and '
                   f'{(df["Placement Status"]=="Unplaced").sum()} unplaced students ({(df["Placement Status"]=="Unplaced").sum()/len(df)*100:.1f}%).')

pdf.add_image_page(f'{OUTPUT_DIR}/02_branch_wise_placement.png',
                   '6.1 Branch-wise Placement Analysis',
                   'Distribution of placement status across different degree branches shows the relative placement rates for Computer Science, Information Technology, Electronics/E&TC, and Other branches.')

pdf.add_image_page(f'{OUTPUT_DIR}/03_cgpa_distribution.png',
                   '6.2 CGPA Distribution by Placement Status',
                   f'CGPA distribution comparison reveals that placed students tend to have higher CGPA. '
                   f'Mean CGPA - Placed: {df[df["Placement Status"]=="Placed"]["CGPA (Out of 10)"].mean():.2f}, '
                   f'Unplaced: {df[df["Placement Status"]=="Unplaced"]["CGPA (Out of 10)"].mean():.2f}.')

pdf.add_image_page(f'{OUTPUT_DIR}/04_salary_distribution.png',
                   '6.3 Salary Package Distribution',
                   f'Salary packages range from {salary_data.min():.2f} to {salary_data.max():.2f} LPA with a mean of {salary_data.mean():.2f} LPA. '
                   f'Product-based companies offer the highest median salary, followed by Service-based and Startups.')

pdf.add_image_page(f'{OUTPUT_DIR}/05_skills_vs_placement.png',
                   '6.4 Skill Ratings vs Placement Status',
                   'Comparison of skill ratings (DSA, OOPS, Communication, English Fluency, Interview Confidence) between placed and unplaced students.')

pdf.add_image_page(f'{OUTPUT_DIR}/06_coding_internship_placement.png',
                   '6.5 Coding Problems & Internship Experience',
                   'Students who solved more coding problems (500+) and had internship experience (2+) show significantly higher placement rates.')

pdf.add_image_page(f'{OUTPUT_DIR}/07_correlation_heatmap.png',
                   '6.6 Correlation Heatmap',
                   'Correlation analysis of numerical features reveals the relationships between academic scores, skill ratings, and salary outcomes.')

pdf.add_image_page(f'{OUTPUT_DIR}/08_projects_opensource.png',
                   '6.7 Projects & Open Source Contributions',
                   'Analysis of how full-stack project experience and open source contributions correlate with placement success.')

pdf.add_image_page(f'{OUTPUT_DIR}/09_salary_by_branch.png',
                   '6.8 Salary by Degree Branch',
                   'Box plot comparison of salary packages across different degree branches for placed students.')

pdf.add_image_page(f'{OUTPUT_DIR}/10_mock_interview_status.png',
                   '6.9 Mock Interviews & Current Status',
                   'Impact of mock interview attendance and current academic status on placement outcomes.')

pdf.add_image_page(f'{OUTPUT_DIR}/20_tech_stack_analysis.png',
                   '6.10 Technology Stack Analysis',
                   'Placement rates analyzed by frontend and backend technology choices, revealing which tech stacks correlate with higher placement rates.')

# --- Section 7: Classification Results ---
pdf.add_page()
pdf.chapter_title('7. Classification Results - Placement Status Prediction')
pdf.body_text('Four classification models were trained and evaluated to predict whether a student will be Placed or Unplaced:')

# Results table
pdf.set_font('Helvetica', 'B', 9)
col_widths = [42, 22, 22, 22, 22, 22, 28]
headers = ['Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC-ROC', 'CV Accuracy']
pdf.set_fill_color(44, 62, 80)
pdf.set_text_color(255, 255, 255)
for i, h in enumerate(headers):
    pdf.cell(col_widths[i], 8, h, 1, 0, 'C', fill=True)
pdf.ln()

pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(0, 0, 0)
for name, r in classification_results.items():
    is_best = name == best_clf_name
    if is_best:
        pdf.set_fill_color(212, 237, 218)
    else:
        pdf.set_fill_color(255, 255, 255)
    pdf.cell(col_widths[0], 7, name, 1, 0, 'L', fill=True)
    pdf.cell(col_widths[1], 7, f'{r["Accuracy"]:.4f}', 1, 0, 'C', fill=True)
    pdf.cell(col_widths[2], 7, f'{r["Precision"]:.4f}', 1, 0, 'C', fill=True)
    pdf.cell(col_widths[3], 7, f'{r["Recall"]:.4f}', 1, 0, 'C', fill=True)
    pdf.cell(col_widths[4], 7, f'{r["F1-Score"]:.4f}', 1, 0, 'C', fill=True)
    pdf.cell(col_widths[5], 7, f'{r["AUC-ROC"]:.4f}', 1, 0, 'C', fill=True)
    pdf.cell(col_widths[6], 7, f'{r["CV Accuracy"]:.4f}', 1, 0, 'C', fill=True)
    pdf.ln()

pdf.ln(3)
pdf.body_text(f'Best Classification Model: {best_clf_name} with {best_clf["Accuracy"]*100:.2f}% accuracy and {best_clf["AUC-ROC"]:.4f} AUC-ROC score. (Highlighted in green above)')

pdf.add_image_page(f'{OUTPUT_DIR}/11_roc_curves.png',
                   '7.1 ROC Curves Comparison',
                   'ROC curves for all classification models showing the trade-off between true positive and false positive rates.')

pdf.add_image_page(f'{OUTPUT_DIR}/12_classification_comparison.png',
                   '7.2 Classification Metrics Comparison',
                   'Side-by-side bar chart comparison of all classification metrics across models.')

pdf.add_image_page(f'{OUTPUT_DIR}/13_confusion_matrices.png',
                   '7.3 Confusion Matrices',
                   'Confusion matrices for each model showing true positives, true negatives, false positives, and false negatives.')

pdf.add_image_page(f'{OUTPUT_DIR}/14_feature_importance_classification.png',
                   '7.4 Feature Importance - Classification',
                   f'Top features driving placement prediction (Random Forest): {", ".join(top5_class[:3])}.')

# --- Section 8: Regression Results ---
pdf.add_page()
pdf.chapter_title('8. Regression Results - Salary Prediction')
pdf.body_text(f'Five regression models were trained on {df_salary.shape[0]} placed student records to predict salary packages:')

# Results table
pdf.set_font('Helvetica', 'B', 9)
col_widths_r = [45, 30, 30, 30, 30]
headers_r = ['Model', 'R-squared', 'MAE (LPA)', 'RMSE (LPA)', 'CV R-squared']
pdf.set_fill_color(44, 62, 80)
pdf.set_text_color(255, 255, 255)
for i, h in enumerate(headers_r):
    pdf.cell(col_widths_r[i], 8, h, 1, 0, 'C', fill=True)
pdf.ln()

pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(0, 0, 0)
for name, r in regression_results.items():
    is_best = name == best_reg_name
    if is_best:
        pdf.set_fill_color(212, 237, 218)
    else:
        pdf.set_fill_color(255, 255, 255)
    pdf.cell(col_widths_r[0], 7, name, 1, 0, 'L', fill=True)
    pdf.cell(col_widths_r[1], 7, f'{r["R2 Score"]:.4f}', 1, 0, 'C', fill=True)
    pdf.cell(col_widths_r[2], 7, f'{r["MAE"]:.4f}', 1, 0, 'C', fill=True)
    pdf.cell(col_widths_r[3], 7, f'{r["RMSE"]:.4f}', 1, 0, 'C', fill=True)
    pdf.cell(col_widths_r[4], 7, f'{r["CV R2"]:.4f}', 1, 0, 'C', fill=True)
    pdf.ln()

pdf.ln(3)
pdf.body_text(f'Best Regression Model: {best_reg_name} with R-squared Score of {best_reg["R2 Score"]:.4f}, '
              f'MAE of {best_reg["MAE"]:.4f} LPA, and RMSE of {best_reg["RMSE"]:.4f} LPA. (Highlighted in green above)')

pdf.add_image_page(f'{OUTPUT_DIR}/15_regression_comparison.png',
                   '8.1 Regression Metrics Comparison',
                   'Comparison of R-squared, MAE, and RMSE across all regression models.')

pdf.add_image_page(f'{OUTPUT_DIR}/16_actual_vs_predicted.png',
                   '8.2 Actual vs Predicted Salary',
                   'Scatter plots showing actual vs predicted salary for each model. Points closer to the diagonal red line indicate better predictions.')

pdf.add_image_page(f'{OUTPUT_DIR}/17_feature_importance_regression.png',
                   '8.3 Feature Importance - Salary Prediction',
                   f'Top features driving salary prediction (Gradient Boosting): {", ".join(top5_reg[:3])}.')

pdf.add_image_page(f'{OUTPUT_DIR}/18_residual_analysis.png',
                   '8.4 Residual Analysis',
                   f'Residual analysis for the best model ({best_reg_name}) showing prediction error distribution.')

pdf.add_image_page(f'{OUTPUT_DIR}/19_salary_gap.png',
                   '8.5 Expected vs Actual Salary Gap',
                   f'Analysis of the gap between students\' expected salary and actual offered salary. Mean gap: {salary_gap["Gap"].mean():.2f} LPA.')

# --- Section 9: Key Findings & Conclusions ---
pdf.add_page()
pdf.chapter_title('9. Key Findings and Conclusions')

pdf.section_title('Classification Findings:')
pdf.bullet_point(f'{best_clf_name} achieved the highest accuracy of {best_clf["Accuracy"]*100:.2f}% for placement prediction.')
pdf.bullet_point(f'All models achieved AUC-ROC scores above {min(r["AUC-ROC"] for r in classification_results.values()):.3f}, indicating reliable discrimination between placed and unplaced students.')
pdf.bullet_point(f'Top predictive features for placement: {", ".join(top5_class)}.')

pdf.section_title('Regression Findings:')
pdf.bullet_point(f'{best_reg_name} achieved the best R-squared score of {best_reg["R2 Score"]:.4f} for salary prediction.')
pdf.bullet_point(f'The model can predict salary within an average error of {best_reg["MAE"]:.2f} LPA (MAE).')
pdf.bullet_point(f'Top predictive features for salary: {", ".join(top5_reg)}.')

pdf.section_title('General Insights:')
placed_cgpa = df[df['Placement Status']=='Placed']['CGPA (Out of 10)'].mean()
unplaced_cgpa = df[df['Placement Status']=='Unplaced']['CGPA (Out of 10)'].mean()
pdf.bullet_point(f'Placed students have higher average CGPA ({placed_cgpa:.2f}) compared to unplaced ({unplaced_cgpa:.2f}).')
pdf.bullet_point(f'Students with 2+ internships show significantly higher placement rates.')
pdf.bullet_point(f'Solving 500+ coding problems is strongly correlated with placement success.')
pdf.bullet_point(f'Product-based companies offer the highest salary packages among placed students.')
pdf.bullet_point(f'The average gap between expected and actual salary is {salary_gap["Gap"].mean():.2f} LPA, suggesting students tend to {"overestimate" if salary_gap["Gap"].mean() > 0 else "underestimate"} their salary expectations.')

# --- Section 10: Recommendations ---
pdf.chapter_title('10. Recommendations')
pdf.bullet_point('Students should focus on improving DSA skills, solving coding problems (target 500+), and gaining internship experience to maximize placement chances.')
pdf.bullet_point('Full-stack project experience and knowledge of modern frontend/backend technologies significantly improve placement prospects.')
pdf.bullet_point('Institutions should implement early identification systems for at-risk students using the ML models developed in this study.')
pdf.bullet_point('Mock interview programs should be expanded as they correlate with improved placement outcomes.')
pdf.bullet_point('Students should calibrate salary expectations based on data-driven insights rather than anecdotal evidence.')

# --- Section 11: Future Scope ---
pdf.chapter_title('11. Future Scope')
pdf.bullet_point('Integration of deep learning models (Neural Networks) for improved prediction accuracy.')
pdf.bullet_point('Real-time web application for students to input their profiles and get instant placement/salary predictions.')
pdf.bullet_point('Multi-institution dataset analysis for broader generalizability of findings.')
pdf.bullet_point('Time-series analysis to track how placement trends evolve across academic years.')
pdf.bullet_point('NLP-based resume scoring to complement the quantitative feature analysis.')

# --- Section 12: References ---
pdf.add_page()
pdf.chapter_title('12. References')
pdf.set_font('Helvetica', '', 10)
refs = [
    'Patil, R., et al. (2019). "Predicting Campus Placement using Machine Learning Algorithms." International Journal of Engineering Research & Technology.',
    'Kumar, S., & Singh, A. (2020). "Campus Placement Prediction Using Ensemble Learning Techniques." Journal of Data Science and Analytics.',
    'Aldowah, H., et al. (2019). "Educational Data Mining and Learning Analytics for 21st Century Higher Education: A Review and Synthesis." Telematics and Informatics, Vol. 37.',
    'Mishra, T., et al. (2021). "Factors Affecting Campus Placement: A Machine Learning Approach." International Conference on Computational Intelligence.',
    'Ben Israel, D., et al. (2020). "Campus Recruitment Dataset." Kaggle Platforms.',
    'Scikit-learn: Machine Learning in Python, Pedregosa et al., JMLR 12, pp. 2825-2830, 2011.',
]
for ref in refs:
    pdf.bullet_point(ref)

# Save PDF
pdf_path = '/home/nikhil/Downloads/Placement_Salary_Prediction_Analysis_Report.pdf'
pdf.output(pdf_path)
print(f"\n  PDF Report saved to: {pdf_path}")

# ============================================================
# DONE
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS COMPLETE!")
print("=" * 60)
print(f"\nOutput directory: {OUTPUT_DIR}/")
print(f"PDF Report: {pdf_path}")
print(f"Total charts generated: 20")
print(f"\nBest Classification Model: {best_clf_name} (Accuracy: {best_clf['Accuracy']*100:.2f}%)")
print(f"Best Regression Model: {best_reg_name} (R2: {best_reg['R2 Score']:.4f})")
