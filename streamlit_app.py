import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Nutrition Paradox Dashboard", layout="wide")

st.title("🥗 Nutrition Paradox: Global Obesity & Malnutrition Dashboard")

conn = sqlite3.connect('nutrition_paradox.db')

# Load data
df_obesity = pd.read_sql("SELECT * FROM obesity", conn)
df_malnutrition = pd.read_sql("SELECT * FROM malnutrition", conn)

# Tabs for navigation
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Data Overview",
    "🧋 Obesity Analysis",
    "👾 Malnutrition Analysis",
    "🔗 Combined Insights"
])

with tab1:
    st.header("Data Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Obesity Data Sample")
        st.dataframe(df_obesity.head(100))
        st.write(f"Shape: {df_obesity.shape}")
        st.write("Missing values:")
        st.write(df_obesity.isnull().sum())
    with col2:
        st.subheader("Malnutrition Data Sample")
        st.dataframe(df_malnutrition.head(100))
        st.write(f"Shape: {df_malnutrition.shape}")
        st.write("Missing values:")
        st.write(df_malnutrition.isnull().sum())

    st.markdown("---")
    st.subheader("Distribution of Mean Estimates")
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        sns.histplot(df_obesity['Mean_Estimate'], bins=30, kde=True, ax=ax)
        ax.set_title("Obesity Mean Estimate")
        st.pyplot(fig)
    with col2:
        fig, ax = plt.subplots()
        sns.histplot(df_malnutrition['Mean_Estimate'], bins=30, kde=True, ax=ax)
        ax.set_title("Malnutrition Mean Estimate")
        st.pyplot(fig)

    st.subheader("Obesity vs Malnutrition Mean Estimate Comparison")
    fig, ax = plt.subplots()
    sns.boxplot(data=[df_obesity['Mean_Estimate'].dropna(), df_malnutrition['Mean_Estimate'].dropna()])
    ax.set_xticklabels(['Obesity', 'Malnutrition'])
    st.pyplot(fig)

