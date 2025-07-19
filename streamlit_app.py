import streamlit as st
import pandas as pd
import sqlite3

st.title("Nutrition Paradox: Global Obesity & Malnutrition Dashboard")

conn = sqlite3.connect('nutrition_paradox.db')

st.header("Obesity Data")
df_obesity = pd.read_sql("SELECT * FROM obesity LIMIT 100", conn)
st.dataframe(df_obesity)

st.header("Malnutrition Data")
df_malnutrition = pd.read_sql("SELECT * FROM malnutrition LIMIT 100", conn)
st.dataframe(df_malnutrition)

# Example: Top 5 regions with highest average obesity in 2022
st.subheader("Top 5 Regions by Obesity (2022)")
query = """
SELECT Region, AVG(Mean_Estimate) as avg_obesity
FROM obesity
WHERE Year = 2022
GROUP BY Region
ORDER BY avg_obesity DESC
LIMIT 5;
"""
st.dataframe(pd.read_sql(query, conn))

conn.close() 