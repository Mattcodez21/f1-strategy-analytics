"""
Day 4: F1 Data Visualizations

Time to make some charts and graphs from all the data I've collected.
Want to create both static and interactive visualizations to show the F1 insights.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
from scipy import stats
import warnings
import os
warnings.filterwarnings('ignore')

print("F1 Visualization Development - Day 4")
print("=" * 40)

# set up some styling 
plt.style.use('default')
sns.set_palette("husl")

# F1 team colors - looked these up online
TEAM_COLORS = {
    'Red Bull Racing': '#1E41FF',
    'Mercedes': '#00D2BE', 
    'Ferrari': '#DC143C',
    'McLaren': '#FF8700',
    'Alpine': '#0090FF',
    'Aston Martin': '#006F62',
    'Williams': '#005AFF',
    'AlphaTauri': '#2B4562',
    'Alfa Romeo': '#900000',
    'Haas': '#FFFFFF',
    'RB': '#2B4562',  # AlphaTauri changed names
    'Kick Sauber': '#900000'  # Alfa Romeo changed too
}

# set up directories
DATA_PATH = "data/processed"
SAVE_PATH = "visualizations"
os.makedirs(SAVE_PATH, exist_ok=True)

print("Environment setup complete!")

def load_data():
    """Load the data files from previous days"""
    try:
        main_df = pd.read_csv("data/processed/day3_full_analysis.csv")
        day2_df = pd.read_csv("data/processed/day2_analysis_data.csv")
        
        print(f"Loaded main data: {main_df.shape}")
        print(f"Loaded day 2 data: {day2_df.shape}")
        
        return main_df, day2_df
        
    except FileNotFoundError as e:
        print(f"Could not load data: {e}")
        return None, None

def create_team_performance_chart(df):
    """Create a chart showing team qualifying performance"""
    print("Creating team performance chart...")
    
    pos_cols = [col for col in df.columns if 'position' in col.lower()]
    team_cols = [col for col in df.columns if 'team' in col.lower()]
    
    if not pos_cols or not team_cols:
        print("Missing required data columns")
        return None
    
    # create matplotlib chart first
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # left plot: box plot of team performance
    team_performance = []
    team_names = []
    
    for team in df[team_cols[0]].unique():
        team_data = df[df[team_cols[0]] == team]
        if len(team_data) > 2:  # need enough data points
            team_performance.append(team_data[pos_cols[0]].values)
            team_names.append(team)
    
    if team_performance:
        ax1.boxplot(team_performance, labels=team_names)
        ax1.set_title('Team Qualifying Performance Distribution')
        ax1.set_ylabel('Qualifying Position')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
    
    # right plot: average performance bar chart
    avg_performance = df.groupby(team_cols[0])[pos_cols[0]].mean().sort_values()
    
    bars = ax2.bar(range(len(avg_performance)), avg_performance.values, 
                   color='lightcoral', alpha=0.7)
    ax2.set_xticks(range(len(avg_performance)))
    ax2.set_xticklabels(avg_performance.index, rotation=45)
    ax2.set_ylabel('Average Qualifying Position')
    ax2.set_title('Team Average Qualifying Performance')
    ax2.grid(True, alpha=0.3)
    
    # add value labels on bars
    for bar, value in zip(bars, avg_performance.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{value:.1f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f'{SAVE_PATH}/team_performance_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig

def create_weather_analysis_chart(df):
    """Look at how weather affects qualifying performance"""
    print("Creating weather analysis...")
    
    weather_cols = [col for col in df.columns if any(w in col.lower() 
                   for w in ['weather', 'condition'])]
    pos_cols = [col for col in df.columns if 'position' in col.lower()]
    team_cols = [col for col in df.columns if 'team' in col.lower()]
    
    if not weather_cols:
        print("No weather data found")
        return None
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.ravel()
    
    # plot 1: weather distribution
    weather_col = weather_cols[0]
    weather_counts = df[weather_col].value_counts()
    
    axes[0].pie(weather_counts.values, labels=weather_counts.index, autopct='%1.1f%%')
    axes[0].set_title('Weather Conditions Distribution')
    
    # plot 2: performance by weather
    if pos_cols:
        pos_col = pos_cols[0]
        weather_performance = df.groupby(weather_col)[pos_col].mean()
        
        bars = axes[1].bar(range(len(weather_performance)), weather_performance.values, 
                          color='lightblue', alpha=0.7)
        axes[1].set_xticks(range(len(weather_performance)))
        axes[1].set_xticklabels(weather_performance.index)
        axes[1].set_ylabel('Average Qualifying Position')
        axes[1].set_title('Performance by Weather Condition')
        axes[1].grid(True, alpha=0.3)
        
        for bar, value in zip(bars, weather_performance.values):
            axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        f'{value:.1f}', ha='center', va='bottom')
    
    # plot 3: team performance in different weather
    if team_cols and pos_cols:
        team_col = team_cols[0]
        
        # create heatmap data
        pivot_data = df.pivot_table(values=pos_col, index=team_col, 
                                   columns=weather_col, aggfunc='mean')
        
        # only show teams with data in multiple conditions
        pivot_data = pivot_data.dropna()
        
        if not pivot_data.empty:
            sns.heatmap(pivot_data, ax=axes[2], cmap='RdYlGn_r', center=10, 
                       annot=True, fmt='.1f', cbar_kws={'label': 'Avg Position'})
            axes[2].set_title('Team Performance by Weather')
            axes[2].set_xlabel('Weather Condition')
            axes[2].set_ylabel('Team')
        else:
            axes[2].text(0.5, 0.5, 'Not enough data for heatmap', 
                        ha='center', va='center')
            axes[2].set_title('Team Weather Performance - Limited Data')
    
    # plot 4: qualifying time spread by weather  
    if 'quali_time' in df.columns:
        # this is tricky because times are in string format
        axes[3].text(0.5, 0.5, 'Time analysis coming soon', 
                    ha='center', va='center')
        axes[3].set_title('Qualifying Time Analysis by Weather')
    else:
        axes[3].text(0.5, 0.5, 'No qualifying time data', 
                    ha='center', va='center')
        axes[3].set_title('Time Analysis - No Data')
    
    plt.tight_layout()
    plt.savefig(f'{SAVE_PATH}/weather_impact_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig

def create_interactive_dashboard(df):
    """Make some interactive plotly charts"""
    print("Creating interactive dashboard...")
    
    pos_cols = [col for col in df.columns if 'position' in col.lower()]
    team_cols = [col for col in df.columns if 'team' in col.lower()]
    weather_cols = [col for col in df.columns if 'weather' in col.lower()]
    
    # create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Team Performance', 'Weather Impact', 
                       'Position Distribution', 'Team Comparison'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # plot 1: team performance box plot
    if team_cols and pos_cols:
        fig.add_trace(
            go.Box(
                y=df[pos_cols[0]],
                x=df[team_cols[0]],
                name='Team Performance'
            ),
            row=1, col=1
        )
    
    # plot 2: weather impact
    if weather_cols and pos_cols:
        fig.add_trace(
            go.Box(
                y=df[pos_cols[0]],
                x=df[weather_cols[0]],
                name='Weather Impact'
            ),
            row=1, col=2
        )
    
    # plot 3: position distribution
    if pos_cols:
        fig.add_trace(
            go.Histogram(
                x=df[pos_cols[0]],
                nbinsx=20,
                name='Position Distribution'
            ),
            row=2, col=1
        )
    
    # plot 4: team averages
    if team_cols and pos_cols:
        team_avg = df.groupby(team_cols[0])[pos_cols[0]].mean().sort_values()
        
        fig.add_trace(
            go.Bar(
                x=team_avg.index,
                y=team_avg.values,
                name='Team Averages'
            ),
            row=2, col=2
        )
    
    fig.update_layout(
        height=800,
        title_text="F1 Qualifying Analysis Interactive Dashboard",
        showlegend=False
    )
    
    # save as HTML
    fig.write_html(f'{SAVE_PATH}/interactive_dashboard.html')
    print("Saved interactive dashboard to HTML")
    fig.show()
    
    return fig

def create_summary_visualization(df):
    """Create a summary chart showing key insights"""
    print("Creating summary visualization...")
    
    team_cols = [col for col in df.columns if 'team' in col.lower()]
    pos_cols = [col for col in df.columns if 'position' in col.lower()]
    
    if not team_cols or not pos_cols:
        print("Missing data for summary")
        return None
    
    # simple summary stats
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # team performance with error bars
    team_stats = df.groupby(team_cols[0])[pos_cols[0]].agg(['mean', 'std', 'count'])
    team_stats = team_stats.sort_values('mean')
    
    # only show teams with enough data
    team_stats = team_stats[team_stats['count'] >= 3]
    
    if not team_stats.empty:
        x_pos = range(len(team_stats))
        ax.errorbar(x_pos, team_stats['mean'], yerr=team_stats['std'], 
                   fmt='o', capsize=5, capthick=2)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(team_stats.index, rotation=45)
        ax.set_ylabel('Average Qualifying Position')
        ax.set_title('Team Performance with Consistency (Error Bars = Std Dev)')
        ax.grid(True, alpha=0.3)
        ax.invert_yaxis()  # better positions at top
    
    plt.tight_layout()
    plt.savefig(f'{SAVE_PATH}/performance_summary.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig

def show_data_info(df, name="Dataset"):
    """Show basic info about the dataset"""
    print(f"\n{name.upper()} INFO")
    print("=" * 25)
    
    print(f"Shape: {df.shape}")
    print(f"Columns: {len(df.columns)}")
    
    # show column types
    print(f"\nColumn info:")
    for col in df.columns:
        dtype = df[col].dtype
        non_null = df[col].count()
        print(f"  {col:<20} | {str(dtype):<10} | {non_null} non-null")
    
    # show first few rows
    print(f"\nFirst 3 rows:")
    print(df.head(3))

def main():
    """Main visualization creation pipeline"""
    
    print("\nLoading data...")
    main_data, day2_data = load_data()
    
    if main_data is None:
        print("No data to visualize")
        return
    
    # show what we're working with
    show_data_info(main_data, "Main Analysis Data")
    
    print("\nCreating visualizations...")
    
    # create different charts
    try:
        print("\n1. Team Performance Analysis...")
        create_team_performance_chart(main_data)
        
        print("\n2. Weather Impact Analysis...")
        create_weather_analysis_chart(main_data)
        
        print("\n3. Interactive Dashboard...")
        create_interactive_dashboard(main_data)
        
        print("\n4. Summary Visualization...")
        create_summary_visualization(main_data)
        
        print(f"\nAll visualizations saved to: {SAVE_PATH}/")
        print("Files created:")
        print(f"  • team_performance_analysis.png")
        print(f"  • weather_impact_analysis.png") 
        print(f"  • interactive_dashboard.html")
        print(f"  • performance_summary.png")
        
        print("\nDay 4 Complete!")
        print("Next: review charts and prepare final analysis")
        
    except Exception as e:
        print(f"Error creating visualizations: {e}")
        print("Check data format and column names")
    
if __name__ == "__main__":
    main()