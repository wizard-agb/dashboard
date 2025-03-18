import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Construction Cost Analysis Dashboard",
    page_icon="🏗️",
    layout="wide"
)

# Dashboard title
st.title("Construction Check Analysis Dashboard")
st.markdown("### Analyze construction project costs by type, year, and categories")

# Load data function
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('dashboard_data/numerically_cleaned.csv', index_col=False)
        df = df.iloc[:,1:]
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure the file 'structured_data/numerically_cleaned.csv' exists.")
        # Create sample data for demo purposes if file is not found
        return create_sample_data()

def create_sample_data():
    """Create sample data for demo purposes"""
    project_types = ['Residential', 'Commercial', 'Transportation', 'Water', 'Public']
    years = [2020, 2021, 2022, 2023, 2024]
    
    sample_data = []
    for i in range(50):
        project_type = np.random.choice(project_types)
        project_year = np.random.choice(years)
        labor = np.random.randint(10000, 500000)
        material = np.random.randint(20000, 700000)
        equipment = np.random.randint(5000, 300000)
        total = labor + material + equipment
        
        sample_data.append({
            'file_name': f'Project_{i+1}',
            'project_type': project_type,
            'project_year': project_year,
            'labor_total': labor,
            'material_total': material,
            'equipment_total': equipment,
            'total_mat_lab_equip': total
        })
    
    return pd.DataFrame(sample_data)

# Load data
df = load_data()

# Sidebar for filtering options
st.sidebar.title("Filters")

# Filter by project type
project_types = ['All'] + sorted(df['project_type'].unique().tolist())
selected_project_type = st.sidebar.selectbox("Select Project Type", project_types)

# Filter by year
years = ['All'] + sorted(df['project_year'].unique().tolist())
selected_year = st.sidebar.selectbox("Select Year", years)

# Apply filters
filtered_df = df.copy()
if selected_project_type != 'All':
    filtered_df = filtered_df[filtered_df['project_type'] == selected_project_type]
if selected_year != 'All':
    filtered_df = filtered_df[filtered_df['project_year'] == selected_year]

# Outlier removal option
include_outliers = st.sidebar.checkbox("Include Outliers", value=True)

def remove_outliers(df, columns=None, threshold=1.5):
    if columns is None:
        columns = df.select_dtypes(include=['number']).columns
    
    df_clean = df.copy()
    
    for col in columns:
        Q1 = df[col].quantile(0.05)
        Q3 = df[col].quantile(0.95)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]
    
    return df_clean

if not include_outliers:
    filtered_df = remove_outliers(filtered_df, columns=['material_total','equipment_total','labor_total'], threshold=2)
    st.sidebar.info(f"Removed {len(df) - len(filtered_df)} outliers")

# Create two columns for the dashboard
col1, col2 = st.columns(2)

# Cost Breakdown by Project Type
with col1:
    st.subheader("Cost Breakdown by Project Type")
    
    if not filtered_df.empty:
        fig = px.bar(
            filtered_df, 
            x="project_type", 
            y=["labor_total", "material_total", "equipment_total"], 
            labels={"value": "Cost ($)", "variable": "Cost Category"}, 
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

# Cost Breakdown by Year
with col2:
    st.subheader("Cost Breakdown by Year")
    
    if not filtered_df.empty:
        fig = px.bar(
            filtered_df, 
            x="project_year", 
            y=["labor_total", "material_total", "equipment_total"], 
            labels={"value": "Cost ($)", "variable": "Cost Category"}, 
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

# Project Type Distribution
col3, col4 = st.columns(2)

with col3:
    st.subheader("Project Type Distribution")
    
    if not filtered_df.empty:
        fig = px.pie(
            filtered_df, 
            names="project_type", 
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

# Cost Correlation Matrix
with col4:
    st.subheader("Cost Correlation Matrix")
    
    if not filtered_df.empty:
        corr_matrix = filtered_df[["labor_total", "material_total", "equipment_total", "total_mat_lab_equip"]].corr()
        z_values = np.round(corr_matrix.values, 2)
        
        fig = ff.create_annotated_heatmap(
            z=z_values,
            x=list(corr_matrix.columns),
            y=list(corr_matrix.index),
            colorscale="Viridis",
            annotation_text=z_values,
            showscale=True
        )
        
        fig.update_layout(
            margin=dict(l=50, r=50, t=30, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

# Distribution of Costs
st.subheader("Distribution of Costs")

if not filtered_df.empty:
    # Create tabs for different visualizations
    tab1, tab2 = st.tabs(["Violin Plot", "Histogram"])
    
    # Melt the DataFrame for plotting
    df_melted = filtered_df.melt(
        value_vars=["labor_total", "material_total", "equipment_total"], 
        var_name="Cost Type", 
        value_name="Total Cost"
    )
    
    with tab1:
        fig = px.violin(
            df_melted, 
            x="Cost Type", 
            y="Total Cost", 
            box=True, 
            color="Cost Type"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = px.histogram(
            df_melted, 
            x="Total Cost", 
            color="Cost Type", 
            nbins=50
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available for the selected filters.")

# Projects Analysis
st.subheader("Projects Analysis")

if not filtered_df.empty:
    tabs = st.tabs(["Cost vs Line Items", "Project Type Analysis"])
    
    with tabs[0]:
        # Group data by file_name
        df_grouped = filtered_df.groupby("file_name").agg(
            labor_total=("labor_total", "sum"),
            material_total=("material_total", "sum"),
            equipment_total=("equipment_total", "sum"),
            file_count=("file_name", "count")
        ).reset_index()
        
        # Melt for plotting
        df_melted = df_grouped.melt(
            id_vars=["file_name", "file_count"], 
            value_vars=["labor_total", "material_total", "equipment_total"], 
            var_name="Cost Category", 
            value_name="Total Cost"
        )
        
        fig = px.scatter(
            df_melted, 
            x="file_count", 
            y="Total Cost", 
            color="Cost Category",
            title="Cost Per Project vs Line Item Count",
            labels={"Total Cost": "Total Cost ($)", "file_count": "Line Item Count"}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        # Group by file_name and include project_type
        df_grouped = filtered_df.groupby("file_name").agg(
            labor_total=("labor_total", "sum"),
            material_total=("material_total", "sum"),
            equipment_total=("equipment_total", "sum"),
            file_count=("project_type", "count"),
            project_type=('project_type', 'unique')
        ).reset_index()
        
        # Melt for plotting
        df_melted = df_grouped.melt(
            id_vars=["file_name", "project_type", "file_count"], 
            value_vars=["labor_total", "material_total", "equipment_total"], 
            var_name="Cost Category", 
            value_name="Total Cost"
        )
        
        # Extract project type from list
        df_melted['project_type'] = df_melted['project_type'].apply(lambda x: x[0])
        
        fig = px.scatter(
            df_melted, 
            x="file_count", 
            y="Total Cost", 
            color="project_type",
            symbol="Cost Category",
            title="Cost Per Project by Project Type",
            labels={"Total Cost": "Total Cost ($)", "file_count": "Line Item Count"}
        )
        
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available for the selected filters.")

# Data Explorer section
st.subheader("Data Explorer")
if st.checkbox("Show Raw Data"):
    st.write(filtered_df)

# Add download button for filtered data
if not filtered_df.empty:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="construction_cost_filtered_data.csv",
        mime="text/csv",
    )

# Footer
st.markdown("---")
st.markdown("Construction Cost Analysis Dashboard | Created with Streamlit and Plotly")