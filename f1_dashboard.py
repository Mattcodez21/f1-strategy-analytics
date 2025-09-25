"""
F1 Strategic Analysis Dashboard

This is my F1 dashboard for analyzing qualifying vs race performance.
Built this for my placement applications to show I can work with data and build web apps.

Still learning Streamlit but getting the hang of it!
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Page setup - took me a while to figure out these settings
st.set_page_config(
    page_title="F1 Strategy Dashboard",
    page_icon="🏁", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - copied some of this from online tutorials and modified it
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF1E00;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: linear-gradient(90deg, #FF1E00, #FF8C00);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    /* tried to make the tabs look like F1 colors */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #FF1E00;
        color: white;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 24px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF8C00;
    }
</style>
""", unsafe_allow_html=True)

# Load the data - this function uses caching which I learned makes things faster
@st.cache_data
def load_f1_data():
    """Load the F1 data from CSV files"""
    try:
        # these are the files created by my analysis scripts
        main_df = pd.read_csv("data/processed/day3_full_analysis.csv")
        day2_df = pd.read_csv("data/processed/day2_analysis_data.csv")
        return main_df, day2_df
    except FileNotFoundError:
        st.error("Data files not found! Make sure you've run the data collection scripts first.")
        return None, None

@st.cache_data  
def calculate_metrics(df):
    """Calculate the key metrics for the dashboard"""
    if df is None or df.empty:
        return {}
    
    # find position columns automatically - this was tricky to get right
    pos_cols = [col for col in df.columns if 'position' in col.lower()]
    team_cols = [col for col in df.columns if 'team' in col.lower()]
    
    metrics = {}
    
    # only do correlation if we have both qualifying and race positions
    if len(pos_cols) >= 2:
        qual_pos = pos_cols[0] 
        race_pos = pos_cols[1]
        
        # calculate correlation - this is the main finding of my project
        correlation = df[qual_pos].corr(df[race_pos])
        metrics['qualifying_correlation'] = correlation
        metrics['r_squared'] = correlation ** 2
        
        # position changes (negative = gained positions)
        pos_changes = df[race_pos] - df[qual_pos]
        metrics['avg_position_change'] = pos_changes.mean()
        metrics['biggest_gain'] = pos_changes.min()
        metrics['biggest_loss'] = pos_changes.max()
    
    if team_cols:
        metrics['total_teams'] = df[team_cols[0]].nunique()
    metrics['total_records'] = len(df)
    
    return metrics

def create_qualifying_chart(df):
    """Create the qualifying time analysis chart"""
    # check if we have the data we need
    if 'quali_time' not in df.columns or 'team' not in df.columns:
        st.warning("Missing qualifying time or team data")
        return None
    
    # clean up the data
    df_clean = df.dropna(subset=['quali_time', 'team']).copy()
    
    if df_clean.empty:
        st.warning("No qualifying data available")
        return None
    
    # convert time format - this was a pain to figure out!
    def time_to_seconds(time_str):
        try:
            if 'days' in str(time_str):
                parts = str(time_str).split()
                time_part = parts[-1]
                time_bits = time_part.split(':')
                if len(time_bits) == 3:
                    mins = float(time_bits[1])
                    secs = float(time_bits[2])
                    return mins * 60 + secs
            return float(time_str)
        except:
            return None
    
    df_clean['quali_seconds'] = df_clean['quali_time'].apply(time_to_seconds)
    df_clean = df_clean.dropna(subset=['quali_seconds'])
    
    if df_clean.empty:
        st.warning("Couldn't convert qualifying times")
        return None
    
    # make the scatter plot
    fig = px.scatter(
        df_clean,
        x=range(len(df_clean)),
        y='quali_seconds',
        color='team',
        hover_data=['driver', 'team', 'quali_time'],
        title=f"Qualifying Times ({len(df_clean)} drivers)",
        labels={'x': 'Driver Index', 'y': 'Qualifying Time (seconds)'},
        color_discrete_sequence=px.colors.qualitative.Set3,
        width=800,
        height=500
    )
    
    # make points bigger so they're easier to see
    fig.update_traces(marker=dict(size=10, opacity=0.8))
    
    # add average line
    avg_time = df_clean['quali_seconds'].mean()
    fig.add_hline(y=avg_time, line_dash="dash", line_color="red",
                  annotation_text=f"Average: {avg_time:.3f}s")
    
    fig.update_layout(
        xaxis=dict(title="Driver Index", showgrid=True),
        yaxis=dict(title="Qualifying Time (seconds)", showgrid=True),
        showlegend=True,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        margin=dict(r=150)
    )
    
    return fig

def create_position_change_histogram(df):
    """Show how much drivers move up/down from qualifying to race"""
    pos_cols = [col for col in df.columns if 'position' in col.lower()]
    
    if len(pos_cols) < 2:
        return None
    
    # calculate position changes
    position_changes = df[pos_cols[1]] - df[pos_cols[0]]
    
    fig = px.histogram(
        x=position_changes,
        nbins=30,
        title="Position Changes (Qualifying to Race)",
        labels={"x": "Position Change", "count": "Number of Drivers"}
    )
    
    # add reference lines
    fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="No Change")
    fig.add_vline(x=position_changes.mean(), line_dash="dash", line_color="green",
                  annotation_text=f"Mean: {position_changes.mean():.1f}")
    
    fig.update_layout(height=400)
    return fig