with tab2:
    st.header("🧋 Obesity Analysis")
    st.markdown("#### Key Trends & Queries")
    # Visualizations
    st.subheader("Obesity Mean Estimate by Region")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(x='Region', y='Mean_Estimate', data=df_obesity, ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.subheader("Global Obesity Trend Over Years")
    obesity_yearly = df_obesity.groupby('Year')['Mean_Estimate'].mean().reset_index()
    fig, ax = plt.subplots()
    sns.lineplot(x='Year', y='Mean_Estimate', data=obesity_yearly, marker='o', ax=ax)
    st.pyplot(fig)

    # Queries in expanders
    with st.expander("Top 5 Regions with Highest Average Obesity (2022)"):
        query = """
        SELECT Region, AVG(Mean_Estimate) as avg_obesity
        FROM obesity
        WHERE Year = 2022
        GROUP BY Region
        ORDER BY avg_obesity DESC
        LIMIT 5;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Top 5 Countries with Highest Obesity Estimates (2022)"):
        query = """
        SELECT Country, AVG(Mean_Estimate) as avg_obesity
        FROM obesity
        WHERE Year = 2022
        GROUP BY Country
        ORDER BY avg_obesity DESC
        LIMIT 5;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Obesity Trend in India Over the Years"):
        query = """
        SELECT Year, AVG(Mean_Estimate) as avg_obesity
        FROM obesity
        WHERE Country = 'India'
        GROUP BY Year
        ORDER BY Year;
        """
        df_india = pd.read_sql(query, conn)
        st.dataframe(df_india)
        fig, ax = plt.subplots()
        sns.lineplot(x='Year', y='avg_obesity', data=df_india, marker='o', ax=ax)
        st.pyplot(fig)

    with st.expander("Average Obesity by Gender"):
        query = """
        SELECT Gender, AVG(Mean_Estimate) as avg_obesity
        FROM obesity
        GROUP BY Gender
        ORDER BY avg_obesity DESC;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Country Count by Obesity Level Category and Age Group"):
        query = """
        SELECT Obesity_Level, Age_Group, COUNT(DISTINCT Country) as country_count
        FROM obesity
        GROUP BY Obesity_Level, Age_Group
        ORDER BY country_count DESC;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Top 5 Least Reliable Countries (Highest Avg CI_Width)"):
        query = """
        SELECT Country, AVG(CI_Width) as avg_ci_width
        FROM obesity
        GROUP BY Country
        ORDER BY avg_ci_width DESC
        LIMIT 5;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Top 5 Most Consistent Countries (Lowest Avg CI_Width)"):
        query = """
        SELECT Country, AVG(CI_Width) as avg_ci_width
        FROM obesity
        GROUP BY Country
        ORDER BY avg_ci_width ASC
        LIMIT 5;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Average Obesity by Age Group"):
        query = """
        SELECT Age_Group, AVG(Mean_Estimate) as avg_obesity
        FROM obesity
        GROUP BY Age_Group
        ORDER BY avg_obesity DESC;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Top 10 Countries with Consistent Low Obesity"):
        query = """
        SELECT Country, AVG(Mean_Estimate) as avg_obesity, AVG(CI_Width) as avg_ci
        FROM obesity
        GROUP BY Country
        HAVING avg_obesity < 25 AND avg_ci < 2
        ORDER BY avg_obesity ASC, avg_ci ASC
        LIMIT 10;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Countries Where Female Obesity Exceeds Male by Large Margin (2022)"):
        query = """
        SELECT o1.Country, (o1.avg_female - o2.avg_male) as diff
        FROM (
            SELECT Country, AVG(Mean_Estimate) as avg_female
            FROM obesity
            WHERE Gender = 'Female' AND Year = 2022
            GROUP BY Country
        ) o1
        JOIN (
            SELECT Country, AVG(Mean_Estimate) as avg_male
            FROM obesity
            WHERE Gender = 'Male' AND Year = 2022
            GROUP BY Country
        ) o2
        ON o1.Country = o2.Country
        WHERE (o1.avg_female - o2.avg_male) > 5
        ORDER BY diff DESC;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Global Average Obesity Percentage Per Year"):
        query = """
        SELECT Year, AVG(Mean_Estimate) as global_avg_obesity
        FROM obesity
        GROUP BY Year
        ORDER BY Year;
        """
        st.dataframe(pd.read_sql(query, conn))

with tab3:
    st.header("👾 Malnutrition Analysis")
    st.markdown("#### Key Trends & Queries")
    # Visualizations
    st.subheader("Malnutrition Mean Estimate by Region")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(x='Region', y='Mean_Estimate', data=df_malnutrition, ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.subheader("Global Malnutrition Trend Over Years")
    mal_yearly = df_malnutrition.groupby('Year')['Mean_Estimate'].mean().reset_index()
    fig, ax = plt.subplots()
    sns.lineplot(x='Year', y='Mean_Estimate', data=mal_yearly, marker='o', ax=ax)
    st.pyplot(fig)

    # Queries in expanders
    with st.expander("Average Malnutrition by Age Group"):
        query = """
        SELECT Age_Group, AVG(Mean_Estimate) as avg_malnutrition
        FROM malnutrition
        GROUP BY Age_Group
        ORDER BY avg_malnutrition DESC;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Top 5 Countries with Highest Malnutrition (2022)"):
        query = """
        SELECT Country, AVG(Mean_Estimate) as avg_malnutrition
        FROM malnutrition
        WHERE Year = 2022
        GROUP BY Country
        ORDER BY avg_malnutrition DESC
        LIMIT 5;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Malnutrition Trend in African Region Over the Years"):
        query = """
        SELECT Year, AVG(Mean_Estimate) as avg_malnutrition
        FROM malnutrition
        WHERE Region = 'Africa'
        GROUP BY Year
        ORDER BY Year;
        """
        df_africa = pd.read_sql(query, conn)
        st.dataframe(df_africa)
        fig, ax = plt.subplots()
        sns.lineplot(x='Year', y='avg_malnutrition', data=df_africa, marker='o', ax=ax)
        st.pyplot(fig)

    with st.expander("Gender-based Average Malnutrition"):
        query = """
        SELECT Gender, AVG(Mean_Estimate) as avg_malnutrition
        FROM malnutrition
        GROUP BY Gender
        ORDER BY avg_malnutrition DESC;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Malnutrition Level-wise Average CI_Width by Age Group"):
        query = """
        SELECT Malnutrition_Level, Age_Group, AVG(CI_Width) as avg_ci_width
        FROM malnutrition
        GROUP BY Malnutrition_Level, Age_Group
        ORDER BY avg_ci_width DESC;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Yearly Malnutrition Change in India, Nigeria, Brazil"):
        query = """
        SELECT Country, Year, AVG(Mean_Estimate) as avg_malnutrition
        FROM malnutrition
        WHERE Country IN ('India', 'Nigeria', 'Brazil')
        GROUP BY Country, Year
        ORDER BY Country, Year;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Regions with Lowest Malnutrition Averages (2022)"):
        query = """
        SELECT Region, AVG(Mean_Estimate) as avg_malnutrition
        FROM malnutrition
        WHERE Year = 2022
        GROUP BY Region
        ORDER BY avg_malnutrition ASC
        LIMIT 5;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Countries with Increasing Malnutrition"):
        query = """
        SELECT Country, MIN(Mean_Estimate) as min_malnutrition, MAX(Mean_Estimate) as max_malnutrition
        FROM malnutrition
        GROUP BY Country
        HAVING (MAX(Mean_Estimate) - MIN(Mean_Estimate)) > 0;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Year-wise Min/Max Malnutrition Levels"):
        query = """
        SELECT Year, MIN(Mean_Estimate) as min_malnutrition, MAX(Mean_Estimate) as max_malnutrition
        FROM malnutrition
        GROUP BY Year
        ORDER BY Year;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("High CI_Width Flags for Monitoring (CI_Width > 5)"):
        query = """
        SELECT *
        FROM malnutrition
        WHERE CI_Width > 5
        ORDER BY CI_Width DESC
        LIMIT 20;
        """
        st.dataframe(pd.read_sql(query, conn))

with tab4:
    st.header("🔗 Combined Insights")
    st.markdown("#### Comparative & Correlative Queries")

    with st.expander("Obesity vs Malnutrition Comparison by Country"):
        countries = ['India', 'Nigeria', 'Brazil', 'United States', 'China']
        query = f"""
        SELECT o.Country, AVG(o.Mean_Estimate) as avg_obesity, AVG(m.Mean_Estimate) as avg_malnutrition
        FROM obesity o
        JOIN malnutrition m ON o.Country = m.Country
        WHERE o.Country IN ({','.join(["'" + c + "'" for c in countries])})
        GROUP BY o.Country
        ORDER BY o.Country;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Gender-based Disparity in Obesity and Malnutrition"):
        query = """
        SELECT o.Gender, AVG(o.Mean_Estimate) as avg_obesity, AVG(m.Mean_Estimate) as avg_malnutrition
        FROM obesity o
        JOIN malnutrition m ON o.Gender = m.Gender AND o.Country = m.Country AND o.Year = m.Year
        GROUP BY o.Gender
        ORDER BY o.Gender;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Region-wise Average Estimates: Africa vs Americas"):
        query = """
        SELECT o.Region, AVG(o.Mean_Estimate) as avg_obesity, AVG(m.Mean_Estimate) as avg_malnutrition
        FROM obesity o
        JOIN malnutrition m ON o.Region = m.Region AND o.Country = m.Country AND o.Year = m.Year
        WHERE o.Region IN ('Africa', 'Americas Region')
        GROUP BY o.Region
        ORDER BY o.Region;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Countries with Obesity Up & Malnutrition Down"):
        query = """
        SELECT o.Country,
            (MAX(o.Mean_Estimate) - MIN(o.Mean_Estimate)) as obesity_change,
            (MIN(m.Mean_Estimate) - MAX(m.Mean_Estimate)) as malnutrition_change
        FROM obesity o
        JOIN malnutrition m ON o.Country = m.Country
        GROUP BY o.Country
        HAVING obesity_change > 0 AND malnutrition_change > 0
        ORDER BY obesity_change DESC;
        """
        st.dataframe(pd.read_sql(query, conn))

    with st.expander("Age-wise Trend Analysis (Obesity & Malnutrition)"):
        query = """
        SELECT o.Year, o.Age_Group, AVG(o.Mean_Estimate) as avg_obesity, AVG(m.Mean_Estimate) as avg_malnutrition
        FROM obesity o
        JOIN malnutrition m ON o.Country = m.Country AND o.Year = m.Year AND o.Age_Group = m.Age_Group
        GROUP BY o.Year, o.Age_Group
        ORDER BY o.Year, o.Age_Group;
        """
        st.dataframe(pd.read_sql(query, conn))

conn.close()