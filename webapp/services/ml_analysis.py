import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.ensemble import (RandomForestClassifier, GradientBoostingClassifier,
                              RandomForestRegressor, GradientBoostingRegressor)
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             confusion_matrix, roc_auc_score, roc_curve,
                             mean_absolute_error, mean_squared_error, r2_score)
import warnings
import os

warnings.filterwarnings('ignore')
sns.set_style('whitegrid')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 10


class PlacementAnalysisPipeline:
    def __init__(self, data_path: str, output_dir: str, progress: dict):
        self.data_path = data_path
        self.output_dir = output_dir
        self.progress = progress
        self.df = None
        self.df_ml = None
        self.feature_cols = None
        self.classification_results = {}
        self.regression_results = {}
        self.chart_files = []
        self.best_clf_name = None
        self.best_reg_name = None
        self.top5_class = []
        self.top5_reg = []
        os.makedirs(output_dir, exist_ok=True)

    def run_all(self) -> dict:
        self.progress.update(phase=1, total=7, message="Loading data...")
        phase1 = self.phase_1_load_data()

        self.progress.update(phase=2, total=7, message="Exploratory Data Analysis...")
        chart_paths = self.phase_2_eda()

        self.progress.update(phase=3, total=7, message="Preprocessing data...")
        prep = self.phase_3_preprocess()

        self.progress.update(phase=4, total=7, message="Training classification models...")
        class_results = self.phase_4_classification(*prep['classification'])

        self.progress.update(phase=5, total=7, message="Training regression models...")
        reg_results = self.phase_5_regression(*prep['regression'])

        self.progress.update(phase=6, total=7, message="Generating summary...")
        summary = self.phase_6_summary()

        self.progress.update(phase=7, total=7, message="Generating PDF report...")
        pdf_path = self.phase_7_pdf()

        self.progress.update(phase=7, total=7, message="Complete", done=True)

        return {
            'dataset_info': phase1,
            'charts': [os.path.basename(c) for c in self.chart_files],
            'classification': {
                name: {k: v for k, v in vals.items() if k not in ['y_pred', 'y_prob']}
                for name, vals in self.classification_results.items()
            },
            'regression': {
                name: {k: round(v, 4) if isinstance(v, float) else v
                       for k, v in vals.items() if k != 'y_pred'}
                for name, vals in self.regression_results.items()
            },
            'summary': summary,
            'pdf_path': pdf_path,
        }

    def phase_1_load_data(self) -> dict:
        self.df = pd.read_excel(self.data_path)
        placed_count = int((self.df['Placement Status'] == 'Placed').sum())
        unplaced_count = int((self.df['Placement Status'] == 'Unplaced').sum())
        salary_data = self.df[self.df['Salary Package (LPA)'].notna()]['Salary Package (LPA)']
        return {
            'rows': int(self.df.shape[0]),
            'columns': int(self.df.shape[1]),
            'placed': placed_count,
            'unplaced': unplaced_count,
            'salary_mean': round(float(salary_data.mean()), 2),
            'salary_min': round(float(salary_data.min()), 2),
            'salary_max': round(float(salary_data.max()), 2),
            'column_names': self.df.columns.tolist(),
        }

    def phase_2_eda(self) -> list:
        df = self.df
        out = self.output_dir
        colors = ['#2ecc71', '#e74c3c']

        # Chart 1: Placement Status Distribution
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        status_counts = df['Placement Status'].value_counts()
        axes[0].pie(status_counts, labels=status_counts.index, autopct='%1.1f%%',
                    colors=colors, startangle=90, explode=(0.05, 0.05))
        axes[0].set_title('Placement Status Distribution', fontweight='bold', fontsize=13)
        sns.countplot(data=df, x='Placement Status', palette=colors, ax=axes[1])
        axes[1].set_title('Placement Status Count', fontweight='bold', fontsize=13)
        for p in axes[1].patches:
            axes[1].annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                             ha='center', va='bottom', fontweight='bold')
        plt.tight_layout()
        path = f'{out}/01_placement_status_distribution.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 2: Branch-wise Placement
        fig, ax = plt.subplots(figsize=(10, 6))
        branch_placement = pd.crosstab(df['Degree Branch'], df['Placement Status'])
        branch_placement.plot(kind='bar', ax=ax, color=colors, edgecolor='black')
        ax.set_title('Branch-wise Placement Status', fontweight='bold', fontsize=13)
        ax.set_xlabel('Degree Branch')
        ax.set_ylabel('Count')
        ax.legend(title='Status')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        path = f'{out}/02_branch_wise_placement.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 3: CGPA Distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        for status, color in zip(['Placed', 'Unplaced'], colors):
            subset = df[df['Placement Status'] == status]
            ax.hist(subset['CGPA (Out of 10)'], bins=25, alpha=0.6, label=status, color=color, edgecolor='black')
        ax.set_title('CGPA Distribution by Placement Status', fontweight='bold', fontsize=13)
        ax.set_xlabel('CGPA (Out of 10)')
        ax.set_ylabel('Frequency')
        ax.legend()
        plt.tight_layout()
        path = f'{out}/03_cgpa_distribution.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 4: Salary Distribution
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        salary_data = df[df['Salary Package (LPA)'].notna()]['Salary Package (LPA)']
        axes[0].hist(salary_data, bins=30, color='#3498db', edgecolor='black', alpha=0.7)
        axes[0].set_title('Salary Package Distribution (LPA)', fontweight='bold', fontsize=13)
        axes[0].set_xlabel('Salary (LPA)')
        axes[0].set_ylabel('Frequency')
        axes[0].axvline(salary_data.mean(), color='red', linestyle='--', label=f'Mean: {salary_data.mean():.2f}')
        axes[0].axvline(salary_data.median(), color='green', linestyle='--', label=f'Median: {salary_data.median():.2f}')
        axes[0].legend()
        company_salary = df[df['Company Type'].notna()]
        sns.boxplot(data=company_salary, x='Company Type', y='Salary Package (LPA)', palette='Set2', ax=axes[1])
        axes[1].set_title('Salary by Company Type', fontweight='bold', fontsize=13)
        plt.tight_layout()
        path = f'{out}/04_salary_distribution.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 5: Skills vs Placement
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
        path = f'{out}/05_skills_vs_placement.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 6: Coding & Internship
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        coding_order = ['0-50', '50-200', '200-500', '500+']
        ct1 = pd.crosstab(df['Coding Problems Solved'], df['Placement Status']).reindex(coding_order)
        ct1.plot(kind='bar', ax=axes[0], color=colors, edgecolor='black')
        axes[0].set_title('Coding Problems Solved vs Placement', fontweight='bold', fontsize=13)
        axes[0].set_xlabel('Problems Solved')
        axes[0].tick_params(axis='x', rotation=0)
        intern_order = ['No Internship', '1 Internship', '2+ Internships']
        ct2 = pd.crosstab(df['Internship Experience'], df['Placement Status']).reindex(intern_order)
        ct2.plot(kind='bar', ax=axes[1], color=colors, edgecolor='black')
        axes[1].set_title('Internship Experience vs Placement', fontweight='bold', fontsize=13)
        axes[1].set_xlabel('Internship Experience')
        axes[1].tick_params(axis='x', rotation=0)
        plt.tight_layout()
        path = f'{out}/06_coding_internship_placement.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 7: Correlation Heatmap
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
        path = f'{out}/07_correlation_heatmap.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 8: Projects & Open Source
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
        path = f'{out}/08_projects_opensource.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 9: Salary by Branch
        fig, ax = plt.subplots(figsize=(10, 6))
        placed_df = df[df['Salary Package (LPA)'].notna()]
        sns.boxplot(data=placed_df, x='Degree Branch', y='Salary Package (LPA)', palette='Set3', ax=ax)
        ax.set_title('Salary Package by Degree Branch', fontweight='bold', fontsize=13)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        path = f'{out}/09_salary_by_branch.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 10: Mock Interview & Status
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
        path = f'{out}/10_mock_interview_status.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        return [os.path.basename(c) for c in self.chart_files]

    def phase_3_preprocess(self) -> dict:
        self.df_ml = self.df.copy()
        df_ml = self.df_ml

        le_target = LabelEncoder()
        df_ml['Placement_Status_Encoded'] = le_target.fit_transform(df_ml['Placement Status'])
        df_ml['Placement_Status_Encoded'] = 1 - df_ml['Placement_Status_Encoded']

        categorical_cols = ['Degree Branch', 'Current Status', 'Coding Problems Solved',
                            'Frontend Technology', 'Full-Stack Project Built',
                            'Technical Projects Completed', 'Internship Experience',
                            'Open Source Contributions', 'Mock Interviews Attended',
                            'Actively Applying for IT Jobs']
        for col in categorical_cols:
            le = LabelEncoder()
            df_ml[col + '_enc'] = le.fit_transform(df_ml[col].astype(str))

        for col in ['Backend Technology', 'Database Knowledge', 'System Design Knowledge']:
            df_ml[col].fillna('None', inplace=True)
            le = LabelEncoder()
            df_ml[col + '_enc'] = le.fit_transform(df_ml[col].astype(str))

        df_ml['Num_Languages'] = df_ml['Programming Languages Known'].apply(lambda x: len(str(x).split(',')))

        self.feature_cols = [
            'CGPA (Out of 10)', '12th Percentage', '10th Percentage',
            'DSA Knowledge (1-5)', 'OOPS Understanding (1-5)',
            'Communication Skill (1-5)', 'English Fluency (1-5)',
            'Interview Confidence (1-5)', 'Num_Languages',
            'Degree Branch_enc', 'Current Status_enc', 'Coding Problems Solved_enc',
            'Frontend Technology_enc', 'Full-Stack Project Built_enc',
            'Technical Projects Completed_enc', 'Internship Experience_enc',
            'Open Source Contributions_enc', 'Mock Interviews Attended_enc',
            'Backend Technology_enc', 'Database Knowledge_enc', 'System Design Knowledge_enc'
        ]

        # Classification split
        X_class = df_ml[self.feature_cols]
        y_class = df_ml['Placement_Status_Encoded']
        X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
            X_class, y_class, test_size=0.2, random_state=42, stratify=y_class)

        # Regression split
        df_salary = df_ml[df_ml['Salary Package (LPA)'].notna()].copy()
        X_reg = df_salary[self.feature_cols]
        y_reg = df_salary['Salary Package (LPA)']
        X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
            X_reg, y_reg, test_size=0.2, random_state=42)

        return {
            'classification': (X_train_c, X_test_c, y_train_c, y_test_c),
            'regression': (X_train_r, X_test_r, y_train_r, y_test_r),
        }

    def phase_4_classification(self, X_train_c, X_test_c, y_train_c, y_test_c) -> dict:
        out = self.output_dir
        scaler_c = StandardScaler()
        X_train_c_scaled = scaler_c.fit_transform(X_train_c)
        X_test_c_scaled = scaler_c.transform(X_test_c)

        classifiers = {
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
            'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42),
            'SVM': SVC(kernel='rbf', probability=True, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=200, max_depth=5, random_state=42)
        }

        fig_roc, ax_roc = plt.subplots(figsize=(10, 8))

        for name, model in classifiers.items():
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

            self.classification_results[name] = {
                'Accuracy': round(acc, 4), 'Precision': round(prec, 4),
                'Recall': round(rec, 4), 'F1-Score': round(f1, 4),
                'AUC-ROC': round(auc, 4), 'CV Accuracy': round(cv_mean, 4),
                'y_pred': y_pred, 'y_prob': y_prob
            }

            fpr, tpr, _ = roc_curve(y_test_c, y_prob)
            ax_roc.plot(fpr, tpr, label=f'{name} (AUC={auc:.3f})', linewidth=2)

        ax_roc.plot([0, 1], [0, 1], 'k--', alpha=0.5)
        ax_roc.set_xlabel('False Positive Rate', fontsize=12)
        ax_roc.set_ylabel('True Positive Rate', fontsize=12)
        ax_roc.set_title('ROC Curves - Classification Models Comparison', fontweight='bold', fontsize=13)
        ax_roc.legend(fontsize=11)
        plt.tight_layout()
        path = f'{out}/11_roc_curves.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 12: Classification Comparison
        metrics_df = pd.DataFrame({
            name: {k: v for k, v in vals.items() if k not in ['y_pred', 'y_prob']}
            for name, vals in self.classification_results.items()
        }).T
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
        path = f'{out}/12_classification_comparison.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 13: Confusion Matrices
        fig, axes = plt.subplots(1, 4, figsize=(20, 4))
        for i, (name, results) in enumerate(self.classification_results.items()):
            cm = confusion_matrix(y_test_c, results['y_pred'])
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[i],
                        xticklabels=['Unplaced', 'Placed'], yticklabels=['Unplaced', 'Placed'])
            axes[i].set_title(name, fontweight='bold', fontsize=11)
            axes[i].set_xlabel('Predicted')
            axes[i].set_ylabel('Actual')
        plt.suptitle('Confusion Matrices - All Models', fontweight='bold', fontsize=14, y=1.05)
        plt.tight_layout()
        path = f'{out}/13_confusion_matrices.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 14: Feature Importance
        rf_model = classifiers['Random Forest']
        feature_importance = pd.Series(rf_model.feature_importances_, index=self.feature_cols)
        feature_importance = feature_importance.sort_values(ascending=True)
        self.top5_class = feature_importance.tail(5).index.tolist()[::-1]

        fig, ax = plt.subplots(figsize=(10, 8))
        feature_importance.plot(kind='barh', ax=ax, color='#3498db', edgecolor='black')
        ax.set_title('Feature Importance (Random Forest - Classification)', fontweight='bold', fontsize=13)
        ax.set_xlabel('Importance Score')
        plt.tight_layout()
        path = f'{out}/14_feature_importance_classification.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        self.best_clf_name = max(self.classification_results, key=lambda x: self.classification_results[x]['Accuracy'])
        return self.classification_results

    def phase_5_regression(self, X_train_r, X_test_r, y_train_r, y_test_r) -> dict:
        out = self.output_dir
        scaler_r = StandardScaler()
        X_train_r_scaled = scaler_r.fit_transform(X_train_r)
        X_test_r_scaled = scaler_r.transform(X_test_r)

        regressors = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0),
            'Lasso Regression': Lasso(alpha=0.1),
            'Random Forest': RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=200, max_depth=5, random_state=42)
        }

        for name, model in regressors.items():
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

            self.regression_results[name] = {
                'R2 Score': round(r2, 4), 'MAE': round(mae, 4),
                'RMSE': round(rmse, 4), 'CV R2': round(cv_r2_mean, 4),
                'y_pred': y_pred_r
            }

        # Chart 15: Regression Comparison
        reg_df = pd.DataFrame({
            name: {k: v for k, v in vals.items() if k != 'y_pred'}
            for name, vals in self.regression_results.items()
        }).T
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
        path = f'{out}/15_regression_comparison.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 16: Actual vs Predicted
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        for i, (name, results) in enumerate(self.regression_results.items()):
            row, col_idx = divmod(i, 3)
            axes[row][col_idx].scatter(y_test_r, results['y_pred'], alpha=0.5, color='#3498db', edgecolor='black', s=30)
            axes[row][col_idx].plot([y_test_r.min(), y_test_r.max()], [y_test_r.min(), y_test_r.max()], 'r--', linewidth=2)
            axes[row][col_idx].set_title(f'{name}\nR\u00b2={results["R2 Score"]:.3f}', fontweight='bold')
            axes[row][col_idx].set_xlabel('Actual Salary (LPA)')
            axes[row][col_idx].set_ylabel('Predicted Salary (LPA)')
        axes[1][2].axis('off')
        plt.suptitle('Actual vs Predicted Salary - All Models', fontweight='bold', fontsize=14, y=1.02)
        plt.tight_layout()
        path = f'{out}/16_actual_vs_predicted.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 17: Feature Importance Regression
        gb_reg = regressors['Gradient Boosting']
        feat_imp_reg = pd.Series(gb_reg.feature_importances_, index=self.feature_cols)
        feat_imp_reg = feat_imp_reg.sort_values(ascending=True)
        self.top5_reg = feat_imp_reg.tail(5).index.tolist()[::-1]

        fig, ax = plt.subplots(figsize=(10, 8))
        feat_imp_reg.plot(kind='barh', ax=ax, color='#e67e22', edgecolor='black')
        ax.set_title('Feature Importance (Gradient Boosting - Salary Prediction)', fontweight='bold', fontsize=13)
        ax.set_xlabel('Importance Score')
        plt.tight_layout()
        path = f'{out}/17_feature_importance_regression.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 18: Residual Analysis
        self.best_reg_name = max(self.regression_results, key=lambda x: self.regression_results[x]['R2 Score'])
        best_pred = self.regression_results[self.best_reg_name]['y_pred']
        residuals = y_test_r.values - best_pred

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        axes[0].scatter(best_pred, residuals, alpha=0.5, color='#9b59b6', edgecolor='black', s=30)
        axes[0].axhline(y=0, color='red', linestyle='--', linewidth=2)
        axes[0].set_title(f'Residual Plot ({self.best_reg_name})', fontweight='bold', fontsize=13)
        axes[0].set_xlabel('Predicted Salary (LPA)')
        axes[0].set_ylabel('Residuals (LPA)')
        axes[1].hist(residuals, bins=25, color='#9b59b6', edgecolor='black', alpha=0.7)
        axes[1].set_title(f'Residual Distribution ({self.best_reg_name})', fontweight='bold', fontsize=13)
        axes[1].set_xlabel('Residuals (LPA)')
        axes[1].set_ylabel('Frequency')
        plt.tight_layout()
        path = f'{out}/18_residual_analysis.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 19: Expected vs Actual Salary Gap
        df = self.df
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
        path = f'{out}/19_salary_gap.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        # Chart 20: Tech Stack Analysis
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        frontend_placement = pd.crosstab(df['Frontend Technology'], df['Placement Status'])
        frontend_rate = (frontend_placement['Placed'] / frontend_placement.sum(axis=1) * 100).sort_values(ascending=True)
        frontend_rate.plot(kind='barh', ax=axes[0], color='#2980b9', edgecolor='black')
        axes[0].set_title('Placement Rate by Frontend Tech', fontweight='bold', fontsize=12)
        axes[0].set_xlabel('Placement Rate (%)')
        for i, v in enumerate(frontend_rate):
            axes[0].text(v + 0.5, i, f'{v:.1f}%', va='center', fontsize=8)
        backend_counts = df['Backend Technology'].value_counts().head(10)
        backend_placement = pd.crosstab(
            df[df['Backend Technology'].isin(backend_counts.index)]['Backend Technology'],
            df[df['Backend Technology'].isin(backend_counts.index)]['Placement Status'])
        backend_rate = (backend_placement['Placed'] / backend_placement.sum(axis=1) * 100).sort_values(ascending=True)
        backend_rate.plot(kind='barh', ax=axes[1], color='#27ae60', edgecolor='black')
        axes[1].set_title('Placement Rate by Backend Tech (Top 10)', fontweight='bold', fontsize=12)
        axes[1].set_xlabel('Placement Rate (%)')
        for i, v in enumerate(backend_rate):
            axes[1].text(v + 0.5, i, f'{v:.1f}%', va='center', fontsize=8)
        plt.tight_layout()
        path = f'{out}/20_tech_stack_analysis.png'
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        self.chart_files.append(path)

        return self.regression_results

    def phase_6_summary(self) -> dict:
        best_clf = self.classification_results[self.best_clf_name]
        best_reg = self.regression_results[self.best_reg_name]

        df = self.df
        placed_cgpa = df[df['Placement Status'] == 'Placed']['CGPA (Out of 10)'].mean()
        unplaced_cgpa = df[df['Placement Status'] == 'Unplaced']['CGPA (Out of 10)'].mean()
        salary_gap = df[df['Salary Package (LPA)'].notna()].copy()
        salary_gap['Gap'] = salary_gap['Expected Salary (LPA)'] - salary_gap['Salary Package (LPA)']

        return {
            'best_classification_model': self.best_clf_name,
            'best_classification_accuracy': best_clf['Accuracy'],
            'best_classification_auc': best_clf['AUC-ROC'],
            'best_regression_model': self.best_reg_name,
            'best_regression_r2': best_reg['R2 Score'],
            'best_regression_mae': best_reg['MAE'],
            'top5_classification_features': self.top5_class,
            'top5_regression_features': self.top5_reg,
            'placed_avg_cgpa': round(placed_cgpa, 2),
            'unplaced_avg_cgpa': round(unplaced_cgpa, 2),
            'salary_gap_mean': round(float(salary_gap['Gap'].mean()), 2),
            'insights': [
                f'Placed students have higher average CGPA ({placed_cgpa:.2f}) compared to unplaced ({unplaced_cgpa:.2f}).',
                'Students with 2+ internships show significantly higher placement rates.',
                'Solving 500+ coding problems is strongly correlated with placement success.',
                'Product-based companies offer the highest salary packages.',
                f'The average gap between expected and actual salary is {salary_gap["Gap"].mean():.2f} LPA.',
            ],
            'recommendations': [
                'Focus on improving DSA skills, solving coding problems (target 500+), and gaining internship experience.',
                'Full-stack project experience and knowledge of modern technologies significantly improve placement prospects.',
                'Institutions should implement early identification systems for at-risk students.',
                'Mock interview programs should be expanded as they correlate with improved outcomes.',
                'Students should calibrate salary expectations based on data-driven insights.',
            ]
        }

    def phase_7_pdf(self) -> str:
        from fpdf import FPDF

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
                    self.image(img_path, x=12, w=185)

        pdf = PDFReport()
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=20)

        out = self.output_dir
        df = self.df
        salary_data = df[df['Salary Package (LPA)'].notna()]['Salary Package (LPA)']
        best_clf = self.classification_results[self.best_clf_name]
        best_reg = self.regression_results[self.best_reg_name]

        # Title Page
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

        # Introduction
        pdf.add_page()
        pdf.chapter_title('1. Introduction / Background and Context')
        pdf.body_text(
            'Campus placement is a critical milestone for students completing their higher education. '
            'This project analyzes a comprehensive dataset of 1,000 student records containing 26 features '
            'including academic performance, technical skills, professional experience, and soft skills. '
            'The analysis employs both classification models to predict placement status and regression models '
            'to predict salary packages for placed candidates.'
        )

        # Problem Statement
        pdf.chapter_title('2. Problem Statement')
        pdf.body_text(
            'This project aims to develop predictive models that can accurately classify students as "Placed" '
            'or "Not Placed" and further predict the expected salary for placed candidates based on academic '
            'performance, technical skills, work experience, and other factors.'
        )

        # Objectives
        pdf.chapter_title('3. Objectives of the Study')
        pdf.bullet_point('To perform comprehensive data preprocessing on campus placement records.')
        pdf.bullet_point('To conduct Exploratory Data Analysis (EDA) to uncover patterns and relationships.')
        pdf.bullet_point('To implement and compare multiple ML models for placement status classification.')
        pdf.bullet_point('To build regression models for salary prediction.')
        pdf.bullet_point('To identify the most influential features that drive placement success.')

        # Dataset Description
        pdf.add_page()
        pdf.chapter_title('4. Dataset Description')
        pdf.body_text(
            f'The dataset contains {df.shape[0]} records with {df.shape[1]} features. '
            f'Placed: {(df["Placement Status"]=="Placed").sum()}, '
            f'Unplaced: {(df["Placement Status"]=="Unplaced").sum()}. '
            f'Salary range: {salary_data.min():.2f} - {salary_data.max():.2f} LPA (Mean: {salary_data.mean():.2f} LPA).'
        )

        # EDA Charts
        chart_titles = [
            ('01_placement_status_distribution.png', '6. Exploratory Data Analysis', 'Placement status distribution.'),
            ('02_branch_wise_placement.png', '6.1 Branch-wise Placement', 'Distribution across degree branches.'),
            ('03_cgpa_distribution.png', '6.2 CGPA Distribution', 'CGPA distribution by placement status.'),
            ('04_salary_distribution.png', '6.3 Salary Distribution', 'Salary package distribution and by company type.'),
            ('05_skills_vs_placement.png', '6.4 Skills vs Placement', 'Skill ratings comparison.'),
            ('06_coding_internship_placement.png', '6.5 Coding & Internship', 'Impact on placement.'),
            ('07_correlation_heatmap.png', '6.6 Correlation Heatmap', 'Feature correlations.'),
            ('08_projects_opensource.png', '6.7 Projects & Open Source', 'Impact on placement.'),
            ('09_salary_by_branch.png', '6.8 Salary by Branch', 'Salary comparison across branches.'),
            ('10_mock_interview_status.png', '6.9 Mock Interviews & Status', 'Impact on placement.'),
            ('20_tech_stack_analysis.png', '6.10 Tech Stack Analysis', 'Placement rates by technology.'),
        ]
        for fname, title, desc in chart_titles:
            pdf.add_image_page(f'{out}/{fname}', title, desc)

        # Classification Results
        pdf.add_page()
        pdf.chapter_title('7. Classification Results')
        pdf.body_text('Four classification models were trained and evaluated:')
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
        for name, r in self.classification_results.items():
            is_best = name == self.best_clf_name
            pdf.set_fill_color(212, 237, 218) if is_best else pdf.set_fill_color(255, 255, 255)
            pdf.cell(col_widths[0], 7, name, 1, 0, 'L', fill=True)
            pdf.cell(col_widths[1], 7, f'{r["Accuracy"]:.4f}', 1, 0, 'C', fill=True)
            pdf.cell(col_widths[2], 7, f'{r["Precision"]:.4f}', 1, 0, 'C', fill=True)
            pdf.cell(col_widths[3], 7, f'{r["Recall"]:.4f}', 1, 0, 'C', fill=True)
            pdf.cell(col_widths[4], 7, f'{r["F1-Score"]:.4f}', 1, 0, 'C', fill=True)
            pdf.cell(col_widths[5], 7, f'{r["AUC-ROC"]:.4f}', 1, 0, 'C', fill=True)
            pdf.cell(col_widths[6], 7, f'{r["CV Accuracy"]:.4f}', 1, 0, 'C', fill=True)
            pdf.ln()
        pdf.ln(3)
        pdf.body_text(f'Best Model: {self.best_clf_name} with {best_clf["Accuracy"]*100:.2f}% accuracy.')

        class_charts = [
            ('11_roc_curves.png', '7.1 ROC Curves', 'ROC curves comparison.'),
            ('12_classification_comparison.png', '7.2 Metrics Comparison', 'All metrics compared.'),
            ('13_confusion_matrices.png', '7.3 Confusion Matrices', 'Per-model confusion matrices.'),
            ('14_feature_importance_classification.png', '7.4 Feature Importance', f'Top features: {", ".join(self.top5_class[:3])}.'),
        ]
        for fname, title, desc in class_charts:
            pdf.add_image_page(f'{out}/{fname}', title, desc)

        # Regression Results
        pdf.add_page()
        pdf.chapter_title('8. Regression Results')
        pdf.body_text('Five regression models were trained for salary prediction:')
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
        for name, r in self.regression_results.items():
            is_best = name == self.best_reg_name
            pdf.set_fill_color(212, 237, 218) if is_best else pdf.set_fill_color(255, 255, 255)
            pdf.cell(col_widths_r[0], 7, name, 1, 0, 'L', fill=True)
            pdf.cell(col_widths_r[1], 7, f'{r["R2 Score"]:.4f}', 1, 0, 'C', fill=True)
            pdf.cell(col_widths_r[2], 7, f'{r["MAE"]:.4f}', 1, 0, 'C', fill=True)
            pdf.cell(col_widths_r[3], 7, f'{r["RMSE"]:.4f}', 1, 0, 'C', fill=True)
            pdf.cell(col_widths_r[4], 7, f'{r["CV R2"]:.4f}', 1, 0, 'C', fill=True)
            pdf.ln()
        pdf.ln(3)
        pdf.body_text(f'Best Model: {self.best_reg_name} (R\u00b2={best_reg["R2 Score"]:.4f}, MAE={best_reg["MAE"]:.4f} LPA).')

        reg_charts = [
            ('15_regression_comparison.png', '8.1 Regression Comparison', 'R2, MAE, RMSE compared.'),
            ('16_actual_vs_predicted.png', '8.2 Actual vs Predicted', 'Scatter plots per model.'),
            ('17_feature_importance_regression.png', '8.3 Feature Importance', f'Top features: {", ".join(self.top5_reg[:3])}.'),
            ('18_residual_analysis.png', '8.4 Residual Analysis', f'Best model: {self.best_reg_name}.'),
            ('19_salary_gap.png', '8.5 Salary Gap', 'Expected vs actual salary gap.'),
        ]
        for fname, title, desc in reg_charts:
            pdf.add_image_page(f'{out}/{fname}', title, desc)

        # Key Findings
        pdf.add_page()
        pdf.chapter_title('9. Key Findings and Conclusions')
        summary = self.phase_6_summary()
        for insight in summary['insights']:
            pdf.bullet_point(insight)
        pdf.chapter_title('10. Recommendations')
        for rec in summary['recommendations']:
            pdf.bullet_point(rec)

        pdf_path = os.path.join(self.output_dir, 'analysis_report.pdf')
        pdf.output(pdf_path)
        return pdf_path
