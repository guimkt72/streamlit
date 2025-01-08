import streamlit as st
import pandas as pd

# Assuming your DataFrame is already loaded (in the future from API)
# For now, let's load it directly from Excel
df = pd.read_excel('teste_gc.xlsx')

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

# Pivot the data to create a format suitable for plotting
pivot_df = grouped_df.pivot(index='mes', columns='nome', values=selected_metric)

# Create the plot
st.subheader(f"{selected_metric_name} by Player Over Time")
st.line_chart(pivot_df)

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