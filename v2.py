import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px

# Add the directory containing main_gc.py to Python's path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_gc import get_data

# Add caching to prevent reloading data on every interaction
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    # Show loading message
    with st.spinner('Fetching data from API... This might take a minute...'):
        try:
            df = get_data()  # Your API function from main_gc.py
            return df
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None

# Initialize session state for data if not exists
if 'data' not in st.session_state:
    st.session_state.data = None

# Add a refresh button
if st.button('Refresh Data'):
    st.session_state.data = None

# Load data if not in session state
if st.session_state.data is None:
    st.session_state.data = load_data()

# Only show the dashboard if we have data
if st.session_state.data is not None:
    df = st.session_state.data
    
    st.title("Game Statistics Dashboard")

    # Define metrics that can be plotted
    metrics = {
        'KDR': 'kdr',
        'ADR': 'adr',
        'Kills': 'matou',
        'Deaths': 'morreu',
        'Multi Kills': 'multikills',
        'First Kills': 'firstkills',
        'Headshot Rate': 'headshotrate',
        'Bombs Planted': 'bomb_planted',
        'Bombs Defused': 'bomb_defused',
        'Matches Played': 'matches'
    }

    # Let user select the metric to analyze with friendly names
    selected_metric_name = st.selectbox("Select metric to analyze", list(metrics.keys()))
    selected_metric = metrics[selected_metric_name]

    # Group the data by month and player, calculating the mean of the selected metric
    grouped_df = df.groupby(['mes', 'nome'])[selected_metric].mean().reset_index()

    # Create the plot using Plotly Express
    fig = px.line(grouped_df, 
                  x='mes', 
                  y=selected_metric, 
                  color='nome',
                  title=f"{selected_metric_name} by Player Over Time",
                  labels={
                      'mes': 'Month',
                      selected_metric: selected_metric_name,
                      'nome': 'Player'
                  },
                  hover_data={selected_metric: ':.2f'}) # Format hover data to 2 decimal places

    # Update layout for better appearance
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title=selected_metric_name,
        legend_title="Players",
        hovermode='x unified'  # Shows all values for agiven x-coordinate
    )

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

    # Show summary statistics
    st.subheader("Summary Statistics")
    summary_df = df.groupby('nome')[selected_metric].agg(['mean', 'min', 'max']).round(2)
    summary_df.columns = ['Average', 'Minimum', 'Maximum']
    st.write(summary_df)

# Add custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #000000;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)