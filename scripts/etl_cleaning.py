import os
import pandas as pd
import requests
import pycountry
import sqlite3

# Ensure data directory exists
os.makedirs('../data', exist_ok=True)

# API URLs
datasets = {
    "adult_obesity": ("https://ghoapi.azureedge.net/api/NCD_BMI_30C", "Adult"),
    "child_obesity": ("https://ghoapi.azureedge.net/api/NCD_BMI_PLUS2C", "Child/Adolescent"),
    "adult_malnutrition": ("https://ghoapi.azureedge.net/api/NCD_BMI_18C", "Adult"),
    "child_malnutrition": ("https://ghoapi.azureedge.net/api/NCD_BMI_MINUS2C", "Child/Adolescent")
}

def fetch_data(url, age_group):
    response = requests.get(url)
    data = response.json()['value']
    df = pd.DataFrame(data)
    df['age_group'] = age_group
    return df

# Download and combine datasets
df_obesity = pd.concat([
    fetch_data(*datasets["adult_obesity"]),
    fetch_data(*datasets["child_obesity"])
], ignore_index=True)
df_malnutrition = pd.concat([
    fetch_data(*datasets["adult_malnutrition"]),
    fetch_data(*datasets["child_malnutrition"])
], ignore_index=True)

# Filter years
df_obesity = df_obesity[df_obesity['TimeDim'].between(2012, 2022)]
df_malnutrition = df_malnutrition[df_malnutrition['TimeDim'].between(2012, 2022)]

# Columns to keep and rename
columns_map = {
    'ParentLocation': 'Region',
    'Dim1': 'Gender',
    'TimeDim': 'Year',
    'Low': 'LowerBound',
    'High': 'UpperBound',
    'NumericValue': 'Mean_Estimate',
    'SpatialDim': 'Country',
    'age_group': 'Age_Group'
}

def clean_df(df, is_obesity=True):
    df = df[list(columns_map.keys())]
    df = df.rename(columns=columns_map)
    # Standardize Gender
    df['Gender'] = df['Gender'].replace({'BTSX': 'Both', 'MLE': 'Male', 'FMLE': 'Female', 'Both sexes': 'Both'})
    # Country code to name
    def code_to_country(code):
        try:
            return pycountry.countries.get(alpha_3=code).name
        except:
            return code
    df['Country'] = df['Country'].apply(code_to_country)
    # Special cases
    special_cases = {
        'GLOBAL': 'Global', 'WB_LMI': 'Low & Middle Income', 'WB_HI': 'High Income',
        'WB_LI': 'Low Income', 'EMR': 'Eastern Mediterranean Region', 'EUR': 'Europe',
        'AFR': 'Africa', 'SEAR': 'South-East Asia Region', 'WPR': 'Western Pacific Region',
        'AMR': 'Americas Region', 'WB_UMI': 'Upper Middle Income'
    }
    df['Country'] = df['Country'].replace(special_cases)
    # CI_Width
    df['CI_Width'] = df['UpperBound'] - df['LowerBound']
    # Obesity/Malnutrition level
    if is_obesity:
        df['Obesity_Level'] = pd.cut(df['Mean_Estimate'], bins=[-float('inf'), 25, 29.9, float('inf')], labels=['Low', 'Moderate', 'High'])
    else:
        df['Malnutrition_Level'] = pd.cut(df['Mean_Estimate'], bins=[-float('inf'), 10, 19.9, float('inf')], labels=['Low', 'Moderate', 'High'])
    return df

df_obesity_clean = clean_df(df_obesity, is_obesity=True)
df_malnutrition_clean = clean_df(df_malnutrition, is_obesity=False)

# Save cleaned data (optional)
df_obesity_clean.to_csv('../data/obesity_clean.csv', index=False)
df_malnutrition_clean.to_csv('../data/malnutrition_clean.csv', index=False)

# Insert into SQLite
conn = sqlite3.connect('../nutrition_paradox.db')
df_obesity_clean.to_sql('obesity', conn, if_exists='replace', index=False)
df_malnutrition_clean.to_sql('malnutrition', conn, if_exists='replace', index=False)
conn.close()

print('ETL and cleaning complete. Data saved to data/ and nutrition_paradox.db.') 