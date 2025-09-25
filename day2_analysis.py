"""
Day 2 Analysis Script

Building on the data collection from yesterday.
Going to try some basic analysis to see what patterns I can find in the F1 data.
"""

from data_collection import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("F1 Strategic Analysis - Day 2")
print("=" * 40)

def collect_multiple_races():
    """Get data from a few races to start building a dataset"""
    print(f"\nTesting with Bahrain 2024 first...")
    race_data = collect_race_data(2024, 'Bahrain')
    
    if race_data:
        df = create_combined_dataframe(race_data)
        if df is not None:
            print(f"   Added {len(df)} driver records")
            print(f"Dataset preview:")
            # show just the basic info for now
            print(df[['driver', 'team', 'quali_time']].head())
            return df
    
    print("Failed to collect data")
    return None

def analyze_qualifying_data(df):
    """Look at the qualifying time data we collected"""
    print("\nQUALIFYING TIME ANALYSIS")
    print("=" * 30)
    
    # basic stats about qualifying times
    if 'quali_time' in df.columns:
        print(f"Total drivers: {len(df)}")
        print(f"Teams represented: {df['team'].nunique()}")
        
        # show fastest and slowest times
        print(f"\nQualifying time range:")
        print(f"Fastest: {df['quali_time'].min()}")
        print(f"Slowest: {df['quali_time'].max()}")
        
        # team performance summary
        print(f"\nTop 3 teams by average qualifying:")
        team_performance = df.groupby('team')['quali_position'].mean().sort_values().head(3)
        for team, avg_pos in team_performance.items():
            print(f"  {team}: {avg_pos:.1f}")
    
    return df

def create_basic_visualization(df):
    """Make a simple chart to visualize the data"""
    print("\nCreating basic visualization...")
    
    if 'quali_position' in df.columns and 'team' in df.columns:
        # simple bar chart of team performance
        plt.figure(figsize=(10, 6))
        team_avg = df.groupby('team')['quali_position'].mean().sort_values()
        
        plt.bar(range(len(team_avg)), team_avg.values)
        plt.xticks(range(len(team_avg)), team_avg.index, rotation=45)
        plt.ylabel('Average Qualifying Position')
        plt.title('Team Qualifying Performance')
        plt.tight_layout()
        
        # save the plot
        plt.savefig('../visualizations/day2_team_performance.png')
        print("Saved visualization to: visualizations/day2_team_performance.png")
        plt.show()

def save_results(df):
    """Save the analysis results"""
    # save the dataset
    df.to_csv('../data/processed/day2_analysis_data.csv', index=False)
    print(f"\nSaved data to: data/processed/day2_analysis_data.csv")
    
    # create a simple summary file
    with open('../data/processed/day2_summary_stats.txt', 'w') as f:
        f.write("Day 2 Analysis Summary\n")
        f.write("=" * 25 + "\n\n")
        f.write(f"Total drivers analyzed: {len(df)}\n")
        f.write(f"Teams in dataset: {df['team'].nunique()}\n")
        
        if 'quali_position' in df.columns:
            f.write(f"Average qualifying position: {df['quali_position'].mean():.2f}\n")
    
    print(f"Saved summary to: data/processed/day2_summary_stats.txt")

def main():
    """Main analysis pipeline for day 2"""
    
    # first check if everything is set up
    print("Checking FastF1 setup...")
    if not test_fastf1_connection():
        print("FastF1 setup failed - check your connection")
        return
    
    # collect some race data
    print("\nCollecting race data...")
    df = collect_multiple_races()
    if df is None:
        print("No data collected - stopping here")
        return
    
    # do basic analysis
    analyzed_df = analyze_qualifying_data(df)
    
    # make a visualization
    create_basic_visualization(analyzed_df)
    
    # save everything
    save_results(analyzed_df)
    
    print(f"\nDay 2 Analysis Complete!")
    print(f"Next step: expand to more races and do deeper analysis")

if __name__ == "__main__":
    main()