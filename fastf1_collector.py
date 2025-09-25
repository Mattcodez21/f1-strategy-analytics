 
import fastf1
import pandas as pd
from datetime import datetime
import os

def test_fastf1_connection():
    """Test FastF1 library with recent race data"""
    
    print("🏎️  TESTING FASTF1 LIBRARY")
    print("=" * 50)
    
    # Enable FastF1 cache for faster loading
    fastf1.Cache.enable_cache('data/external/fastf1_cache')
    
    try:
        # Get 2024 season schedule
        print("📅 Loading 2024 F1 season schedule...")
        schedule = fastf1.get_event_schedule(2024)
        print(f"✅ Found {len(schedule)} events in 2024")
        
        # Show first few races
        print("\n📊 First 5 races of 2024:")
        for i in range(min(5, len(schedule))):
            event = schedule.iloc[i]
            print(f"  {i+1}. {event['EventName']} - {event['Location']} ({event['EventDate'].strftime('%b %d')})")
        
        return schedule
        
    except Exception as e:
        print(f"❌ Error loading FastF1: {e}")
        return None

def explore_race_session_data(schedule):
    """Get detailed data from one race session"""
    
    print("\n" + "=" * 50)
    print("EXPLORING RACE SESSION DATA")
    print("=" * 50)
    
    try:
        # Get the first completed race (Bahrain 2024)
        print("🏁 Loading Bahrain GP 2024 data...")
        
        # Load qualifying session
        qualifying = fastf1.get_session(2024, 'Bahrain', 'Q')
        qualifying.load()
        
        print("✅ Qualifying session loaded successfully!")
        print(f"   Session: {qualifying.event['EventName']}")
        print(f"   Date: {qualifying.date}")
        print(f"   Weather: {qualifying.weather_data.iloc[0]['AirTemp']}°C")
        
        # Get qualifying results
        quali_results = qualifying.results
        print(f"\n🏆 Qualifying Results (Top 5):")
        for i in range(min(5, len(quali_results))):
            driver = quali_results.iloc[i]
            print(f"  {driver['Position']:2.0f}. {driver['Abbreviation']} - {driver['Q3'] if pd.notna(driver['Q3']) else driver['Q2'] if pd.notna(driver['Q2']) else driver['Q1']}")
        
        # Load race session
        print("\n🏁 Loading race session...")
        race = fastf1.get_session(2024, 'Bahrain', 'R')
        race.load()
        
        print("✅ Race session loaded successfully!")
        
        # Get race results
        race_results = race.results
        print(f"\n🏆 Race Results (Top 5):")
        for i in range(min(5, len(race_results))):
            driver = race_results.iloc[i]
            time_str = str(driver['Time']) if pd.notna(driver['Time']) else 'DNF'
            print(f"  {driver['Position']:2.0f}. {driver['Abbreviation']} - {time_str}")
        
        # Save sample data
        print("\n💾 Saving sample data...")
        os.makedirs('data/raw', exist_ok=True)
        
        quali_results.to_csv('data/raw/sample_qualifying.csv', index=False)
        race_results.to_csv('data/raw/sample_race_results.csv', index=False)
        
        # Get weather data
        weather_df = qualifying.weather_data
        weather_df.to_csv('data/raw/sample_weather.csv', index=False)
        
        print("✅ Sample data saved to data/raw/")
        
        return qualifying, race
        
    except Exception as e:
        print(f"❌ Error loading race data: {e}")
        return None, None

def analyze_sample_data(qualifying, race):
    """Basic analysis of the loaded data"""
    
    if qualifying is None or race is None:
        return
        
    print("\n" + "=" * 50)
    print("BASIC DATA ANALYSIS")
    print("=" * 50)
    
    try:
        # Compare qualifying vs race positions
        quali_results = qualifying.results[['Position', 'Abbreviation']].copy()
        race_results = race.results[['Position', 'Abbreviation']].copy()
        
        # Merge data
        quali_results.columns = ['QualiPos', 'Driver']
        race_results.columns = ['RacePos', 'Driver']
        
        comparison = pd.merge(quali_results, race_results, on='Driver', how='inner')
        comparison['PositionChange'] = comparison['QualiPos'] - comparison['RacePos']
        
        print("📊 QUALIFYING VS RACE POSITION ANALYSIS:")
        print("Driver  | Quali | Race | Change")
        print("-" * 35)
        
        for _, row in comparison.head(10).iterrows():
            change = f"+{int(row['PositionChange'])}" if row['PositionChange'] > 0 else str(int(row['PositionChange']))
            print(f"{row['Driver']:8}|   {int(row['QualiPos']):2}  |  {int(row['RacePos']):2}  |   {change:>3}")
        
        # Weather analysis
        weather = qualifying.weather_data
        print(f"\n🌤️  WEATHER CONDITIONS:")
        print(f"Temperature: {weather['AirTemp'].mean():.1f}°C (avg)")
        print(f"Humidity: {weather['Humidity'].mean():.1f}% (avg)")
        print(f"Pressure: {weather['Pressure'].mean():.1f} mbar (avg)")
        
        print(f"\n✅ This is the kind of data we'll use for your analysis!")
        
    except Exception as e:
        print(f"❌ Error in analysis: {e}")

if __name__ == "__main__":
    # Run the exploration
    schedule = test_fastf1_connection()
    
    if schedule is not None:
        qualifying, race = explore_race_session_data(schedule)
        analyze_sample_data(qualifying, race)
        
        print("\n" + "=" * 50)
        print("🎉 FASTF1 EXPLORATION COMPLETE!")
        print("✅ You now have sample F1 data in data/raw/")
        print("✅ Ready to build your analysis pipeline!")
        print("=" * 50)