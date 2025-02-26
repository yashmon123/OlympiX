import numpy as np
import pandas as pd


import numpy as np
import pandas as pd

def fetch_medal_tally(df, year, country):
    # Ensure 'Medal' column is not empty
    medal_df = df.dropna(subset=['Medal'])
    medal_df = medal_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
    elif year == 'Overall' and country != 'Overall':
        temp_df = medal_df[medal_df['region'] == country]
    elif year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    else:
        temp_df = medal_df[(medal_df['Year'] == int(year)) & (medal_df['region'] == country)]

    # Ensure 'Gold', 'Silver', 'Bronze' columns exist
    temp_df['Gold'] = temp_df['Medal'].apply(lambda x: 1 if x == 'Gold' else 0)
    temp_df['Silver'] = temp_df['Medal'].apply(lambda x: 1 if x == 'Silver' else 0)
    temp_df['Bronze'] = temp_df['Medal'].apply(lambda x: 1 if x == 'Bronze' else 0)

    # Group data properly
    if country == 'Overall':
        x = temp_df.groupby('region')[['Gold', 'Silver', 'Bronze']].sum().sort_values('Gold', ascending=False).reset_index()
    else:
        x = temp_df.groupby('Year')[['Gold', 'Silver', 'Bronze']].sum().reset_index()

    # Add total medals column
    x['Total'] = x['Gold'] + x['Silver'] + x['Bronze']

    # Convert to integers
    x[['Gold', 'Silver', 'Bronze', 'Total']] = x[['Gold', 'Silver', 'Bronze', 'Total']].astype(int)

    return x



def country_year_list(df):
    years = sorted(df['Year'].unique().tolist())
    years.insert(0, 'Overall')

    country = sorted(df['region'].dropna().unique().tolist())
    country.insert(0, 'Overall')

    return years, country

def yearwise_medal_tally(df, country):
    temp_df = df.dropna(subset=['Medal']).drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
    )
    new_df = temp_df[temp_df['region'] == country]
    return new_df.groupby('Year').count()['Medal'].reset_index()

def country_event_heatmap(df, country):
    temp_df = df.dropna(subset=['Medal']).drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
    )
    new_df = temp_df[temp_df['region'] == country]
    return new_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)

def get_athlete_data(df, athlete_name):
    return df[df["Name"] == athlete_name]


def top_10_athletes(df, country):
    # Filter only medal winners
    temp_df = df.dropna(subset=['Medal'])

    # Filter for selected country
    country_df = temp_df[temp_df['region'] == country]

    # Exclude duplicate teams (ensuring only unique athletes count)
    country_df = country_df.drop_duplicates(subset=['Name', 'Sport', 'Event'])

    # Count total medals per athlete
    top_athletes = country_df['Name'].value_counts().reset_index()
    top_athletes.columns = ['Athlete', 'Total Medals']

    # Get the top 10 athletes
    return top_athletes.head(10)