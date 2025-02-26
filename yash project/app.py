import streamlit as st
import pandas as pd
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
from chatbot import OlympicsInsightBot
import os
from dotenv import load_dotenv

load_dotenv()

# Define the create_insights_panel function first
def create_insights_panel(data_context, title="AI Insights"):
    # CSS for the sliding panel
    st.markdown(
        """
        <style>
        .ai-panel {
            position: fixed;
            right: 0;
            top: 0;
            width: 350px;
            height: 100vh;
            background: white;
            box-shadow: -2px 0 5px rgba(0,0,0,0.1);
            padding: 20px;
            z-index: 1000;
            overflow-y: auto;
        }
        .close-button {
            position: absolute;
            right: 10px;
            top: 10px;
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: #ff4b4b;
        }
        .show-button {
            position: fixed;
            right: 0;
            top: 50%;
            transform: translateY(-50%);
            background: #ff4b4b;
            color: white;
            padding: 10px;
            border: none;
            cursor: pointer;
            border-radius: 5px 0 0 5px;
            z-index: 999;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Initialize session state for panel visibility
    if 'panel_visible' not in st.session_state:
        st.session_state.panel_visible = True

    # Show/Hide button
    if not st.session_state.panel_visible:
        if st.button("📊 Show Insights", key="show_insights"):
            st.session_state.panel_visible = True
            st.rerun()

    # Panel content
    if st.session_state.panel_visible:
        with st.container():
            st.markdown(
                f"""
                <div class="ai-panel">
                    <button class="close-button" onclick="document.querySelector('.ai-panel').style.display='none';">×</button>
                    <h3>{title}</h3>
                    <div id="insights-content">
                        <div class="loading">Analyzing data...</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            try:
                insights = chatbot.get_component_insights(data_context)
                st.markdown(
                    f"""
                    <div class="ai-panel">
                        <button class="close-button" onclick="document.querySelector('.ai-panel').style.display='none';">×</button>
                        <h3>{title}</h3>
                        <div id="insights-content">
                            {insights}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"Error generating insights: {str(e)}")

            if st.button("✖️ Close", key="close_panel"):
                st.session_state.panel_visible = False
                st.rerun()

st.set_page_config(page_title="Olympics Analysis", layout="wide")

# Hide Streamlit branding
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Load Data
df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

df = preprocessor.preprocess(df, region_df)

# Sidebar
st.sidebar.title("🏅 OlympiX - Olympics Analysis")
st.sidebar.image('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQziycHlXw_iHLMN7JjFm2uwwSUO_tZwyKW-w&s')

# Initialize the chatbot
chatbot = OlympicsInsightBot()

user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis')
)

# Medal Tally
if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally")
    years, country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)
    
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("Overall Tally")
    if selected_year != 'Overall' and selected_country == 'Overall':
        st.title("Medal Tally in " + str(selected_year) + " Olympics")
    if selected_year == 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " overall performance")
    if selected_year != 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " performance in " + str(selected_year) + " Olympics")
    
    st.table(medal_tally)

    # Add AI insights panel
    medal_context = f"""
    Analysis for: {selected_country if selected_country != 'Overall' else 'All Countries'}
    Time Period: {selected_year if selected_year != 'Overall' else 'All Years'}
    Medal Distribution: {medal_tally.to_dict()}
    """
    create_insights_panel(medal_context, "Medal Analysis")


# Overall Analysis
if user_menu == 'Overall Analysis':
    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]

    st.title("Top Statistics")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📅 Editions", value=editions)
    with col2:
        st.metric(label="🌎 Hosts", value=cities)
    with col3:
        st.metric(label="🏅 Sports", value=sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🎟 Events", value=events)
    with col2:
        st.metric(label="🌍 Nations", value=nations)
    with col3:
        st.metric(label="👤 Athletes", value=athletes)

    # Heatmap - No. of Events Over Time
    st.title("📊 No. of Events Over Time (Each Sport)")
    fig, ax = plt.subplots(figsize=(20, 20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax = sns.heatmap(
        x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype('int'),
        annot=True,
        cmap="coolwarm"
    )
    st.pyplot(fig)

    # Select Country for Top 10 Athletes
    st.sidebar.header("🏅 Top 10 Athletes Analysis")
    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()
    selected_country = st.sidebar.selectbox("Select Country", country_list)

    # Fetch Top 10 Athletes for selected country
    top_athletes = helper.top_10_athletes(df, selected_country)

    # Display Top 10 Athletes in a table
    st.title(f"🏅 Top 10 Athletes from {selected_country}")
    st.table(top_athletes)

    # Add AI insights panel
    overall_context = f"""
    Olympics Statistics:
    - Total Editions: {editions}
    - Total Sports: {sports}
    - Total Events: {events}
    - Total Athletes: {athletes}
    - Total Nations: {nations}
    """
    create_insights_panel(overall_context, "Overall Olympics Analysis")


# Country-wise Analysis
if user_menu == 'Country-wise Analysis':
    st.sidebar.title('Country-wise Analysis')
    
    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()
    
    selected_country = st.sidebar.selectbox('Select a Country', country_list)
    
    country_df = helper.yearwise_medal_tally(df, selected_country)
    fig = px.line(country_df, x="Year", y="Medal", title=f"{selected_country} Medal Tally Over the Years")
    st.plotly_chart(fig)

    st.title(f"{selected_country} Excels in the Following Sports")
    pt = helper.country_event_heatmap(df, selected_country)

    if not pt.empty:
        fig, ax = plt.subplots(figsize=(20, 20))
        sns.heatmap(pt, annot=True, ax=ax, cmap="coolwarm")
        st.pyplot(fig)
    else:
        st.warning(f"No event data available for {selected_country}.")

    # Add AI insights panel
    country_context = f"""
    Country: {selected_country}
    Medal History: {country_df.to_dict()}
    """
    create_insights_panel(country_context, f"{selected_country} Analysis")

# Athlete-wise Analysis
if user_menu == 'Athlete-wise Analysis':
    st.sidebar.title("Athlete-Wise Analysis")

    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    selected_athlete = st.sidebar.selectbox("Select an Athlete", athlete_df['Name'].unique())

    st.title(f"Athlete-Wise Analysis for {selected_athlete}")

    athlete_data = df[df['Name'] == selected_athlete]

    st.write("🏅 *Medal Count*")
    medal_count = athlete_data.groupby('Medal').size()
    st.bar_chart(medal_count)

    st.write("📊 *Performance Over Years*")
    fig = px.line(athlete_data, x="Year", y="Event", title=f"{selected_athlete} Events Over the Years")
    st.plotly_chart(fig)

    st.write("📍 *Country Representation*")
    st.write(athlete_data[['Year', 'Sport', 'region']].drop_duplicates())

    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    # Add AI insights panel
    athlete_context = f"""
    Age Distribution:
    - Overall Athletes: Mean={x1.mean():.2f}, Median={x1.median():.2f}
    - Gold Medalists: Mean={x2.mean():.2f}, Median={x2.median():.2f}
    - Silver Medalists: Mean={x3.mean():.2f}, Median={x3.median():.2f}
    - Bronze Medalists: Mean={x4.mean():.2f}, Median={x4.median():.2f}
    """
    create_insights_panel(athlete_context, "Athlete Analysis")