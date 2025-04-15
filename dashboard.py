import streamlit as st
import pandas as pd
import plotly.express as px




# Load your data (replace with actual file path or source)
data = pd.read_csv("cleaned.csv")

# Clean column names
cols = [col.strip() for col in data.columns]
data.columns = cols

# Convert total to numeric if not already
data['total_mat_lab_equip'] = pd.to_numeric(data['total_mat_lab_equip'], errors='coerce')

# Custom color palette
custom_colors = ['#0c2340', '#e07c00', '#7c7c7c', '#b2b2b2', '#cccccc']

# Set page configuration
st.set_page_config(
    page_title="Construction Check Dashboard",
    page_icon="🏗️",
    layout="wide"
)

col_title, col_logo = st.columns([3, 1])  # Wider left column for text, narrower right for logo

with col_title:
    st.markdown("<h1 style='color:#0c2340;'>Construction Check Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#e07c00;'>PCS Cost Data Summary</h3>", unsafe_allow_html=True)

with col_logo:
    st.image(
        "https://cdn.prod.website-files.com/63b68119ba1a9f43948a602f/6603f8f3151d0ac28befd166_Construction-Check_Logo_Horiz_TaglineR_CMYK-p-500.png",
        use_container_width=True
    )

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    selected_project = st.multiselect("Project Id", options=data['project_id'].unique())
    selected_category = st.multiselect("Construction Category", options=data['construction_category'].dropna().unique())

# Apply filters
filtered_data = data.copy()
if selected_project:
    filtered_data = filtered_data[filtered_data['project_id'].isin(selected_project)]
if selected_category:
    filtered_data = filtered_data[filtered_data['construction_category'].isin(selected_category)]

# Summary statistics
st.subheader("Summary")
st.metric("Total Cost", f"${filtered_data['total_mat_lab_equip'].sum():,.2f}")
st.metric("# of Items", f"{len(filtered_data):,}")

# ----- Section 1: Projects by Sum of Cost -----
st.subheader("Projects by Sum of Cost")
col1, col2 = st.columns(2)

# Group by construction category
with col1:
    grouped_by_category = (
        filtered_data.groupby('construction_category')['total_mat_lab_equip']
        .sum()
        .reset_index()
        .sort_values(by='total_mat_lab_equip', ascending=False)
    )
    fig1 = px.bar(grouped_by_category, x='construction_category', y='total_mat_lab_equip',
                  title="Total Cost by Construction Category",
                  labels={'total_mat_lab_equip': 'Total Cost', 'construction_category': 'Category'},
                  color_discrete_sequence=custom_colors)
    st.plotly_chart(fig1, use_container_width=True)

# Group by project category
with col2:
    grouped_by_proj_cat = (
        filtered_data.groupby('project_category')['total_mat_lab_equip']
        .sum()
        .reset_index()
        .sort_values(by='total_mat_lab_equip', ascending=False)
    )
    fig2 = px.bar(grouped_by_proj_cat, x='project_category', y='total_mat_lab_equip',
                  title="Total Cost by Project Category",
                  labels={'total_mat_lab_equip': 'Total Cost', 'project_category': 'Project Category'},
                  color_discrete_sequence=custom_colors)
    st.plotly_chart(fig2, use_container_width=True)

# ----- Section 2: Count of Line Items by Categories -----
st.subheader("Count of Line Items by Categories")
col3, col4 = st.columns(2)

with col3:
    count_by_construction_category = filtered_data['construction_category'].value_counts().reset_index()
    count_by_construction_category.columns = ['construction_category', 'count']
    fig3 = px.bar(count_by_construction_category, x='construction_category', y='count',
                 title="Line Item Count by Construction Category",
                 color_discrete_sequence=custom_colors)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    count_by_project_category = filtered_data['project_category'].value_counts().reset_index()
    count_by_project_category.columns = ['project_category', 'count']
    fig4 = px.bar(count_by_project_category, x='project_category', y='count',
                 title="Line Item Count by Project Category",
                 color_discrete_sequence=custom_colors)
    st.plotly_chart(fig4, use_container_width=True)

# Total cost per source file
cost_by_file = filtered_data.groupby('source_file_name')['total_mat_lab_equip'].sum().reset_index()
fig5 = px.pie(cost_by_file, values='total_mat_lab_equip', names='source_file_name',
              title="Cost Distribution by Source File",
              color_discrete_sequence=custom_colors)
fig5.update_traces(textinfo='none')
st.plotly_chart(fig5, use_container_width=True)

# ----- Section 3: Cost vs. Line Item Count -----
st.subheader("Cost vs. Line Item Count")

cost_vs_count = filtered_data.groupby('project_id').agg(
    total_cost=('total_mat_lab_equip', 'sum'),
    line_item_count=('id', 'count')
).reset_index()

col5, col6 = st.columns(2)

with col5:
    st.subheader("Cost Distribution")
    filtered_data_outliers_1 = filtered_data[filtered_data['total_mat_lab_equip'] < 10000000]
    fig = px.histogram(filtered_data_outliers_1, x="total_mat_lab_equip", nbins=20, color_discrete_sequence=custom_colors, labels={"total_mat_lab_equip": "Total Cost ($)"})
    st.plotly_chart(fig, use_container_width=True)

with col6:
    st.subheader("Line Items Cost Scatter")
    # remove top 10 outliers
    filtered_data_outliers = filtered_data[filtered_data['total_mat_lab_equip'] < 1000000000]
    df_grouped = filtered_data_outliers.groupby("source_file_name").agg(
        total_mat_lab_equip=("total_mat_lab_equip", "sum"),
        line_items=("source_file_name", "count")
    ).reset_index()

    fig = px.scatter(df_grouped, x="line_items", y="total_mat_lab_equip", 
                     title="Project Cost vs Line Item Count",
                     labels={"line_items": "Line Item Count", "total_mat_lab_equip": "Total Cost ($)"},
                     color_discrete_sequence=custom_colors)
    st.plotly_chart(fig, use_container_width=True)

# Table preview
st.subheader("Data Preview")
st.dataframe(filtered_data.head(50))