def create_team_performance_chart(df):
    """Compare team performance using box plots"""
    pos_cols = [col for col in df.columns if 'position' in col.lower()]
    team_cols = [col for col in df.columns if 'team' in col.lower()]
    
    if not pos_cols or not team_cols:
        return None
    
    fig = px.box(
        df, 
        x=team_cols[0], 
        y=pos_cols[0],
        title="Team Performance Comparison",
        labels={team_cols[0]: "Team", pos_cols[0]: "Position"}
    )
    
    fig.update_layout(height=500, xaxis_tickangle=45)
    return fig

def create_weather_chart(df):
    """Weather analysis - still working on this part"""
    weather_cols = [col for col in df.columns if any(w in col.lower() 
                   for w in ['weather', 'rain', 'temp', 'condition'])]
    pos_cols = [col for col in df.columns if 'position' in col.lower()]
    
    if not weather_cols or not pos_cols:
        st.warning("No weather data found")
        return None
    
    try:
        fig = px.box(
            df,
            x=weather_cols[0],
            y=pos_cols[0], 
            title="Performance by Weather",
            labels={weather_cols[0]: "Weather", pos_cols[0]: "Position"}
        )
        fig.update_layout(height=400)
        return fig
    except:
        st.warning("Couldn't create weather chart")
        return None

# Main dashboard function
def main():
    # Header
    st.markdown('<h1 class="main-header">F1 Strategic Analysis Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading F1 data..."):
        main_data, day2_data = load_f1_data()
    
    if main_data is None:
        st.stop()
    
    # Sidebar controls
    st.sidebar.markdown("## Dashboard Controls")
    st.sidebar.markdown("### Race Selection")
    
    # find race columns (but not position columns - learned this the hard way!)
    race_cols = [col for col in main_data.columns if any(keyword in col.lower() 
                for keyword in ['race', 'event', 'session', 'grand', 'gp']) 
                and 'position' not in col.lower()]
    
    # let user choose analysis scope
    analysis_scope = st.sidebar.radio(
        "Analysis Scope:",
        ["All Races Combined", "Individual Race Analysis"],
        help="View all races together or pick a specific race"
    )
    
    filtered_data = main_data.copy()
    race_info = "All Races Combined"
    
    # individual race selection
    if analysis_scope == "Individual Race Analysis":
        if race_cols:
            race_col = race_cols[0]
            races = sorted(main_data[race_col].dropna().unique())
            
            selected_race = st.sidebar.selectbox("Select Race:", races)
            filtered_data = main_data[main_data[race_col] == selected_race]
            race_info = f"{selected_race}"
        else:
            st.sidebar.warning("No race data found")
    
    # show dataset info
    with st.sidebar:
        st.info(f"""
        **Current View:** {race_info}
        **Records:** {filtered_data.shape[0]}
        **Total Available:** {main_data.shape[0]} records
        **Columns:** {main_data.shape[1]} features
        """)
        
        # refresh button
        if st.button("Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    # Analysis tabs
    st.markdown("## Strategic Analysis")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Qualifying Performance", 
        "Position Changes", 
        "Team Comparison", 
        "Weather Impact"
    ])
    
    # Tab 1: Qualifying analysis
    with tab1:
        st.markdown(f"### Qualifying Performance - {race_info}")
        
        if analysis_scope == "All Races Combined":
            st.markdown("Qualifying times across all races in the dataset.")
        else:
            st.markdown(f"Qualifying performance for {race_info}.")
        
        fig1 = create_qualifying_chart(filtered_data)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
    
    # Tab 2: Position changes
    with tab2:
        st.markdown(f"### Position Changes - {race_info}")
        st.markdown("Shows how much drivers move up or down from qualifying to race finish.")
        
        fig2 = create_position_change_histogram(filtered_data)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
    
    # Tab 3: Team performance
    with tab3:
        st.markdown(f"### Team Performance - {race_info}")
        st.markdown("Compare how different F1 teams perform in qualifying.")
        
        fig3 = create_team_performance_chart(filtered_data)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
    
    # Tab 4: Weather impact
    with tab4:
        st.markdown(f"### Weather Impact - {race_info}")
        st.markdown("How weather conditions affect F1 performance.")
        
        fig4 = create_weather_chart(filtered_data)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)
    
    # Raw data explorer
    with st.expander("Raw Data Explorer"):
        st.markdown(f"### Data View - {race_info}")
        st.dataframe(filtered_data.head(100), use_container_width=True)
        
        # download button
        csv = filtered_data.to_csv(index=False)
        filename = f"f1_data_{race_info.replace(' ', '_')}.csv" if analysis_scope == "Individual Race Analysis" else "f1_data_all.csv"
        st.download_button(
            label=f"Download CSV ({filtered_data.shape[0]} records)",
            data=csv,
            file_name=filename,
            mime="text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **F1 Strategic Analysis Dashboard**  
    Built with Python, Streamlit, and Plotly | Data from FastF1 API  
    Created for placement applications - demonstrates data analysis and web development skills
    """)

if __name__ == "__main__":
    main()