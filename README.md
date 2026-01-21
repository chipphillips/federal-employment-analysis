# Federal Employment Data Analysis

Analysis and visualization of November 2025 federal workforce data.

## Overview

This project provides tools to clean, analyze, and visualize federal employment data including:

- **780MB+ raw dataset** with 31 columns of workforce information
- **Jupyter notebook** for data exploration, cleaning, and analysis
- **Interactive HTML dashboard** for visualizing key metrics

## Data Columns Available

| Category | Columns |
|----------|---------|
| **Demographics** | age_bracket, education_level, length_of_service_years |
| **Organization** | agency, agency_subelement, duty_station_state |
| **Position** | occupational_series, grade, pay_plan, supervisory_status |
| **Compensation** | annualized_adjusted_basic_pay (some REDACTED) |
| **Employment** | appointment_type, work_schedule, stem_occupation |

## Project Structure

```
federal-employment-analysis/
├── data/
│   ├── raw/                    # Place raw CSV here (not tracked in git)
│   └── processed/              # Aggregated data files for dashboard
├── dashboard/
│   └── index.html              # Interactive visualization dashboard
├── notebooks/
│   └── 01_data_exploration_and_cleaning.ipynb
└── README.md
```

## Quick Start

### 1. Set Up Environment

```bash
# Install required Python packages
pip install pandas numpy matplotlib seaborn jupyter
```

### 2. Run the Notebook

1. Place the raw data file in `data/raw/` (or update the path in the notebook)
2. Open the notebook:
   ```bash
   jupyter notebook notebooks/01_data_exploration_and_cleaning.ipynb
   ```
3. Run all cells to:
   - Load and profile the data
   - Clean and transform values
   - Generate aggregated CSV files
   - Export data for the dashboard

### 3. View the Dashboard

After running the notebook, open `dashboard/index.html` in a browser.

The dashboard provides:
- **Overview**: Agency headcounts, pay distributions, STEM comparisons
- **Agencies**: Searchable table with all agency statistics
- **Geography**: State-by-state employment and pay analysis
- **Occupations**: Filter by STEM status, search job series
- **Compare**: Side-by-side agency comparison tool

## Analysis Features

The notebook includes functions for custom analysis:

```python
# Analyze any categorical column
analyze_by_column(df_clean, 'occupational_series', top_n=20)

# Compare two specific groups
compare_two_groups(df_clean, 'stem_occupation', 'STEM OCCUPATIONS', 'ALL OTHER OCCUPATIONS')

# Filter and summarize
filter_and_analyze(df_clean, agency='DEPARTMENT OF TREASURY', education_level="MASTER'S DEGREE")
```

## Key Insights Available

- Employee distribution across 100+ agencies
- Pay analysis by grade, education, tenure, location
- STEM vs non-STEM workforce comparisons
- Geographic distribution of federal employees
- Appointment type breakdown (career, political, etc.)
- Supervisory ratio analysis

## Data Notes

- **REDACTED values**: Some salary/location data is redacted for privacy
- **Pipe-delimited**: Raw file uses `|` as separator
- **Snapshot date**: November 2025 (202511)

## GitHub Pages (Optional)

To host the dashboard publicly:

1. Push to GitHub
2. Go to Settings > Pages
3. Set source to `main` branch, `/dashboard` folder
4. Access at `https://[username].github.io/federal-employment-analysis/`

## Requirements

- Python 3.8+
- pandas
- numpy
- matplotlib
- seaborn
- jupyter

## License

Data is from public federal sources. Analysis code is MIT licensed.
