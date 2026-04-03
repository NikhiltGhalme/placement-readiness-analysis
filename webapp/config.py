import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

DATA_PATH = os.path.join(PROJECT_DIR, 'placement_readiness_data.xlsx')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
CHARTS_DIR = os.path.join(OUTPUT_DIR, 'charts')
REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')
GENERATED_DIR = os.path.join(OUTPUT_DIR, 'generated')

for d in [OUTPUT_DIR, CHARTS_DIR, REPORTS_DIR, GENERATED_DIR]:
    os.makedirs(d, exist_ok=True)
