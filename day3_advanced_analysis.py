"""
Day 3: Advanced F1 Analysis

Expanding on yesterday's work - going to collect more races and do deeper analysis.
Want to look at team performance across different conditions and build a bigger dataset.
"""

from data_collection import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

print("F1 Strategic Analysis - Day 3")
print("=" * 40)

def collect_full_season_data():
    """Get data from multiple races to build a proper dataset"""
    # races I want to analyze with weather info I looked up
    races_2024 = [
        ('Bahrain', 'Dry'),
        ('Saudi Arabia', 'Dry'),
        ('Australia', 'Dry'),
        ('Japan', 'Wet'),
        ('China', 'Dry'),
        ('Miami', 'Dry'),
        ('Imola', 'Mixed'),
        ('Monaco', 'Dry'),
        ('Canada', 'Dry'),
        ('Spain', 'Dry')
    ]
    
    all_race_data = []
    
    for race_name, weather in races_2024:
        print(f"\nCollecting {race_name} ({weather} conditions)...")
        race_data = collect_race_data(2024, race_name)
        
        if race_data:
            df = create_combined_dataframe(race_data)
            if df is not None:
                df['weather_condition'] = weather  # add weather info manually
                all_race_data.append(df)
                print(f"   Added {len(df)} driver records")
            else:
                print(f"   Failed to process {race_name}")
        else:
            print(f"   Failed to collect {race_name}")
    
    if all_race_data:
        combined_df = pd.concat(all_race_data, ignore_index=True)
        print(f"\nTOTAL DATASET: {len(combined_df)} records from {len(all_race_data)} races")
        return combined_df
    else:
        print("No data collected")
        return None

def analyze_qualifying_performance(df):
    """Look at qualifying performance across all races"""
    print("\nQUALIFYING PERFORMANCE ANALYSIS")
    print("=" * 35)
    
    # basic stats
    total_drivers = len(df)
    total_teams = df['team'].nunique()
    
    print(f"Total driver performances: {total_drivers}")
    print(f"Teams analyzed: {total_teams}")
    
    # team performance summary
    print(f"\nTeam qualifying averages:")
    team_performance = df.groupby('team')['quali_position'].mean().sort_values()
    for i, (team, avg_pos) in enumerate(team_performance.head(5).items()):
        print(f"  {i+1}. {team}: {avg_pos:.1f}")
    
    # look at qualifying time spreads
    if 'quali_time' in df.columns:
        print(f"\nQualifying time analysis:")
        # this is tricky because times are in different formats
        print(f"  Fastest time: {df['quali_time'].min()}")
        print(f"  Slowest time: {df['quali_time'].max()}")
    
    return df

def weather_impact_analysis(df):
    """See how weather affects performance"""
    print(f"\nWEATHER IMPACT ANALYSIS")
    print("=" * 25)
    
    weather_stats = {}
    
    for condition in df['weather_condition'].unique():
        condition_df = df[df['weather_condition'] == condition]
        
        # basic stats for each weather condition
        avg_quali_pos = condition_df['quali_position'].mean()
        std_quali_pos = condition_df['quali_position'].std()
        
        weather_stats[condition] = {
            'avg_position': avg_quali_pos,
            'std_position': std_quali_pos,
            'races': len(condition_df)
        }
        
        print(f"\n{condition.upper()} CONDITIONS:")
        print(f"  Average qualifying position: {avg_quali_pos:.2f}")
        print(f"  Position spread (std): {std_quali_pos:.2f}")
        print(f"  Driver performances: {len(condition_df)}")
    
    return weather_stats

def team_performance_deep_dive(df):
    """Detailed look at how teams perform in different conditions"""
    print(f"\nTEAM PERFORMANCE BY CONDITIONS")
    print("=" * 32)
    
    # performance by weather for top teams
    top_teams = df.groupby('team')['quali_position'].mean().sort_values().head(3).index
    
    for team in top_teams:
        print(f"\n{team}:")
        team_data = df[df['team'] == team]
        
        for condition in team_data['weather_condition'].unique():
            condition_data = team_data[team_data['weather_condition'] == condition]
            if len(condition_data) > 0:
                avg_pos = condition_data['quali_position'].mean()
                races = len(condition_data)
                print(f"  {condition}: {avg_pos:.1f} avg position ({races} races)")
    
    return True

def create_summary_stats(df):
    """Generate some basic statistics for the dataset"""
    print(f"\nDATASET SUMMARY STATISTICS")
    print("=" * 28)
    
    stats_summary = {
        'total_records': len(df),
        'unique_teams': df['team'].nunique(),
        'unique_drivers': df['driver'].nunique(),
        'races_analyzed': df['event_name'].nunique(),
        'weather_conditions': df['weather_condition'].nunique()
    }
    
    for key, value in stats_summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    return stats_summary

def save_day3_results(df, stats, weather_analysis):
    """Save all the analysis results"""
    
    # save the big dataset
    df.to_csv('data/processed/day3_full_analysis.csv', index=False)
    print(f"\nSaved full dataset to: data/processed/day3_full_analysis.csv")
    
    # save a summary report
    with open('data/processed/day3_statistical_report.txt', 'w') as f:
        f.write("F1 Analysis - Day 3 Report\n")
        f.write("=" * 30 + "\n\n")
        
        f.write("Dataset Summary:\n")
        for key, value in stats.items():
            f.write(f"{key.replace('_', ' ').title()}: {value}\n")
        
        f.write(f"\nWeather Analysis:\n")
        for condition, data in weather_analysis.items():
            f.write(f"{condition}: {data['avg_position']:.2f} avg position, ")
            f.write(f"{data['races']} performances\n")
    
    print(f"Saved analysis report to: data/processed/day3_statistical_report.txt")

def main():
    """Main analysis pipeline for day 3"""
    
    # collect data from multiple races
    print("Collecting full season data...")
    df = collect_full_season_data()
    if df is None:
        print("No data to analyze")
        return
    
    # do various analyses
    print("\nRunning qualifying performance analysis...")
    analyzed_df = analyze_qualifying_performance(df)
    
    print("\nAnalyzing weather impact...")
    weather_results = weather_impact_analysis(analyzed_df)
    
    print("\nTeam performance deep dive...")
    team_performance_deep_dive(analyzed_df)
    
    print("\nGenerating summary statistics...")
    summary_stats = create_summary_stats(analyzed_df)
    
    # save everything
    save_day3_results(analyzed_df, summary_stats, weather_results)
    
    print(f"\nDAY 3 ANALYSIS COMPLETE!")
    print(f"Analyzed {summary_stats['total_records']} driver performances")
    print(f"Across {summary_stats['races_analyzed']} races and {summary_stats['weather_conditions']} weather conditions")

if __name__ == "__main__":
    main()