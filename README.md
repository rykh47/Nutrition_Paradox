# Nutrition Paradox: A Global View on Obesity and Malnutrition

## Overview
Analyze global trends in obesity and malnutrition using WHO data. Clean, explore, and visualize the data, and provide actionable insights for public health.

## Project Structure
```
nutrition_paradox/
│
├── data/                        # For optional CSV exports
├── notebooks/
│   └── eda_and_queries.ipynb    # Jupyter notebook for EDA & SQL queries
├── scripts/
│   └── etl_cleaning.py          # Data collection & cleaning script
├── nutrition_paradox.db         # SQLite database (auto-created)
├── requirements.txt             # Python dependencies
├── README.md                    # Project overview
└── streamlit_app.py             # (Optional) Streamlit dashboard
```

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run ETL: `python scripts/etl_cleaning.py`
3. Explore EDA and queries in `notebooks/eda_and_queries.ipynb`
4. (Optional) Launch dashboard: `streamlit run streamlit_app.py` 