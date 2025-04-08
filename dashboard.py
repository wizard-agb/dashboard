import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Construction Check Dashboard",
    page_icon="🏗️",
    layout="wide"
)

col_title, col_logo = st.columns([3, 1])  # Wider left column for text, narrower right for logo

with col_title:
    st.markdown("<h1 style='color:#0c2340;'>Construction Check Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#e07c00;'>Explore construction project trends by type and year</h3>", unsafe_allow_html=True)

with col_logo:
    st.image(
        "https://cdn.prod.website-files.com/63b68119ba1a9f43948a602f/6603f8f3151d0ac28befd166_Construction-Check_Logo_Horiz_TaglineR_CMYK-p-500.png",
        use_container_width=True
    )

custom_colors = ['#0c2340', '#e07c00',  '#7c7c7c', '#b2b2b2', '#cccccc']  # Add more if needed

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('numerically_cleaned.csv', index_col=False)
        df = df.iloc[:,1:]
        # treat outliers in total_mat_lab_equip column using IQR
        q1 = df['total_mat_lab_equip'].quantile(0.25)
        q3 = df['total_mat_lab_equip'].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        df = df[(df['total_mat_lab_equip'] >= lower_bound) & (df['total_mat_lab_equip'] <= upper_bound)]
        
        return df
    except FileNotFoundError:
        return create_sample_data()

def create_sample_data():
    project_types = ['Residential', 'Commercial', 'Transportation', 'Water', 'Public']
    years = [2020, 2021, 2022, 2023, 2024]

    data = []
    for i in range(50):
        project_type = np.random.choice(project_types)
        project_year = np.random.choice(years)
        total_cost = np.random.randint(50000, 1500000)

        data.append({
            'file_name': f'Project_{i+1}',
            'project_type': project_type,
            'project_year': project_year,
            'total_mat_lab_equip': total_cost
        })
    return pd.DataFrame(data)

# Load data
df = load_data()

# Sidebar filters (optional)
project_types = ['All'] + sorted(df['project_type'].unique().tolist())
selected_project_type = 'All'

years = ['All'] + sorted(df['project_year'].unique().tolist())
selected_year = 'All'

# Apply filters
filtered_df = df.copy()
if selected_project_type != 'All':
    filtered_df = filtered_df[filtered_df['project_type'] == selected_project_type]
if selected_year != 'All':
    filtered_df = filtered_df[filtered_df['project_year'] == selected_year]

# Dashboard Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Total Project Cost by Type")
    fig = px.bar(filtered_df, x="project_type", y="total_mat_lab_equip", 
                 labels={"total_mat_lab_equip": "Total Cost ($)"}, 
                 title="Project Cost by Type", color="project_type",
                 color_discrete_sequence=custom_colors)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Line Items Cost Scatter")
    df_grouped = filtered_df.groupby("file_name").agg(
        total_mat_lab_equip=("total_mat_lab_equip", "sum"),
        line_items=("file_name", "count")
    ).reset_index()

    fig = px.scatter(df_grouped, x="line_items", y="total_mat_lab_equip", 
                     title="Project Cost vs Line Item Count",
                     labels={"line_items": "Line Item Count", "total_mat_lab_equip": "Total Cost ($)"},
                     color_discrete_sequence=custom_colors)
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Project Type Distribution")
    fig = px.pie(filtered_df, names="project_type", hole=0.4, labels={"project_type": "Project Type"}, title="Project Type Distribution", color_discrete_sequence=custom_colors)
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Cost Distribution")
    fig = px.histogram(filtered_df, x="total_mat_lab_equip", nbins=30, color_discrete_sequence=custom_colors, labels={"total_mat_lab_equip": "Total Cost ($)"})
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Data Explorer")
if st.checkbox("Show Raw Data"):
    st.write(filtered_df)

if not filtered_df.empty:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_project_data.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("Construction Check Dashboard | Created with Streamlit and Plotly")