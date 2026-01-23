import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# streamlit page config
st.set_page_config(
    page_title="Kdrama Dashboard",  # the page title shown in the browser tab
    page_icon="🎬",  # the page favicon shown in the browser tab
    layout="wide",  # page layout : use the entire screen
)

# Run in command line:
# streamlit run dashboard_test.py

# load data
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "kdrama.csv"

df = pd.read_csv(DATA_PATH)


# add page title
st.title("Korean Dramas Dashboard")

# expander to show/hide the 'about dataset' section
with st.expander('About the Dataset'):
    st.write("""This Dataset was obtained on Kaggle containing curated metadata for the highest-ranked Korean dramas based on user ratings from MyDramaList. Each row represents a single drama, with columns capturing broadcast details, creative contributors, genres, ratings, and rankings.""")

st.header("Exploratory Analysis on Ratings")

# 1. Add a search bar
search_query = st.text_input("🔍 Search for a Kdrama title:", "")

# 2. Filter the dataframe based on search
if search_query:
    # We filter the 'Name' column
    filtered_df = df[df['Name'].str.contains(search_query, case=False, na=False)]
    
    if not filtered_df.empty:
        st.write(f"Found {len(filtered_df)} result(s):")
        
        # 3. Show only specific columns like Name and Rank
        st.dataframe(filtered_df[['Name', 'Rank', 'Rating']], use_container_width=True)
    else:
        st.warning("No Kdrama found with that name. Try another one!")
else:
    # Show the full top 10 if the search bar is empty
    st.caption("Showing Top 10 Kdramas:")
    st.dataframe(df[['Name', 'Rank', 'Rating']].head(10), use_container_width=True)


## idea:
# create a sidebar with filtering options. nothing is selected by default but we can do 
# groupby: people: directors, screenwriters, casts (actors) --> averange rating & no. of dramas (not clean) - done
# global filter by: year of release - done


# --- 1. Sidebar Configuration ---
st.sidebar.header("Global Filters")

# Year Slider (Fixed range 2003 - 2022)
year_range = st.sidebar.slider(
    "Year of Release:",
    min_value=2003,
    max_value=2022,
    value=(2003, 2022) # Default selection covers the whole range
)

st.sidebar.divider() # Visual separator
st.sidebar.header("Analysis Settings")

# Choose the Role
role = st.sidebar.selectbox(
    "Analyse by Role:",
    options=["Director", "Screenwriter", "Cast"],
    index=None,
    placeholder="Select a Role"
)

# Choose the Metric
metric_choice = st.sidebar.selectbox(
    "Choose Metric to Visualise:",
    options=["Average Rating", "Number of Dramas"],
    index=None,
    placeholder="Select a Metric"
)

# --- 2. Filter the Dataframe by Year ---
# This ensures that the 'df' used below only contains the selected years
filtered_df = df[(df['Year of release'] >= year_range[0]) & (df['Year of release'] <= year_range[1])]

# --- 3. Visualisation Logic ---
if role and metric_choice:
    st.header(f"{metric_choice} by {role}")
    
    # Use the filtered_df here instead of df.copy()
    analysis_df = filtered_df.copy()
    
    target_col = role
    
    # Data Cleaning: Split, Explode, and Strip
    analysis_df[target_col] = analysis_df[target_col].str.split(',')
    analysis_df = analysis_df.explode(target_col)
    analysis_df[target_col] = analysis_df[target_col].str.strip()
    
    # Aggregation
    stats = analysis_df.groupby(target_col).agg(
        avg_rating=('Rating', 'mean'),
        drama_count=('Rating', 'count')
    ).reset_index()

    # --- Switching Logic ---
    if metric_choice == "Average Rating":
        plot_x = 'avg_rating'
        plot_label = 'Average Rating'
        plot_color = 'RdPu'
        # Sort and take top 15
        plot_df = stats.sort_values(plot_x, ascending=False).head(15)
    else:
        plot_x = 'drama_count'
        plot_label = 'Total Dramas'
        plot_color = 'Blues'
        plot_df = stats.sort_values(plot_x, ascending=False).head(15)

    # --- 4. UI: Text and Plot ---
    st.caption(f"Results for dramas released between {year_range[0]} and {year_range[1]}.")
    st.caption(f"Showing the top 15 {role}s based on their **{metric_choice.lower()}**.")

    fig = px.bar(
        plot_df,
        x=plot_x,
        y=target_col,
        orientation='h',
        color=plot_x,
        labels={plot_x: plot_label, target_col: role},
        color_continuous_scale=plot_color,
        hover_data={plot_x: ":.2f" if metric_choice == "Average Rating" else True, target_col: True}
    )

    fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.info("Try out the filters in the sidebar!")
