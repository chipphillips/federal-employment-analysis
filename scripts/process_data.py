#!/usr/bin/env python3
"""
Federal Employment Data Processing Script
Processes the raw 780MB CSV and exports aggregated data for the dashboard.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import sys

# Paths
RAW_DATA_PATH = Path('/mnt/c/Users/chipp/Downloads/employment_202511_1_2026-01-21.csv')
PROCESSED_DATA_PATH = Path(__file__).parent.parent / 'data' / 'processed'
PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Federal Employment Data Processing")
print("=" * 60)

# Check if file exists
if not RAW_DATA_PATH.exists():
    print(f"ERROR: Raw data file not found at {RAW_DATA_PATH}")
    sys.exit(1)

print(f"\nSource file: {RAW_DATA_PATH}")
print(f"Output directory: {PROCESSED_DATA_PATH}")

# Define optimized dtypes
dtype_map = {
    'age_bracket': 'category',
    'agency': 'category',
    'agency_code': 'category',
    'agency_subelement': 'category',
    'agency_subelement_code': 'category',
    'annualized_adjusted_basic_pay': 'object',
    'appointment_type': 'category',
    'appointment_type_code': 'category',
    'count': 'int32',
    'duty_station_country': 'category',
    'duty_station_country_code': 'category',
    'duty_station_state': 'category',
    'duty_station_state_abbreviation': 'category',
    'duty_station_state_code': 'category',
    'education_level': 'category',
    'education_level_code': 'category',
    'grade': 'object',
    'length_of_service_years': 'float32',
    'occupational_group': 'category',
    'occupational_group_code': 'category',
    'occupational_series': 'category',
    'occupational_series_code': 'category',
    'pay_plan': 'category',
    'pay_plan_code': 'category',
    'snapshot_yyyymm': 'int32',
    'stem_occupation': 'category',
    'stem_occupation_type': 'category',
    'supervisory_status': 'category',
    'supervisory_status_code': 'category',
    'work_schedule': 'category',
    'work_schedule_code': 'category'
}

print("\n[1/8] Loading data (this may take a moment for 780MB)...")
df = pd.read_csv(RAW_DATA_PATH, sep='|', dtype=dtype_map, low_memory=False)
print(f"      Loaded {len(df):,} rows and {len(df.columns)} columns")
print(f"      Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")

print("\n[2/8] Cleaning data...")
# Convert pay to numeric
df['pay_numeric'] = pd.to_numeric(df['annualized_adjusted_basic_pay'], errors='coerce')
df['is_redacted'] = df['annualized_adjusted_basic_pay'] == 'REDACTED'
df['grade_numeric'] = pd.to_numeric(df['grade'], errors='coerce')

# Create tenure categories
def categorize_tenure(years):
    if pd.isna(years): return 'Unknown'
    elif years < 1: return '< 1 year'
    elif years < 5: return '1-5 years'
    elif years < 10: return '5-10 years'
    elif years < 20: return '10-20 years'
    elif years < 30: return '20-30 years'
    else: return '30+ years'

df['tenure_category'] = df['length_of_service_years'].apply(categorize_tenure).astype('category')

# Create pay bands
def categorize_pay(pay):
    if pd.isna(pay): return 'Unknown/Redacted'
    elif pay < 40000: return '< $40K'
    elif pay < 60000: return '$40K-$60K'
    elif pay < 80000: return '$60K-$80K'
    elif pay < 100000: return '$80K-$100K'
    elif pay < 150000: return '$100K-$150K'
    elif pay < 200000: return '$150K-$200K'
    else: return '$200K+'

df['pay_band'] = df['pay_numeric'].apply(categorize_pay).astype('category')

print(f"      Records with salary: {df['pay_numeric'].notna().sum():,}")
print(f"      Records REDACTED: {df['is_redacted'].sum():,}")

print("\n[3/8] Exporting agency summary...")
agency_export = df.groupby(['agency', 'agency_code']).agg({
    'count': 'sum',
    'pay_numeric': ['mean', 'median', 'std'],
    'length_of_service_years': ['mean', 'median'],
    'grade_numeric': 'mean',
    'is_redacted': 'sum'
}).round(2)
agency_export.columns = ['_'.join(col).strip('_') for col in agency_export.columns]
agency_export = agency_export.reset_index()
agency_export.to_csv(PROCESSED_DATA_PATH / 'agency_summary.csv', index=False)
print(f"      {len(agency_export)} agencies")

print("\n[4/8] Exporting state summary...")
state_export = df.groupby(['duty_station_state', 'duty_station_state_abbreviation']).agg({
    'count': 'sum',
    'pay_numeric': ['mean', 'median'],
    'length_of_service_years': 'mean'
}).round(2)
state_export.columns = ['_'.join(col).strip('_') for col in state_export.columns]
state_export = state_export.reset_index()
state_export.to_csv(PROCESSED_DATA_PATH / 'state_summary.csv', index=False)
print(f"      {len(state_export)} states/territories")

print("\n[5/8] Exporting occupation summary...")
occupation_export = df.groupby(['occupational_group', 'occupational_series', 'stem_occupation']).agg({
    'count': 'sum',
    'pay_numeric': ['mean', 'median'],
    'length_of_service_years': 'mean',
    'grade_numeric': 'mean'
}).round(2)
occupation_export.columns = ['_'.join(col).strip('_') for col in occupation_export.columns]
occupation_export = occupation_export.reset_index()
occupation_export.to_csv(PROCESSED_DATA_PATH / 'occupation_summary.csv', index=False)
print(f"      {len(occupation_export)} occupation series")

print("\n[6/8] Exporting demographics summary...")
demographics_export = df.groupby(['age_bracket', 'education_level', 'tenure_category']).agg({
    'count': 'sum',
    'pay_numeric': 'mean'
}).round(2)
demographics_export.columns = ['employee_count', 'avg_pay']
demographics_export = demographics_export.reset_index()
demographics_export.to_csv(PROCESSED_DATA_PATH / 'demographics_summary.csv', index=False)
print(f"      {len(demographics_export)} demographic combinations")

print("\n[7/8] Exporting pay distribution and appointment data...")
pay_distribution = df.groupby(['pay_band', 'agency']).agg({'count': 'sum'}).reset_index()
pay_distribution.to_csv(PROCESSED_DATA_PATH / 'pay_distribution.csv', index=False)
print(f"      {len(pay_distribution)} pay distribution rows")

appointment_export = df.groupby(['appointment_type', 'agency']).agg({
    'count': 'sum',
    'pay_numeric': 'mean',
    'length_of_service_years': 'mean'
}).round(2)
appointment_export.columns = ['employee_count', 'avg_pay', 'avg_tenure']
appointment_export = appointment_export.reset_index()
appointment_export.to_csv(PROCESSED_DATA_PATH / 'appointment_summary.csv', index=False)
print(f"      {len(appointment_export)} appointment type rows")

print("\n[8/8] Exporting overall statistics...")
overall_stats = {
    'total_employees': int(df['count'].sum()),
    'total_agencies': int(df['agency'].nunique()),
    'total_states': int(df['duty_station_state'].nunique()),
    'avg_salary': round(float(df['pay_numeric'].mean()), 2),
    'median_salary': round(float(df['pay_numeric'].median()), 2),
    'avg_tenure': round(float(df['length_of_service_years'].mean()), 2),
    'pct_redacted': round(float(df['is_redacted'].mean() * 100), 2),
    'snapshot_date': int(df['snapshot_yyyymm'].iloc[0])
}

with open(PROCESSED_DATA_PATH / 'overall_stats.json', 'w') as f:
    json.dump(overall_stats, f, indent=2)

print("\n" + "=" * 60)
print("OVERALL STATISTICS")
print("=" * 60)
for k, v in overall_stats.items():
    if isinstance(v, int) and v > 1000:
        print(f"  {k}: {v:,}")
    elif isinstance(v, float):
        print(f"  {k}: {v:,.2f}")
    else:
        print(f"  {k}: {v}")

print("\n" + "=" * 60)
print("EXPORTED FILES")
print("=" * 60)
for f in sorted(PROCESSED_DATA_PATH.glob('*')):
    size_kb = f.stat().st_size / 1024
    print(f"  {f.name}: {size_kb:.1f} KB")

print("\n[DONE] Data processing complete!")
print(f"Dashboard ready at: ../dashboard/index.html")
