import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

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

# Show shape and missing values
st.subheader("Obesity Data Overview")
st.write(f"Shape: {df_obesity.shape}")
st.write("Missing values:")
st.write(df_obesity.isnull().sum())

st.subheader("Malnutrition Data Overview")
st.write(f"Shape: {df_malnutrition.shape}")
st.write("Missing values:")
st.write(df_malnutrition.isnull().sum())

# Distribution of Mean_Estimate (Obesity)
st.subheader("Distribution of Obesity Mean Estimate")
fig, ax = plt.subplots()
sns.histplot(df_obesity['Mean_Estimate'], bins=30, kde=True, ax=ax)
st.pyplot(fig)

# Distribution of Mean_Estimate (Malnutrition)
st.subheader("Distribution of Malnutrition Mean Estimate")
fig, ax = plt.subplots()
sns.histplot(df_malnutrition['Mean_Estimate'], bins=30, kde=True, ax=ax)
st.pyplot(fig)

# Boxplot by Region (Obesity)
st.subheader("Obesity Mean Estimate by Region")
fig, ax = plt.subplots(figsize=(10, 5))
sns.boxplot(x='Region', y='Mean_Estimate', data=df_obesity, ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)

# Line plot: Obesity trend over years (global average)
st.subheader("Global Obesity Trend Over Years")
obesity_yearly = df_obesity.groupby('Year')['Mean_Estimate'].mean().reset_index()
fig, ax = plt.subplots()
sns.lineplot(x='Year', y='Mean_Estimate', data=obesity_yearly, marker='o', ax=ax)
st.pyplot(fig)

# Compare distributions: Obesity vs Malnutrition (side-by-side boxplots)
st.subheader("Obesity vs Malnutrition Mean Estimate Comparison")
fig, ax = plt.subplots()
sns.boxplot(data=[df_obesity['Mean_Estimate'].dropna(), df_malnutrition['Mean_Estimate'].dropna()])
ax.set_xticklabels(['Obesity', 'Malnutrition'])
st.pyplot(fig)

conn.close()