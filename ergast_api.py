 
import requests
import json
from datetime import datetime

def test_ergast_connection():
    """Test basic connection to Ergast F1 API"""
    
    # Basic API endpoint
    base_url = "http://ergast.com/api/f1"
    
    print("Testing Ergast F1 API connection...")
    print("-" * 40)
    
    # Test 1: Get current season info
    url = f"{base_url}/current.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for bad status codes
        
        data = response.json()
        season_info = data['MRData']['RaceTable']
        
        print(f"✅ API Connection: SUCCESS")
        print(f"Current season: {season_info['season']}")
        print(f"Total races: {season_info['total']}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API Connection failed: {e}")
        return False

def explore_available_data():
    """Explore what data types are available"""
    
    print("\n" + "="*50)
    print("EXPLORING AVAILABLE DATA TYPES")
    print("="*50)
    
    base_url = "http://ergast.com/api/f1"
    
    # Test different endpoints
    endpoints = {
        "Races": "/2024.json",
        "Results": "/2024/1/results.json", 
        "Qualifying": "/2024/1/qualifying.json",
        "Drivers": "/2024/drivers.json",
        "Constructors": "/2024/constructors.json"
    }
    
    for name, endpoint in endpoints.items():
        print(f"\n📊 Testing {name} data...")
        
        try:
            response = requests.get(base_url + endpoint)
            response.raise_for_status()
            
            data = response.json()
            
            # Print basic info about each data type
            if name == "Races":
                races = data['MRData']['RaceTable']['Races']
                print(f"   Found {len(races)} races in 2024")
                print(f"   First race: {races[0]['raceName']} at {races[0]['Circuit']['circuitName']}")
                
            elif name == "Results":
                results = data['MRData']['RaceTable']['Races'][0]['Results']
                print(f"   Found {len(results)} race results")
                print(f"   Winner: {results[0]['Driver']['familyName']}")
                
            elif name == "Qualifying":
                qualifying = data['MRData']['RaceTable']['Races'][0]['QualifyingResults']
                print(f"   Found {len(qualifying)} qualifying results")
                print(f"   Pole position: {qualifying[0]['Driver']['familyName']}")
                
            elif name == "Drivers":
                drivers = data['MRData']['DriverTable']['Drivers']
                print(f"   Found {len(drivers)} drivers in 2024")
                
            elif name == "Constructors":
                constructors = data['MRData']['ConstructorTable']['Constructors']
                print(f"   Found {len(constructors)} teams in 2024")
                
        except Exception as e:
            print(f"   ❌ Error accessing {name}: {e}")

def get_sample_race_data():
    """Get detailed data from one race to understand structure"""
    
    print("\n" + "="*50)
    print("GETTING SAMPLE RACE DATA")
    print("="*50)
    
    base_url = "http://ergast.com/api/f1"
    
    # Get results from Bahrain 2024 (first race)
    print("📥 Downloading Bahrain 2024 race data...")
    
    try:
        # Get race results
        results_url = f"{base_url}/2024/1/results.json"
        response = requests.get(results_url)
        race_data = response.json()
        
        # Get qualifying results  
        qualifying_url = f"{base_url}/2024/1/qualifying.json"
        response = requests.get(qualifying_url)
        qualifying_data = response.json()
        
        # Save sample data
        with open('data/raw/sample_race_results.json', 'w') as f:
            json.dump(race_data, f, indent=2)
            
        with open('data/raw/sample_qualifying_results.json', 'w') as f:
            json.dump(qualifying_data, f, indent=2)
            
        print("✅ Sample data saved to data/raw/")
        
        # Show some basic analysis
        race_results = race_data['MRData']['RaceTable']['Races'][0]['Results']
        qualifying_results = qualifying_data['MRData']['RaceTable']['Races'][0]['QualifyingResults']
        
        print(f"\n📊 BASIC ANALYSIS:")
        print(f"Race: {race_data['MRData']['RaceTable']['Races'][0]['raceName']}")
        print(f"Date: {race_data['MRData']['RaceTable']['Races'][0]['date']}")
        
        print(f"\nTop 3 Qualifying:")
        for i in range(3):
            driver = qualifying_results[i]['Driver']['familyName']
            time = qualifying_results[i]['Q3']
            print(f"  {i+1}. {driver} - {time}")
            
        print(f"\nTop 3 Race Results:")
        for i in range(3):
            driver = race_results[i]['Driver']['familyName']
            time = race_results[i]['Time']['time'] if 'Time' in race_results[i] else 'N/A'
            print(f"  {i+1}. {driver} - {time}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error getting sample data: {e}")
        return False

if __name__ == "__main__":
    print("🏎️  F1 DATA EXPLORATION")
    print("=" * 50)
    
    # Run all tests
    if test_ergast_connection():
        explore_available_data()
        get_sample_race_data()
        
        print("\n" + "="*50)
        print("✅ DATA EXPLORATION COMPLETE!")
        print("Check the data/raw/ folder for sample files")
        print("="*50)
    else:
        print("❌ Could not connect to API")