#!/usr/bin/env python3
"""
Create clean aggregated data and generate a professional dashboard with embedded data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

# Paths
RAW_DATA_PATH = Path('/mnt/c/Users/chipp/Downloads/employment_202511_1_2026-01-21.csv')
OUTPUT_PATH = Path('/mnt/c/Users/chipp/federal-employment-analysis/dashboard')

print("Loading data...")
dtype_map = {
    'age_bracket': 'category',
    'agency': 'category',
    'agency_code': 'category',
    'agency_subelement': 'category',
    'annualized_adjusted_basic_pay': 'object',
    'appointment_type': 'category',
    'count': 'int32',
    'duty_station_state': 'category',
    'duty_station_state_abbreviation': 'category',
    'education_level': 'category',
    'grade': 'object',
    'length_of_service_years': 'float32',
    'occupational_group': 'category',
    'occupational_series': 'category',
    'pay_plan': 'category',
    'stem_occupation': 'category',
    'supervisory_status': 'category',
    'work_schedule': 'category'
}

df = pd.read_csv(RAW_DATA_PATH, sep='|', dtype=dtype_map, low_memory=False, usecols=list(dtype_map.keys()))
print(f"Loaded {len(df):,} rows")

# Clean data
df['pay_numeric'] = pd.to_numeric(df['annualized_adjusted_basic_pay'], errors='coerce')
df['grade_numeric'] = pd.to_numeric(df['grade'], errors='coerce')

# Agency summary - aggregate by agency name only, filter zeros
print("Creating agency summary...")
agency_data = df.groupby('agency', observed=True).agg({
    'count': 'sum',
    'pay_numeric': ['mean', 'median'],
    'length_of_service_years': 'mean',
    'grade_numeric': 'mean'
}).round(2)
agency_data.columns = ['employees', 'avg_pay', 'median_pay', 'avg_tenure', 'avg_grade']
agency_data = agency_data[agency_data['employees'] > 0].reset_index()
agency_data = agency_data.sort_values('employees', ascending=False)
print(f"  {len(agency_data)} agencies with employees")

# State summary
print("Creating state summary...")
state_data = df.groupby(['duty_station_state', 'duty_station_state_abbreviation'], observed=True).agg({
    'count': 'sum',
    'pay_numeric': ['mean', 'median'],
    'length_of_service_years': 'mean'
}).round(2)
state_data.columns = ['employees', 'avg_pay', 'median_pay', 'avg_tenure']
state_data = state_data[state_data['employees'] > 0].reset_index()
state_data = state_data.sort_values('employees', ascending=False)
# Filter out REDACTED
state_data = state_data[state_data['duty_station_state'] != 'REDACTED']
print(f"  {len(state_data)} states")

# Pay distribution
print("Creating pay distribution...")
def pay_band(pay):
    if pd.isna(pay): return 'Redacted'
    elif pay < 50000: return 'Under $50K'
    elif pay < 75000: return '$50K-$75K'
    elif pay < 100000: return '$75K-$100K'
    elif pay < 125000: return '$100K-$125K'
    elif pay < 150000: return '$125K-$150K'
    elif pay < 200000: return '$150K-$200K'
    else: return '$200K+'

df['pay_band'] = df['pay_numeric'].apply(pay_band)
pay_dist = df.groupby('pay_band', observed=True)['count'].sum().reset_index()
pay_dist.columns = ['band', 'employees']
# Order properly
band_order = ['Under $50K', '$50K-$75K', '$75K-$100K', '$100K-$125K', '$125K-$150K', '$150K-$200K', '$200K+', 'Redacted']
pay_dist['order'] = pay_dist['band'].apply(lambda x: band_order.index(x) if x in band_order else 99)
pay_dist = pay_dist.sort_values('order').drop('order', axis=1)

# Education summary
print("Creating education summary...")
edu_data = df.groupby('education_level', observed=True).agg({
    'count': 'sum',
    'pay_numeric': 'mean'
}).round(2)
edu_data.columns = ['employees', 'avg_pay']
edu_data = edu_data[edu_data['employees'] > 0].reset_index()
edu_data = edu_data.sort_values('avg_pay', ascending=False)

# Appointment type summary
print("Creating appointment summary...")
appt_data = df.groupby('appointment_type', observed=True).agg({
    'count': 'sum',
    'pay_numeric': 'mean',
    'length_of_service_years': 'mean'
}).round(2)
appt_data.columns = ['employees', 'avg_pay', 'avg_tenure']
appt_data = appt_data[appt_data['employees'] > 0].reset_index()
appt_data = appt_data.sort_values('employees', ascending=False)

# Age bracket summary
print("Creating age summary...")
age_data = df.groupby('age_bracket', observed=True).agg({
    'count': 'sum',
    'pay_numeric': 'mean',
    'length_of_service_years': 'mean'
}).round(2)
age_data.columns = ['employees', 'avg_pay', 'avg_tenure']
age_data = age_data[age_data['employees'] > 0].reset_index()
# Order age brackets
age_order = ['LESS THAN 20', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65 OR MORE']
age_data['order'] = age_data['age_bracket'].apply(lambda x: age_order.index(x) if x in age_order else 99)
age_data = age_data.sort_values('order').drop('order', axis=1)

# STEM comparison
print("Creating STEM comparison...")
stem_data = df.groupby('stem_occupation', observed=True).agg({
    'count': 'sum',
    'pay_numeric': 'mean',
    'length_of_service_years': 'mean'
}).round(2)
stem_data.columns = ['employees', 'avg_pay', 'avg_tenure']
stem_data = stem_data[stem_data['employees'] > 0].reset_index()

# Supervisory status
print("Creating supervisory summary...")
super_data = df.groupby('supervisory_status', observed=True).agg({
    'count': 'sum',
    'pay_numeric': 'mean'
}).round(2)
super_data.columns = ['employees', 'avg_pay']
super_data = super_data[super_data['employees'] > 0].reset_index()
super_data = super_data.sort_values('employees', ascending=False)

# Overall stats
overall = {
    'total_employees': int(df['count'].sum()),
    'total_agencies': int(agency_data['agency'].nunique()),
    'total_states': len(state_data),
    'avg_salary': round(float(df['pay_numeric'].mean()), 0),
    'median_salary': round(float(df['pay_numeric'].median()), 0),
    'avg_tenure': round(float(df['length_of_service_years'].mean()), 1),
    'pct_stem': round(float(df[df['stem_occupation'] == 'STEM OCCUPATIONS']['count'].sum() / df['count'].sum() * 100), 1),
    'snapshot': 'November 2025'
}

# Convert to JSON-friendly format
def df_to_json(dataframe):
    return dataframe.to_dict('records')

data = {
    'overall': overall,
    'agencies': df_to_json(agency_data.head(50)),  # Top 50 for performance
    'allAgencies': df_to_json(agency_data),
    'states': df_to_json(state_data),
    'payDistribution': df_to_json(pay_dist),
    'education': df_to_json(edu_data),
    'appointments': df_to_json(appt_data),
    'ageBrackets': df_to_json(age_data),
    'stem': df_to_json(stem_data),
    'supervisory': df_to_json(super_data)
}

# Save as JS file for embedding
print("Writing data file...")
with open(OUTPUT_PATH / 'data.js', 'w') as f:
    f.write('const DASHBOARD_DATA = ')
    json.dump(data, f)
    f.write(';')

print(f"\nData exported to {OUTPUT_PATH / 'data.js'}")
print(f"  Agencies: {len(data['allAgencies'])}")
print(f"  States: {len(data['states'])}")
print(f"  Total employees: {overall['total_employees']:,}")
