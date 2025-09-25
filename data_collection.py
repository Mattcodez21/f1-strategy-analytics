"""
F1 Data Collection Script

This script collects F1 data using the FastF1 library.
First time working with F1 data APIs - took a while to understand how it all fits together.

The goal is to get qualifying and race data that I can analyze in my dashboard.
"""

import fastf1
import pandas as pd
import numpy as np
import warnings
import os

# turn off warnings - they were getting annoying during development
warnings.filterwarnings('ignore')

# set up caching so I don't have to re-download data every time
cache_dir = os.path.join('..', 'data', 'cache')
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

def test_fastf1_connection():
    """Quick test to make sure FastF1 is working properly"""
    try:
        print("Testing FastF1 connection...")
        # try to load a recent race to test the connection
        race = fastf1.get_session(2024, 'Bahrain', 'R')
        print(f"Successfully connected! Found race: {race.event['EventName']}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
    
def collect_race_data(year, race_name):
    """Get race and qualifying data for a specific race"""
    try:
        print(f"Collecting data for {year} {race_name}...")
        
        # load the race session first
        print(f"   Loading race session...")
        race = fastf1.get_session(year, race_name, 'R')
        race.load()  # this actually downloads the data
        
        # then get qualifying data
        print(f"   Loading qualifying session...")
        quali = fastf1.get_session(year, race_name, 'Q')
        quali.load()  
        
        # extract the results we need
        race_results = race.results
        quali_results = quali.results
        
        print(f"Successfully loaded {race.event['EventName']}")
        print(f"   Race entries: {len(race_results)}")
        print(f"   Qualifying entries: {len(quali_results)}")
        
        # return everything in a dictionary
        return {
            'race_results': race_results,
            'quali_results': quali_results,
            'race_info': {
                'year': year,
                'race': race_name,
                'event_name': race.event['EventName'],
                'date': race.date
            }
        }
    except Exception as e:
        print(f"Error collecting data for {year} {race_name}: {e}")
        return None
    
def create_combined_dataframe(race_data):
    """Combine qualifying and race data into one dataframe for analysis"""
    if not race_data:
        return None
        
    # get qualifying data and use best available time
    quali_results = race_data['quali_results']
    quali_df = quali_results[['Position', 'Abbreviation', 'TeamName']].copy()
    
    # use Q3 time if available, otherwise Q2, otherwise Q1
    # this gives us the best qualifying time for each driver
    quali_df['quali_time'] = quali_results['Q3'].fillna(
        quali_results['Q2'].fillna(quali_results['Q1']))

    race_df = race_data['race_results'][['Position', 'Abbreviation', 'Points', 'Status']].copy()
    
    # debug prints to see what we're working with
    print(f"Qualifying drivers: {len(quali_df)}")
    print(f"Race drivers: {len(race_df)}")
    
    # merge the dataframes - using outer join to keep all drivers
    # this was tricky to get right - originally used inner join and lost drivers
    combined = pd.merge(quali_df, race_df, on='Abbreviation', how='outer')
    print(f"After merge: {len(combined)} drivers")
    
    # clean up column names 
    combined.columns = ['quali_position', 'driver', 'team', 'quali_time', 'race_position', 'points', 'status']
    
    # calculate position changes (positive = lost positions, negative = gained)
    combined['position_change'] = combined['race_position'] - combined['quali_position']
    
    # add race information
    combined['year'] = race_data['race_info']['year']
    combined['race'] = race_data['race_info']['race']
    combined['event_name'] = race_data['race_info']['event_name']
    
    return combined

def analyze_qualifying_performance(df):
    """Basic analysis of qualifying vs race performance"""
    # remove drivers who didn't finish or had missing data
    clean_df = df.dropna(subset=['quali_position', 'race_position'])
    
    if len(clean_df) == 0:
        return None, None
    
    # calculate correlation between qualifying and race positions
    correlation = clean_df['quali_position'].corr(clean_df['race_position'])
    
    # basic statistics
    stats = {
        'correlation': correlation,
        'r_squared': correlation**2,
        'sample_size': len(clean_df),
        'mean_position_change': clean_df['position_change'].mean(),
        'std_position_change': clean_df['position_change'].std()
    }
    
    return stats, clean_df
    
# main execution
if __name__ == "__main__":
    # test connection first
    if test_fastf1_connection():
        # races I want to analyze - started with just a few to test
        races = ['Bahrain', 'Saudi Arabia', 'Australia', 'Japan', 'China']
        
        all_race_data = []
        
        # collect data for each race
        for race in races:
            race_data = collect_race_data(2024, race)
            if race_data:
                combined_df = create_combined_dataframe(race_data)
                if combined_df is not None:
                    all_race_data.append(combined_df)
        
        # combine all races into one big dataset
        if all_race_data:
            final_dataset = pd.concat(all_race_data, ignore_index=True)
            
            # save to CSV for use in dashboard
            final_dataset.to_csv('data/processed/day2_analysis_data.csv', index=False)
            print(f"Saved {len(final_dataset)} records to day2_analysis_data.csv")
            
            # quick summary of what we collected
            print(f"\nData collection summary:")
            print(f"- Total races: {len(all_race_data)}")
            print(f"- Total driver records: {len(final_dataset)}")
            print(f"- Teams found: {final_dataset['team'].nunique()}")
        else:
            print("No data was collected - check for errors above")
    else:
        print("FastF1 connection test failed - check your internet connection")