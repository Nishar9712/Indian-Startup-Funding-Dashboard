# Indian Startup Funding Analysis Dashboard


[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas)](https://pandas.pydata.org/)

An interactive Streamlit dashboard for analyzing Indian startup funding data. The application provides overall market analysis, startup-level funding details, and investor-level insights using Pandas, Matplotlib, and Seaborn.


## 🚀 Live Demo

**Try the dashboard online:**  
👉 [Indian Startup Funding Analysis · Streamlit](https://aguvuqysttsxeaaghbknfq.streamlit.app/)

> The dashboard is deployed with Streamlit and can be opened directly in a browser without installing the project locally.


## 📊 Project Overview

This project is an interactive analytics dashboard for exploring Indian startup funding data. It combines data processing and visualization to help users understand funding trends, sectors, cities, investment stages, startups, and investors.

## Features

### Overall Analysis
- Total funding, maximum funding, average funding, and number of funded startups.
- Month-on-month funding amount or deal-count trends.
- Sector distribution by funding amount or deal count.
- Top 10 cities by total funding.
- Funding-stage distribution.
- Yearly funding heatmap by month.
- Top 15 funded startups with optional year filtering.
- Top 10 active investors by number of deals.

### Startup Analysis
Select a startup to view:
- Total amount raised.
- Number of funding rounds.
- Industry and city.
- Funding-round history.
- Funding progression over time.
- Investment-type breakdown.
- Similar companies in the same industry.

### Investor Analysis
Select an investor to view:
- Total capital invested.
- Number of startups backed.
- Total number of deals.
- Recent investments.
- Sector, investment-stage, and city distributions.
- Biggest investments by startup.
- Year-over-year investment activity.
- Similar investors based on shared sectors/deals.

## Tech Stack

- **Python**
- **Streamlit** — interactive dashboard interface
- **Pandas** — data loading, cleaning, transformation, and aggregation
- **Matplotlib** — chart rendering
- **Seaborn** — visualization styling and statistical charts

## Project Structure

```text
.
├── app.py
├── Cleaned Startup funding.csv
└── README.md
```

> Rename the Python source file to `app.py` (or update the run command below) if your current filename is different.

## Dataset Requirements

The application expects a CSV file named:

```text
Cleaned Startup funding.csv
```

The dataset is expected to contain the following columns:

- `Date`
- `Investment Amount($)`
- `Startup`
- `Industry`
- `Sub Vertical`
- `City`
- `Investors`
- `Investment Type`

The application converts `Date` to a datetime value and derives `year`, `month`, and `month_name`. It also creates shorter internal column names for analysis.

## Installation

### 1. Clone or download the project

Place the Python application and CSV dataset in the same directory.

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**macOS/Linux**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install streamlit pandas matplotlib seaborn
```

## Running the Dashboard

From the project directory, run:

```bash
streamlit run app.py
```

Streamlit will start a local web server and provide a URL that can be opened in a browser.

## Dashboard Navigation

The sidebar provides three main views:

1. **Overall Analysis** — high-level trends and rankings across the dataset.
2. **StartUp** — detailed analysis for an individual startup.
3. **Investor** — detailed analysis for an individual investor.

Startup and investor names are populated dynamically from the loaded dataset.

## Data Processing

When the application starts, the CSV is loaded through a cached `load_data()` function. The following processing is performed:

1. The funding CSV is read with Pandas.
2. `Date` is converted to datetime, with invalid values coerced to missing values.
3. Year, month number, and abbreviated month name are extracted.
4. Dataset columns are mapped to simpler internal names such as `amount`, `startup`, `industry`, and `investors`.
5. Investor names are split on commas for investor-level counts and selection.
6. Undisclosed investor entries are excluded from investor lists.
7. Charts and summary tables are generated from grouped and aggregated data.

## Currency Formatting

Funding values are displayed using compact units:

- Billions as `$B`
- Millions as `$M`
- Thousands as `$K`
- Smaller values as full dollar amounts

For example, a large funding amount may be displayed as `$1.25B` rather than its full numeric value.

## Notes

- The dashboard reads the CSV using a relative path, so the CSV should be available in the application's working directory.
- The analysis is entirely driven by the contents of the supplied dataset.
- Investor entries containing multiple names are split by commas.
- Charts use Seaborn/Matplotlib and are rendered directly in Streamlit.
- Streamlit data caching is used for the main dataset-loading function.

## Troubleshooting

### CSV file not found

Make sure the file is named exactly:

```text
Cleaned Startup funding.csv
```

and is located in the same directory from which the Streamlit application is run.

### Missing Python package

Install all required packages with:

```bash
pip install streamlit pandas matplotlib seaborn
```

### Empty or unexpected charts

Check that the CSV contains the required columns and valid funding/date values.

## 📌 Application Source

This README documents the provided Indian Startup Funding Analysis Streamlit application and its implemented functionality. The application configures the page title as **Indian Startup Funding Analysis** and uses a wide Streamlit layout. fileciteturn0file0L6-L10
