# Data Breach Intelligence Dashboard

**Analysis and Visualization of Publicly Reported Cybersecurity Breaches**

An MSc Artificial Intelligence & Cybersecurity mini project that transforms a raw,
publicly-reported data breach dataset into an interactive cybersecurity intelligence
dashboard using Python, Pandas, Plotly, and Streamlit.

---

## Project Objective

Organizations and cybersecurity professionals need to understand patterns in publicly
reported data breaches: which organizations experienced the largest breaches, what
categories of data were compromised, how breach activity has trended over time, and
how breaches differ across verification, sensitivity, and malware status. Raw breach
data is difficult to interpret directly — this project cleans, analyzes, and visualizes
that data through a professional, filterable, multi-page dashboard.

## Dataset Description

The dataset (`data/original_dataset.csv`) contains ~777 publicly reported breach
records with the following fields:

| Column | Description |
|---|---|
| `Name` | Unique name of the breached organization/service |
| `Title` | Display title of the breach |
| `Domain` | Website domain of the organization |
| `BreachDate` | Date the breach occurred |
| `AddedDate` | Date the breach was added to the source database |
| `ModifiedDate` | Date the breach record was last modified |
| `PwnCount` | Number of compromised/exposed records |
| `Description` | Narrative description of the breach |
| `LogoPath` | URL to the organization's logo |
| `DataClasses` | Categories of data exposed (e.g. emails, passwords) |
| `IsVerified` | Whether the breach has been verified |
| `IsFabricated` | Whether the breach is believed fabricated |
| `IsSensitive` | Whether the breach contains sensitive information |
| `IsRetired` | Whether the breach record has been retired |
| `IsSpamList` | Whether the breach is associated with a spam list |
| `IsMalware` | Whether the breach is associated with malware |
| `IsSubscriptionFree` | Whether the breach is freely accessible |

## Features

- **Automated cleaning pipeline**: date parsing, boolean normalization, `DataClasses`
  list parsing, duplicate removal, and derived feature engineering
  (`BreachYear`, `BreachMonth`, `BreachYearMonth`, `LogPwnCount`, `NumberOfDataClasses`)
- **20+ dynamically computed EDA answers** — nothing is hardcoded; every number recalculates
  when filters change
- **25+ Plotly visualizations**: KPI cards, time-series, bar charts, donut charts,
  histograms, box plots, multivariate scatter/bubble charts, and heatmaps
- **6-page interactive Streamlit dashboard** with a dark cybersecurity theme
- **Sidebar filtering** by year range, domain, verification/sensitivity/malware/spam status
- **Searchable Breach Explorer** with CSV export of filtered results
- **Dynamically generated insights** — no hardcoded conclusions

## Installation

1. Extract this project folder and open it in VS Code (or any IDE).
2. (Recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

From the project root directory:

```bash
streamlit run app.py
```

Streamlit will open the dashboard in your default browser (typically at
`http://localhost:8501`).

## Dashboard Pages

1. **Executive Overview** — KPI cards, breach trend, top breaches, key insights
2. **Breach Trend Analysis** — breaches/records by year, trend line, year×month heatmap
3. **Data Exposure Analysis** — most exposed data categories, breaches with most data
   categories exposed
4. **Cybersecurity Risk Analysis** — verified/sensitive/malware/spam donut charts,
   distribution & outlier analysis, correlation heatmap
5. **Breach Explorer** — searchable, filterable, exportable breach table
6. **Insights & Conclusion** — dynamically generated findings, limitations, and
   recommendations

## Technologies Used

- **Python 3.9+**
- **Streamlit** — interactive dashboard framework
- **Pandas / NumPy** — data cleaning and analysis
- **Plotly** — interactive charting

## Project Structure

```
data_breach_intelligence_dashboard/
│
├── app.py                     # Main Streamlit entry point
├── requirements.txt
├── README.md
│
├── data/
│   ├── original_dataset.csv   # Provided raw dataset
│   └── cleaned_breaches.csv   # Generated on first run
│
├── src/
│   ├── __init__.py
│   ├── data_preprocessing.py  # Cleaning + feature engineering
│   ├── analysis.py            # EDA / metric calculations
│   └── visualizations.py      # Plotly chart builders
│
└── assets/                    # Optional static assets
```

## Notes

- `data/cleaned_breaches.csv` is generated automatically the first time you run the
  app, so it does not need to be committed manually.
- All analytical results are calculated dynamically from the dataset at runtime — no
  metric or conclusion in the dashboard is hardcoded.
